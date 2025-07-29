#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2025.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
import copy
import json
import math
from datetime import datetime

import pandas as pd
from dateutil.tz import tzlocal

from datarobot_mlops.channel.output_channel_queue import OutputChannelQueueAsync
from datarobot_mlops.channel.output_channel_queue import OutputChannelQueueSync
from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.exception import DRApiException
from datarobot_mlops.common.exception import DRCommonException
from datarobot_mlops.common.exception import DRUnsupportedType
from datarobot_mlops.constants import Constants
from datarobot_mlops.event import ExternalNaNPredictionsEvent
from datarobot_mlops.metric import AggregatedStatsContainer
from datarobot_mlops.metric import AggregationHelper
from datarobot_mlops.metric import CustomMetric
from datarobot_mlops.metric import CustomMetricContainer
from datarobot_mlops.metric import DeploymentStats
from datarobot_mlops.metric import DeploymentStatsContainer
from datarobot_mlops.metric import EventContainer
from datarobot_mlops.metric import GeneralStats
from datarobot_mlops.metric import PingMsgContainer
from datarobot_mlops.metric import PredictionsData
from datarobot_mlops.metric import PredictionsDataContainer


class Model:
    DEFAULT_ASYNC_REPORTING = False
    MAX_TS_PREDICTIONS = 10000
    MAX_TS_FEATURE_ROWS = 10000

    REQUEST_PARAMETERS_MAPPING = {
        "forecast_point": "forecastPoint",
        "predictions_start_date": "predictionsStartDate",
        "predictions_end_date": "predictionsEndDate",
        "relax_kia_check": "relaxKnownInAdvanceFeaturesCheck",
        "relax_seen_cross_series_check": "relaxSeenCrossSeriesCheck",
        "relax_insufficient_history_check": "relaxInsufficientHistoryCheck",
    }

    DEFAULT_AGGREGATION_HISTOGRAM_BIN_COUNT = 10
    DEFAULT_AGGREGATION_DISTINCT_CATEGORY_COUNT = 10
    DEFAULT_SEGMENT_VALUE_ATTR_COUNT = 10000

    def __init__(self, feature_types=None):
        self._stats_counter = {}
        self._report_queue = None
        if config.get_config_default(ConfigConstants.ASYNC_REPORTING, self.DEFAULT_ASYNC_REPORTING):
            self._report_queue = OutputChannelQueueAsync()
        else:
            self._report_queue = OutputChannelQueueSync()

        # stats aggregation fields
        self._init_aggregation_params(feature_types)

    def _init_aggregation_params(self, feature_types):
        features_types_filename = config.get_config_default(
            ConfigConstants.FEATURE_TYPES_FILENAME, None
        )
        features_types_json = config.get_config_default(ConfigConstants.FEATURE_TYPES_JSON, None)
        if features_types_json or features_types_filename:
            self._feature_types = self._build_feature_types_from_vars(
                features_types_filename, features_types_json
            )
        else:
            self._feature_types = feature_types

        self._histogram_bin_count = config.get_config_default(
            ConfigConstants.STATS_AGGREGATION_HISTOGRAM_BIN_COUNT,
            self.DEFAULT_AGGREGATION_HISTOGRAM_BIN_COUNT,
        )
        self._distinct_category_count = config.get_config_default(
            ConfigConstants.STATS_AGGREGATION_DISTINCT_CATEGORY_COUNT,
            self.DEFAULT_AGGREGATION_DISTINCT_CATEGORY_COUNT,
        )
        self._segment_value_per_attribute_count = config.get_config_default(
            ConfigConstants.STATS_AGGREGATION_SEGMENT_VALUE_COUNT,
            self.DEFAULT_SEGMENT_VALUE_ATTR_COUNT,
        )
        segment_attributes_str = config.get_config_default(
            ConfigConstants.STATS_AGGREGATION_SEGMENT_ATTRIBUTES, None
        )
        if segment_attributes_str:
            self._segment_attributes = [attr.strip() for attr in segment_attributes_str.split(",")]
        else:
            self._segment_attributes = None
        self._prediction_timestamp_column_name = config.get_config_default(
            ConfigConstants.STATS_AGGREGATION_PREDICTION_TS_COLUMN_NAME, None
        )
        self._prediction_timestamp_column_format = config.get_config_default(
            ConfigConstants.STATS_AGGREGATION_PREDICTION_TS_COLUMN_FORMAT, None
        )

    def shutdown(self, timeout_sec=0):
        self._report_queue.shutdown(timeout_sec=timeout_sec, final_shutdown=False)
        self._report_queue = None

    def _validate_input_association_ids(self, predictions, association_ids):
        self._validate_parameter(predictions, association_ids, "association ids", str)
        if len(set(association_ids)) != len(association_ids):
            raise DRCommonException(
                "All association ids should be unique, "
                "association ids uniquely identify each individual prediction"
            )

    def _validate_input_features_and_predictions(self, feature_data_df, predictions):
        for feature_name, feature_values in feature_data_df.items():
            if len(feature_values) != len(predictions):
                raise DRUnsupportedType(
                    """The number of feature values for feature '{}' ({}) does not match the number
                      of prediction values {}""".format(
                        feature_name, len(feature_values), len(predictions)
                    )
                )

    def _validate_predictions(self, predictions, class_names):
        """
        Returns the list of indexes in the list with invalid prediction values "NaN"

        :param predictions:
        :param class_names:
        :return:
        """
        if not isinstance(predictions, list):
            raise DRUnsupportedType(
                "'predictions' should be a list of probabilities, numbers or strings"
            )

        likely_classification_predictions = False
        likely_regression_predictions = False
        likely_text_generation_predictions = False
        class_names_present = False
        likely_num_classes = 0
        if class_names is not None:
            if not isinstance(class_names, list):
                raise DRUnsupportedType("'class_names' should be a list")
            if len(class_names) < 2:
                raise DRCommonException("'class_names' should contain at least 2 values")
            for class_name in class_names:
                if not isinstance(class_name, str):
                    raise DRUnsupportedType(
                        "Each class name is expected to be a string, but received {}".format(
                            type(class_name)
                        )
                    )
            class_names_present = True
            likely_num_classes = len(class_names)

        first_prediction = predictions[0]
        if isinstance(first_prediction, list):
            likely_classification_predictions = True
            likely_num_classes = len(first_prediction)
        elif isinstance(first_prediction, float) or isinstance(first_prediction, int):
            likely_regression_predictions = True
        elif isinstance(first_prediction, str):
            likely_text_generation_predictions = True
        else:
            raise DRUnsupportedType(
                f"Predictions with type '{str(type(first_prediction))}' not supported"
            )

        nan_prediction_indexes = []
        # Now verify that the remaining list of elements have the same instance / format
        for index, prediction in enumerate(predictions):
            if likely_regression_predictions:
                if not (isinstance(prediction, float) or isinstance(prediction, int)):
                    raise DRUnsupportedType(
                        """Invalid prediction '{}' at index '{}', expecting a prediction value of
                        type int or float""".format(
                            str(prediction), index
                        )
                    )
                if math.isnan(prediction):
                    nan_prediction_indexes.append(index)

            elif likely_classification_predictions:
                if not isinstance(prediction, list):
                    raise DRUnsupportedType(
                        """Invalid prediction '{}' at index '{}', expecting list of prediction
                        probabilities""".format(
                            str(prediction), index
                        )
                    )
                if len(prediction) < 2:
                    raise DRCommonException(
                        """Invalid prediction '{}' at index '{}', expecting list of size at least 2
                        """.format(
                            str(prediction), index
                        )
                    )
                if len(prediction) != likely_num_classes:
                    raise DRCommonException(
                        """Invalid prediction '{}' at index '{}', length of class probabilities in
                        the prediction does not match, expected '{}', got '{}'""".format(
                            str(prediction), index, likely_num_classes, len(prediction)
                        )
                    )
                if class_names_present:
                    if len(prediction) != len(class_names):
                        raise DRUnsupportedType(
                            """Number of prediction probabilities '[{}]'({}) at index {} does not
                             match class_names length {}""".format(
                                str(prediction), len(prediction), index, len(class_names)
                            )
                        )
                for prob in prediction:
                    if not isinstance(prob, float):
                        raise DRCommonException(
                            """Probability value '{}' in prediction '{}' at index '{}' is not
                            a float value""".format(
                                prob, prediction, index
                            )
                        )
                    if prob > 1.0 or prob < 0.0:
                        raise DRCommonException(
                            """Probability value '{}' in prediction '{}' at index '{}' is not
                            between 0 and 1""".format(
                                prob, prediction, index
                            )
                        )
                    if math.isnan(prob):
                        nan_prediction_indexes.append(index)
                        break
            elif likely_text_generation_predictions:
                if not isinstance(prediction, str):
                    raise DRUnsupportedType(
                        """Invalid prediction '{}' at index '{}', expecting a prediction value of
                        type string""".format(
                            str(prediction), index
                        )
                    )

        return nan_prediction_indexes

    def _report_stats(self, deployment_id, model_id, stats_serializer):
        """
        This function is used for reporting metrics and events.
        """
        data_type = stats_serializer.data_type()

        # Keep account of number of records submitted to channel
        self._report_queue.submit(stats_serializer, deployment_id)
        if data_type not in self._stats_counter:
            self._stats_counter[data_type] = 0
        self._stats_counter[data_type] += 1

    def get_stats_counters(self):
        return self._stats_counter

    @staticmethod
    def _get_general_stats(model_id, batch_id=None):
        return GeneralStats(model_id, batch_id=batch_id)

    def report_deployment_stats(
        self,
        deployment_id,
        model_id,
        num_predictions,
        user_error,
        system_error,
        execution_time_ms=None,
        batch_id=None,
    ):
        """
        Report the number of predictions and execution time
        to DataRobot MLOps.

        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :param num_predictions: number of predictions
        :type num_predictions: int
        :param user_error: did the request have a user error
        :type user_error: bool
        :param system_error: did the request have a system error
        :type system_error: bool
        :param execution_time_ms: time in milliseconds
        :type execution_time_ms: float
        """
        deployment_stats = DeploymentStats(
            num_predictions, execution_time_ms, user_error, system_error
        )
        deployment_stats_container = DeploymentStatsContainer(
            self._get_general_stats(model_id, batch_id=batch_id),
            deployment_stats,
        )

        self._report_stats(deployment_id, model_id, deployment_stats_container)

    def report_custom_metric(self, deployment_id, model_id, metric_id, value, timestamp=None):
        """
        Report an arbitrary metric to DataRobot MLOps. The metric_id is used to identify the metric.
        This method is used to report a metric which is tied to a deployment and not a model.

        :param deployment_id: Deployment id to report metric for
        :param model_id: Model id to report metric for. If None, metric is a deployment metric.
        :param metric_id: Metric id to use
        :param value: Numeric value to report
        :param timestamp: Timestamp to report for the metric
        """

        # If value is a single value pack it with timestamp into a list of items
        if not isinstance(metric_id, str):
            raise DRUnsupportedType(
                "Metric id must be of type str - got type ({}) {}".format(
                    type(metric_id), isinstance(metric_id, str)
                )
            )

        if not isinstance(value, (list, int, float)):
            raise DRUnsupportedType(
                "Value for custom metric must be either int or float (or list of int or float)"
            )

        if isinstance(value, list):
            if not all(isinstance(v, (int, float)) for v in value):
                raise DRUnsupportedType("Values for custom metrics should be all numeric")
            value_list = value[:]
            # We make sure timestamp is also a list
            if not isinstance(timestamp, list):
                raise DRUnsupportedType(
                    "When providing a list of values for custom metrics, "
                    + "timestamp must also be a list"
                )
            if len(timestamp) != len(value):
                raise DRCommonException(
                    "Length of timestamp list ({}) != Length of value list ({})".format(
                        len(timestamp), len(value)
                    )
                )
            timestamp_list = [GeneralStats.to_dr_timestamp(ts) for ts in timestamp]
        else:
            value_list = [value]
            # Allowing a None timestamp in the case where value is not a list.
            # The timestamp is generated using now()
            if timestamp is None:
                timestamp = GeneralStats.to_dr_timestamp(datetime.now(tzlocal()))
            elif isinstance(timestamp, (list, dict)):
                raise DRCommonException("Value is a scalar while timestamp is not")
            else:
                timestamp = GeneralStats.to_dr_timestamp(timestamp)
            timestamp_list = [timestamp]

        custom_metric = CustomMetric(metric_id, value_list, timestamp_list)
        metric_container = CustomMetricContainer(self._get_general_stats(model_id), custom_metric)
        self._report_stats(deployment_id, model_id, metric_container)

    def report_predictions_data(
        self,
        deployment_id,
        model_id,
        features_df=None,
        predictions=None,
        association_ids=None,
        class_names=None,
        skip_drift_tracking=False,
        skip_accuracy_tracking=False,
        batch_id=None,
    ):
        """
        Report features and predictions to DataRobot MLOps for tracking and monitoring.

        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe
        :param predictions: List of predictions.  For Regression deployments, this is 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type. For LLM
            deployments it is the list of completions
            Binary Classification: e.g. [[0.2, 0.8], [0.3, 0.7]].
            Regression Predictions: e.g. [1, 2, 4, 3, 2]
            TextGeneration predictions: eg. ["Completion 1", "Completion 2"]
        :type predictions: list

        At least one of `features` or `predictions` must be specified.

        :param association_ids: an optional list of association IDs corresponding to each
            prediction used for accuracy calculations.  Association IDs have to be unique for each
            prediction reported.  Number of `predictions` should be equal to number of
            `association_ids` in the list
        :type association_ids: list
        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list
        :param skip_drift_tracking: Should the DataRobot App skip drift calculation for this raw
            data
        :type skip_drift_tracking: bool
        :param skip_accuracy_tracking: Should the DataRobot App skip accuracy calculation for
            these predictions
        :type skip_accuracy_tracking: bool
        :param batch_id: ID of the batch these statistics belong to
        :type batch_id: str
        """
        nan_prediction_indexes, reporting_data = self._validate_and_copy_feature_predictions(
            features_df, predictions, class_names, association_ids
        )

        if nan_prediction_indexes:
            reporting_data = self._remove_nans(nan_prediction_indexes, reporting_data)

            self._report_external_nan_predictions_event(
                deployment_id, model_id, nan_prediction_indexes
            )

        self._report_metric(
            deployment_id,
            model_id,
            reporting_data["_features_df"],
            reporting_data["_predictions"],
            reporting_data["_association_ids"],
            reporting_data["_class_names"],
            skip_drift_tracking=skip_drift_tracking,
            skip_accuracy_tracking=skip_accuracy_tracking,
            batch_id=batch_id,
        )

    def _validate_and_copy_feature_predictions(
        self,
        features_df=None,
        predictions=None,
        class_names=None,
        association_ids=None,
    ):
        if features_df is None and predictions is None:
            raise DRCommonException("One of `features_df` or `predictions` argument is required")
        nan_prediction_indexes = None
        if predictions is not None:
            nan_prediction_indexes = self._validate_predictions(predictions, class_names)
        if features_df is not None and not isinstance(features_df, pd.DataFrame):
            raise DRUnsupportedType(f"features_df argument has to be of type '{pd.DataFrame}'")
        if predictions and association_ids:
            self._validate_input_association_ids(predictions, association_ids)
        # If dataframe provided we do a deep copy, in case is modified before processing
        if features_df is not None and predictions:
            self._validate_input_features_and_predictions(features_df, predictions)
        # Deep copy the values
        reporting_data = self._deep_copy_reporting_data(
            features_df=features_df,
            predictions=predictions,
            association_ids=association_ids,
            class_names=class_names,
        )

        return nan_prediction_indexes, reporting_data

    def report_aggregated_predictions_data(
        self,
        deployment_id,
        model_id,
        features_df=None,
        predictions=None,
        class_names=None,
        batch_id=None,
    ):
        """
        Report features and predictions aggregated using mlops-stats-aggregator
         to DataRobot MLOps for tracking and monitoring.

        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe
        :param predictions: List of predictions.  For Regression deployments, this is 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type
            Binary Classification: e.g. [[0.2, 0.8], [0.3, 0.7]].
            Regression Predictions: e.g. [1, 2, 4, 3, 2]
        :type predictions: list

        At least one of `features` or `predictions` must be specified.
        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list
        :param batch_id: ID of the batch these statistics belong to
        :type batch_id: str
        """
        if features_df is not None and self._feature_types is None:
            raise DRCommonException("Features type should be provided during MLOPS initialization")

        (nan_prediction_indexes, reporting_data) = self._validate_and_copy_feature_predictions(
            features_df, predictions, class_names
        )
        if nan_prediction_indexes:
            reporting_data = self._remove_nans(nan_prediction_indexes, reporting_data)

            self._report_external_nan_predictions_event(
                deployment_id, model_id, nan_prediction_indexes
            )

        predictions_df = self._convert_predictions_to_df(
            reporting_data["_predictions"], reporting_data["_class_names"]
        )

        # If the prediction timestamp column is not set or is not present in the feature list
        # follow the regular path
        if (
            self._prediction_timestamp_column_name
            and self._prediction_timestamp_column_format
            and self._prediction_timestamp_column_name in reporting_data["_features_df"].columns
        ):
            # Split rows based on timestamps
            self._process_data_for_aggregation_with_prediction_timestamp(
                deployment_id,
                model_id,
                reporting_data["_features_df"],
                predictions_df,
                reporting_data["_class_names"],
                batch_id,
            )
        else:
            # Call method to report aggregated stats directly
            self._aggregate_stats(
                deployment_id,
                model_id,
                feature_data_df=reporting_data["_features_df"],
                predictions_df=predictions_df,
                class_names=class_names,
                batch_id=batch_id,
            )

    def _process_data_for_aggregation_with_prediction_timestamp(
        self,
        deployment_id,
        model_id,
        features_df=None,
        predictions_df=None,
        class_names=None,
        batch_id=None,
    ):
        try:
            from datarobot_mlops.stats_aggregator.type_conversion import convert_date_feature
        except ImportError:
            message = (
                "Large-Scale Monitoring failed; missing package; "
                "need to `pip install {}[aggregator]`".format(Constants.OFFICIAL_NAME)
            )
            raise RuntimeError(message)

        converted_timestamp = convert_date_feature(
            features_df[self._prediction_timestamp_column_name],
            self._prediction_timestamp_column_format,
        )
        # convert timestamp to near-est hour
        converted_timestamp = converted_timestamp.apply(lambda ts: ts - (ts % 3600))
        unique_timestamps = set(converted_timestamp)

        for timestamp in unique_timestamps:
            ts_filter = converted_timestamp == timestamp
            slice_feature_df = features_df[ts_filter] if features_df is not None else None
            slice_predictions_df = predictions_df[ts_filter] if predictions_df is not None else None

            self._aggregate_stats(
                deployment_id,
                model_id,
                feature_data_df=slice_feature_df,
                predictions_df=slice_predictions_df,
                class_names=class_names,
                timestamp=timestamp,
                batch_id=batch_id,
            )

    @staticmethod
    def _convert_predictions_to_df(predictions, class_names):
        if predictions is None:
            return None

        if class_names:
            return pd.DataFrame(predictions, columns=class_names)
        else:
            return pd.DataFrame(predictions)

    def _aggregate_stats(
        self,
        deployment_id,
        model_id,
        feature_data_df=None,
        predictions_df=None,
        class_names=None,
        timestamp=None,
        batch_id=None,
    ):
        try:
            from datarobot_mlops.stats_aggregator import aggregate_stats
        except ImportError:
            message = (
                "Large-Scale Monitoring failed; missing package; "
                "need to `pip install {}[aggregator]`".format(Constants.OFFICIAL_NAME)
            )
            raise RuntimeError(message)

        aggregated_out = aggregate_stats(
            features=feature_data_df,
            feature_types=self._feature_types,
            predictions=predictions_df,
            segment_attributes=self._segment_attributes,
            histogram_bin_count=self._histogram_bin_count,
            distinct_category_count=self._distinct_category_count,
            segment_value_per_attribute_count=self._segment_value_per_attribute_count,
        )

        self._report_aggregated_stats(
            deployment_id, model_id, aggregated_out, class_names, timestamp, batch_id
        )

    def _report_aggregated_stats(
        self, deployment_id, model_id, aggregated_out, class_names, timestamp, batch_id
    ):
        if timestamp is not None:
            timestamp = datetime.fromtimestamp(timestamp)

        aggregated_stats_container = AggregatedStatsContainer(
            general_stats=GeneralStats(
                model_id,
                GeneralStats.to_dr_timestamp(timestamp),
                batch_id=batch_id,
            ),
            aggregated_stats=AggregationHelper.build_aggregated_stats(aggregated_out, class_names),
        )
        self._report_stats(deployment_id, model_id, aggregated_stats_container)

    @staticmethod
    def _get_num_rows(feature_data_df, predictions_df):
        if feature_data_df is not None:
            return len(feature_data_df)
        else:
            return len(predictions_df)

    def report_raw_time_series_predictions_data(
        self,
        deployment_id,
        model_id,
        features_df=None,
        predictions=None,
        association_ids=None,
        class_names=None,
        request_parameters=None,
        forecast_distance=None,
        row_index=None,
        partition=None,
        series_id=None,
        skip_drift_tracking=False,
        skip_accuracy_tracking=False,
    ):
        """
        Report features and predictions to DataRobot MLOps for tracking and monitoring
        of an external time series deployment

        :param series_id: List of series ids indicating the time series each prediction belongs to
        :type series_id: list[str]
        :param partition: List of forecast dates for which these time series predictions are made
        :type partition: list[datetime]
        :param row_index: Indexes of the rows in the input for which these predictions are made
        :type row_index: list[int]
        :param forecast_distance: list of forecast distance value used for each
            corresponding prediction
        :type forecast_distance: list[int]
        :param request_parameters: Request parameters used to make these predictions, either
            forecast point or bulk parameters
        :type request_parameters: dict[str, datetime]
        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe
        :param predictions: List of predictions.  For Regression deployments, this is a 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type
            Regression Predictions: e.g. [1, 2, 4, 3, 2]
            Binary Classification: e.g. [[0.2, 0.8], [0.3, 0.7]].
        :type predictions: list

        At least one of `features` or `predictions` must be specified.

        :param association_ids: an optional list of association IDs corresponding to each
            prediction. Used for accuracy calculations.  Association IDs have to be unique for each
            prediction to report.  The number of `predictions` should be equal to number of
            `association_ids` in the list
        :type association_ids: list
        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :param skip_drift_tracking: Should the DataRobot App skip drift calculation for this raw
            data
        :type skip_drift_tracking: bool
        :param skip_accuracy_tracking: Should the DataRobot App skip accuracy calculation for
            these predictions
        :type skip_accuracy_tracking: bool
        """
        if features_df is None and not predictions:
            raise DRCommonException("One of `features_df` or `predictions` argument is required")

        nan_prediction_indexes = None
        if predictions:
            nan_prediction_indexes = self._validate_predictions(predictions, class_names)
            if len(predictions) - len(nan_prediction_indexes) > self.MAX_TS_PREDICTIONS:
                raise DRCommonException(
                    """MLOps library currently supports posting only {} predictions in
                     a single call""".format(
                        self.MAX_TS_PREDICTIONS
                    )
                )
            # Validate time series prediction report
            self._validate_time_series_prediction_report(
                predictions, forecast_distance, row_index, partition
            )
            series_id = self._validate_series_id(predictions, series_id)
            if association_ids:
                self._validate_input_association_ids(predictions, association_ids)

        if features_df is not None and not isinstance(features_df, pd.DataFrame):
            raise DRUnsupportedType("features_df argument has to be of type '{}'", pd.DataFrame)

        if features_df is not None:
            if features_df.shape[0] > self.MAX_TS_FEATURE_ROWS:
                raise DRCommonException(
                    """MLOps library currently supports posting only {} feature rows in
                     a single call""".format(
                        self.MAX_TS_FEATURE_ROWS
                    )
                )

        # Deep copy the values
        reporting_data = self._deep_copy_reporting_data(
            features_df=features_df,
            predictions=predictions,
            association_ids=association_ids,
            forecast_distance=forecast_distance,
            row_index=row_index,
            partition=partition,
            series_id=series_id,
            class_names=class_names,
            request_parameters=request_parameters,
        )

        if nan_prediction_indexes:
            # Remove NaN predictions and corresponding rows
            reporting_data = self._remove_nans(nan_prediction_indexes, reporting_data)

            self._report_external_nan_predictions_event(
                deployment_id, model_id, nan_prediction_indexes
            )

        self._report_metric(
            deployment_id,
            model_id,
            feature_data=reporting_data["_features_df"],
            predictions=reporting_data["_predictions"],
            association_ids=reporting_data["_association_ids"],
            class_names=reporting_data["_class_names"],
            request_parameters=reporting_data["_request_parameters"],
            forecast_distance=reporting_data["_forecast_distance"],
            row_index=reporting_data["_row_indexes"],
            partition=reporting_data["_partition"],
            series_id=reporting_data["_series_id"],
            skip_drift_tracking=skip_drift_tracking,
            skip_accuracy_tracking=skip_accuracy_tracking,
        )

    def _deep_copy_reporting_data(
        self,
        features_df=None,
        predictions=None,
        association_ids=None,
        forecast_distance=None,
        row_index=None,
        partition=None,
        series_id=None,
        class_names=None,
        request_parameters=None,
    ):
        reporting_data = {
            key: None
            for key in [
                "_features_df",
                "_predictions",
                "_association_ids",
                "_forecast_distance",
                "_row_indexes",
                "_partition",
                "_series_id",
                "_class_names",
                "_request_parameters",
            ]
        }
        # Validate and modify request parameters
        if request_parameters:
            reporting_data["_request_parameters"] = self._update_request_parameters(
                request_parameters
            )
        if features_df is not None:
            reporting_data["_features_df"] = features_df.copy(deep=True)
            # Reseting index is required to drop exact rows for which predictions are NaN
            reporting_data["_features_df"].reset_index(drop=True, inplace=True)
        if predictions is not None:
            reporting_data["_predictions"] = copy.deepcopy(predictions)
        if association_ids is not None:
            reporting_data["_association_ids"] = copy.deepcopy(association_ids)
        if forecast_distance is not None:
            reporting_data["_forecast_distance"] = copy.deepcopy(forecast_distance)
        if row_index is not None:
            reporting_data["_row_indexes"] = copy.deepcopy(row_index)
        if partition is not None:
            reporting_data["_partition"] = copy.deepcopy(partition)
        if series_id is not None:
            reporting_data["_series_id"] = copy.deepcopy(series_id)
        if class_names is not None:
            reporting_data["_class_names"] = copy.deepcopy(class_names)

        return reporting_data

    @staticmethod
    def _remove_nans(nan_prediction_indexes, reporting_data):
        if not nan_prediction_indexes:
            return

        if reporting_data["_features_df"] is not None:
            # In case of Time Series Predictions, where number of feature rows == number of predictions
            # we can eliminate the rows easily
            if reporting_data["_features_df"].shape[0] == len(reporting_data["_predictions"]):
                reporting_data["_features_df"].drop(nan_prediction_indexes, axis=0, inplace=True)

            # In case of Time Series Predictions, where number of feature rows != number of predictions
            # it will be really hard to identify which rows to delete in case of NaN predictions.  So,
            # we will not remove any rows from features_df.  That is ok, because number of feature rows are
            # anyways not equal to the number of predictions.

        # Need to remove invalid indexes in reverse order, or else it will mess up all the indexes
        for invalid_index in sorted(nan_prediction_indexes, reverse=True):
            del reporting_data["_predictions"][invalid_index]
            if reporting_data["_association_ids"]:
                del reporting_data["_association_ids"][invalid_index]
            if reporting_data["_forecast_distance"]:
                del reporting_data["_forecast_distance"][invalid_index]
            if reporting_data["_row_indexes"]:
                del reporting_data["_row_indexes"][invalid_index]
            if reporting_data["_partition"]:
                del reporting_data["_partition"][invalid_index]
            if reporting_data["_series_id"]:
                del reporting_data["_series_id"][invalid_index]

        return reporting_data

    def report_event(self, deployment_id, model_id, event):
        """
        Wrap event in a container and use report_stats() to place in queue.
        """
        # automatically set deployment ID so user's code doesn't need to
        if event.is_entity_a_deployment():
            event.set_entity_id(deployment_id)
        event_container = EventContainer(event)
        self._report_stats(deployment_id, model_id, event_container)

    def send_ping_to_agent(self, message):
        ping_msg_container = PingMsgContainer(GeneralStats(None), message)
        return self._report_stats(None, None, ping_msg_container)

    def _report_metric(
        self,
        deployment_id,
        model_id,
        feature_data=None,
        predictions=None,
        association_ids=None,
        class_names=None,
        request_parameters=None,
        forecast_distance=None,
        row_index=None,
        partition=None,
        series_id=None,
        skip_drift_tracking=False,
        skip_accuracy_tracking=False,
        batch_id=None,
    ):
        predictions_data = PredictionsData(
            feature_data=feature_data,
            predictions=predictions,
            association_ids=association_ids,
            class_names=class_names,
            request_parameters=request_parameters,
            forecast_distance=forecast_distance,
            row_index=row_index,
            partition=partition,
            series_id=series_id,
            skip_drift_tracking=skip_drift_tracking,
            skip_accuracy_tracking=skip_accuracy_tracking,
        )
        predictions_data_container = PredictionsDataContainer(
            self._get_general_stats(model_id, batch_id=batch_id),
            predictions_data,
        )
        self._report_stats(deployment_id, model_id, predictions_data_container)

    def _validate_time_series_prediction_report(
        self, predictions, forecast_distance, row_index, partition
    ):
        self._validate_parameter(predictions, forecast_distance, "forecast distance", int)
        self._validate_parameter(predictions, row_index, "row index", int)
        self._validate_parameter(predictions, partition, "partition", datetime)

    @staticmethod
    def _validate_parameter(predictions, parameter, param_name, expected_type):
        if not parameter:
            raise DRCommonException(
                f"'{parameter}' values are required to report time series predictions"
            )
        if not isinstance(parameter, list):
            raise DRUnsupportedType(f"{param_name} argument has to be of type '{list}'")
        if len(predictions) != len(parameter):
            raise DRCommonException(
                f"Number of predictions and {param_name} values should be the same"
            )
        for param in parameter:
            if not isinstance(param, expected_type):
                raise DRCommonException(
                    "Value {} is of type {}, expected of type {}".format(
                        param, type(param), expected_type
                    )
                )

    def _validate_series_id(self, predictions, series_id):
        if series_id is None:
            return None

        if not isinstance(series_id, list):
            raise DRUnsupportedType("'series_id' argument has to be of type 'list'")

        # If all values in the series are None, then simply convert series id to be None
        if all(_id is None for _id in series_id):
            return None

        self._validate_parameter(predictions, series_id, "series id", str)
        return series_id

    def _update_request_parameters(self, request_parameters):
        allowed_keys = self.REQUEST_PARAMETERS_MAPPING.keys()
        camel_case_values = self.REQUEST_PARAMETERS_MAPPING.values()
        updated_request_parameters = {}
        for key, value in request_parameters.items():
            if key in allowed_keys:
                new_key = self.REQUEST_PARAMETERS_MAPPING[key]
                if isinstance(value, datetime):
                    updated_request_parameters[new_key] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                else:
                    updated_request_parameters[self.REQUEST_PARAMETERS_MAPPING[key]] = value
            elif key in camel_case_values:
                # If the key is already a camel case, just copy it as it is
                if isinstance(value, datetime):
                    updated_request_parameters[key] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                else:
                    updated_request_parameters[key] = value
            # else:
            # Don't copy the keys which are not in requestParametersMapping or its values
        return updated_request_parameters

    def _build_feature_types_from_vars(self, features_types_filename, features_types_json):
        if features_types_filename and features_types_json:
            # if both vars are provided, raise error
            raise DRApiException(
                "Feature types are provided using file and json, only one is supported"
            )

        feature_types = None
        if features_types_filename:
            with open(features_types_filename, "rb") as f:
                feature_types = json.load(f)
        if features_types_json:
            feature_types = json.loads(features_types_json)

        AggregationHelper.validate_feature_types(feature_types)
        return AggregationHelper.convert_dict_to_feature_types(feature_types)

    def _report_external_nan_predictions_event(
        self, deployment_id, model_id, nan_prediction_indexes
    ):
        # Generate ExternalNaNPredictions event
        external_nan_predictions_event = ExternalNaNPredictionsEvent(
            deployment_id, model_id, nan_prediction_indexes
        )

        self.report_event(deployment_id, model_id, external_nan_predictions_event)
