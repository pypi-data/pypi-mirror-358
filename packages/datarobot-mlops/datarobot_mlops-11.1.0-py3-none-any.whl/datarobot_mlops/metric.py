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

import json
import math
import sys
import time
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from math import isnan

import numpy as np
import pandas as pd
from dateutil.tz import tzlocal

from datarobot_mlops.common.enums import DataFormat
from datarobot_mlops.common.enums import DataType
from datarobot_mlops.common.exception import DRApiException
from datarobot_mlops.common.exception import DRUnsupportedType
from datarobot_mlops.common.sanitize import NameSanitizer
from datarobot_mlops.common.stringutil import camelize
from datarobot_mlops.constants import Constants
from datarobot_mlops.event import Event
from datarobot_mlops.json_shim import default_serializer
from datarobot_mlops.json_shim import json_dumps_bytes

"""
Currently there are the following independent types of information:

GeneralStats: model ID, timestamp
DeploymentStats: number of predictions, execution time
PredictionsStats: predictions, class names

These parameters may be combined and reported in different ways and structures:

Reporting deployment stats includes: model ID, timestamp, num predictions, execution time.
Reporting predictions includes: timestamp, predictions and class names.

DeploymentStatsContainer and PredictionStatsContainer are responsible
for implementing to_iterable() method for data structuring.
"""


def estimate_metric_size(metric):
    """
    Estimate the memory usage of object metric
    :param metric:
    :return: size of metric in bytes
    """
    estimate_size = sys.getsizeof(metric)

    if hasattr(metric, "__dict__"):
        estimate_size += sum([sys.getsizeof(x) for x in metric.__dict__.values() if x is not None])
    return estimate_size


class SerializationConstants:
    class GeneralConstants:
        MODEL_ID_FIELD_NAME = "modelId"
        TIMESTAMP_FIELD_NAME = "timestamp"
        BATCH_ID_FIELD_NAME = "batchId"

    class DeploymentStatsConstants:
        NUM_PREDICTIONS_FIELD_NAME = "numPredictions"
        EXECUTION_TIME_FIELD_NAME = "executionTime"
        USER_ERROR_FIELD_NAME = "userError"
        SYSTEM_ERROR_FIELD_NAME = "systemError"

    class CustomMetricStatsConstants:
        BUCKETS_FIELD_NAME = "buckets"
        METRIC_ID_FIELD_NAME = "customMetricId"
        METRIC_VALUE_FIELD_NAME = "value"

    class PredictionsStatsConstants:
        PREDICTIONS_FIELD_NAME = "predictions"
        ASSOCIATION_IDS_FIELD_NAME = "associationIds"
        RESULTS_FIELD_NAME = "results"
        CLASS_NAMES_FIELD_NAME = "classNames"

    class PredictionsDataConstants:
        PREDICTIONS_FIELD_NAME = "predictions"
        ASSOCIATION_IDS_FIELD_NAME = "associationIds"
        FEATURES_FIELD_NAME = "features"
        CLASS_NAMES_FIELD_NAME = "classNames"
        REQUEST_PARAMETERS_FIELD_NAME = "requestParameters"
        FORECAST_DISTANCE_FIELD_NAME = "forecastDistance"
        ROW_INDEX_FIELD_NAME = "rowIndex"
        PARTITION_FIELD_NAME = "partition"
        SERIES_ID_FIELD_NAME = "seriesId"
        SKIP_DRIFT_TRACKING_FIELD_NAME = "skipDriftTracking"
        SKIP_ACCURACY_TRACKING_FIELD_NAME = "skipAccuracyTracking"

    class AggregatedStatsConstants:
        NUMERIC_AGGREGATE_MAP = "numericAggregateMap"
        CATEGORICAL_AGGREGATE_MAP = "categoricalAggregateMap"
        PREDICTION_AGGREGATE_MAP = "predictionAggregateMap"
        SEGMENT_ATTRIBUTES_AGGREGATE_STATS = "segmentAttributesAggregatedStats"
        SEGMENT_ATTRIBUTES_FIELD_NAME = "segments"

    class EventConstants:
        EVENT_TYPE_FIELD_NAME = "eventType"
        ORG_ID_FIELD_NAME = "orgId"
        ENTITY_ID_FIELD_NAME = "deploymentId"  # todo this is changing
        MESSAGE_FIELD_NAME = "message"
        DATA_FIELD_NAME = "data"

    class PingMsgConstants:
        MESSAGE_FIELD_NAME = "message"
        CREATED_TIMESTAMP = "createdTimestamp"


class GeneralStats:
    """
    General statistics.
    """

    def __init__(self, model_id, timestamp=None, batch_id=None):
        self._model_id = model_id
        self._batch_id = batch_id
        if timestamp is None:
            self._timestamp = self.to_dr_timestamp(datetime.now(tzlocal()))
        else:
            self._timestamp = timestamp

    @staticmethod
    def to_dr_timestamp(ts):
        if ts is None:
            return None

        micro_timestamp = ts.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        return micro_timestamp[0:23] + micro_timestamp[26:]

    def get_model_id(self):
        return self._model_id

    def get_timestamp(self):
        return self._timestamp

    def get_batch_id(self):
        return self._batch_id


class DeploymentStats:
    """
    Class to keep data about deployment statistics.
    """

    def __init__(self, num_predictions, execution_time, user_error, system_error):
        self._num_predictions = num_predictions
        self._execution_time = execution_time
        self._user_error = user_error
        self._system_error = system_error

    def get_num_predictions(self):
        return self._num_predictions

    def get_execution_time(self):
        return self._execution_time

    def get_user_error(self):
        return self._user_error

    def get_system_error(self):
        return self._system_error


class CustomMetric:
    """
    Class to keep data about a custom metric.
    """

    def __init__(self, metric_id, values, timestamps):
        self._metric_id = metric_id
        self._values = values
        self._timestamps = timestamps

    def get_nr_rows(self):
        return len(self._values)

    def get_metric_id(self):
        return self._metric_id

    def get_values(self):
        return self._values

    def get_timestamps(self):
        return self._timestamps


class PredictionsStats:
    """
    Class to keep data about predictions statistics.
    """

    def __init__(self, predictions, class_names, association_ids=None):
        self._predictions = predictions
        self._class_names = class_names
        self._association_ids = association_ids

    def get_predictions(self):
        return self._predictions

    def get_class_names(self):
        return self._class_names

    def get_association_ids(self):
        return self._association_ids


class FeatureDataStats:
    """
    Class to keep feature data.
    """

    def __init__(self, feature_data):
        self._feature_data = feature_data

    def get_feature_data(self):
        return self._feature_data


class PredictionsData:
    """
    Class to keep features and predictions data together
    """

    def __init__(
        self,
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
    ):
        self._feature_data = feature_data
        self._has_feature_data = False if feature_data is None else True
        self._has_prediction_data = False if predictions is None else True
        self._predictions = predictions
        self._association_ids = association_ids
        self._class_names = class_names
        self._request_parameters = request_parameters
        self._forecast_distance = forecast_distance
        self._row_index = row_index
        self._partition = partition
        self._series_id = series_id
        self._skip_drift_tracking = skip_drift_tracking
        self._skip_accuracy_tracking = skip_accuracy_tracking

    def get_num_rows(self):
        if self._has_feature_data and self._has_prediction_data:
            # raw time series data can have different number of features and predictions
            return max(len(self._feature_data), len(self._predictions))
        elif self.has_feature_data():
            return len(self._feature_data)
        else:
            return len(self._predictions)

    def get_num_prediction_rows(self):
        if self._has_prediction_data:
            return len(self._predictions)
        else:
            return 0

    def get_num_feature_rows(self):
        if self._has_feature_data:
            return len(self._feature_data)
        else:
            return 0

    def get_predictions(self):
        return self._predictions

    def get_class_names(self):
        return self._class_names

    def get_association_ids(self):
        return self._association_ids

    def has_feature_data(self):
        return self._has_feature_data

    def get_feature_data_df(self):
        return self._feature_data

    def get_request_parameters(self):
        return self._request_parameters

    def get_forecast_distance(self):
        return self._forecast_distance

    def get_row_index(self):
        return self._row_index

    def get_partition(self):
        return self._partition

    def get_series_id(self):
        return self._series_id

    def skip_drift_tracking(self):
        return self._skip_drift_tracking

    def skip_accuracy_tracking(self):
        return self._skip_accuracy_tracking


class AggregatedStats:
    def __init__(
        self,
        numeric_aggregate_map=None,
        categorical_aggregate_map=None,
        prediction_aggregate_map=None,
        segment_attributes_aggregated_stats=None,
        class_names=None,
    ):
        self.numeric_aggregate_map = numeric_aggregate_map
        self.categorical_aggregate_map = categorical_aggregate_map
        self.prediction_aggregate_map = prediction_aggregate_map
        self.segment_attributes_aggregated_stats = segment_attributes_aggregated_stats
        self._class_names = class_names

    def get_numeric_aggregate_map(self):
        return self.numeric_aggregate_map

    def get_categorical_aggregate_maps(self):
        return self.categorical_aggregate_map

    def get_prediction_aggregate_map(self):
        return self.prediction_aggregate_map

    def get_segment_attributes_aggregated_stats(self):
        return self.segment_attributes_aggregated_stats

    def get_class_names(self):
        return self._class_names


class StatsContainer(ABC):
    @abstractmethod
    def to_iterable(self):
        pass

    @abstractmethod
    def get_estimate_size(self):
        """
        Return current stats estimated size in memory
        :return: estimated size of object in bytes
        """

    @abstractmethod
    def data_type(self):
        """
        Get type of the data current metric represents.
        Check @DataType.

        :return: type of the data for current metric.
        :rtype: DataType
        """

    @abstractmethod
    def to_api_payload(self):
        """
        Get the format of the data that can be sent to the
        DataRobot API. This will be a serialized payload.

        :return: type of the data for current metric.
        :rtype: str
        """

    def serialize(self, data_format, api_format=False):
        if data_format == DataFormat.JSON:
            if api_format:
                return self.to_api_payload()
            return self.to_iterable()
        elif data_format == DataFormat.BYTE_ARRAY:
            json_str = json.dumps(self.to_iterable())
            return bytearray(json_str, encoding="utf8")
        else:
            raise NotImplementedError(
                f"Metric serialization does not support data format {data_format}"
            )

    def serialize_iterable(self, data_format, stat_iterable):
        if data_format == DataFormat.JSON:
            return stat_iterable
        elif data_format == DataFormat.BYTE_ARRAY:
            json_str = json.dumps(stat_iterable)
            return bytearray(json_str, encoding="utf8")
        else:
            raise NotImplementedError(
                f"Metric serialization does not support data format {data_format}"
            )


class DeploymentStatsContainer(StatsContainer):
    """
    Deployment stats data formatter.
    """

    def __init__(self, general_stats, deployment_stats):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType(
                "Wrong value type for general_stats. Expected: {}, provided: {}".format(
                    GeneralStats, type(general_stats)
                )
            )
        if not isinstance(deployment_stats, DeploymentStats):
            raise DRUnsupportedType(
                "Wrong value type for deployment_stats. Expected: {}, provided: {}".format(
                    DeploymentStats, type(deployment_stats)
                )
            )

        self._general_stats = general_stats
        self._deployment_stats = deployment_stats
        self._estimate_size = None

    def get_estimate_size(self):
        if self._estimate_size is None:
            self._estimate_size = estimate_metric_size(self._general_stats) + estimate_metric_size(
                self._deployment_stats
            )
        return self._estimate_size

    def data_type(self):
        return DataType.DEPLOYMENT_STATS

    def to_iterable(self):
        ret = dict()
        ret[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = (
            self._general_stats.get_timestamp()
        )
        ret[SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME] = (
            self._general_stats.get_model_id()
        )
        if self._general_stats.get_batch_id():
            ret[SerializationConstants.GeneralConstants.BATCH_ID_FIELD_NAME] = (
                self._general_stats.get_batch_id()
            )
        ret[SerializationConstants.DeploymentStatsConstants.NUM_PREDICTIONS_FIELD_NAME] = (
            self._deployment_stats.get_num_predictions()
        )
        ret[SerializationConstants.DeploymentStatsConstants.EXECUTION_TIME_FIELD_NAME] = (
            self._deployment_stats.get_execution_time()
        )
        ret[SerializationConstants.DeploymentStatsConstants.USER_ERROR_FIELD_NAME] = (
            self._deployment_stats.get_user_error()
        )
        ret[SerializationConstants.DeploymentStatsConstants.SYSTEM_ERROR_FIELD_NAME] = (
            self._deployment_stats.get_system_error()
        )

        return ret

    def to_api_payload(self):
        payload = {"data": [self.to_iterable()]}
        serialized_payload = json_dumps_bytes(payload)
        return serialized_payload


class CustomMetricContainer(StatsContainer):
    """
    Custom Metric data formatter.
    """

    METRIC_ID_FIELD_NAME = SerializationConstants.CustomMetricStatsConstants.METRIC_ID_FIELD_NAME
    METRIC_VALUE_FIELD_NAME = (
        SerializationConstants.CustomMetricStatsConstants.METRIC_VALUE_FIELD_NAME
    )
    TIMESTAMP_FIELD_NAME = SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME
    BUCKETS_FIELD_NAME = SerializationConstants.CustomMetricStatsConstants.BUCKETS_FIELD_NAME

    def __init__(self, general_stats, custom_metric, api_format=False):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType(
                "Wrong value type for general_stats. Expected: {}, provided: {}".format(
                    GeneralStats, type(general_stats)
                )
            )
        if not isinstance(custom_metric, CustomMetric):
            raise DRUnsupportedType(
                "Wrong value type for custom_metric. Expected: {}, provided: {}".format(
                    CustomMetric, type(custom_metric)
                )
            )

        self._general_stats = general_stats
        self._custom_metric = custom_metric
        self._estimate_size = None
        self._api_format = api_format

    def get_estimate_size(self):
        if self._estimate_size is None:
            self._estimate_size = estimate_metric_size(self._general_stats) + estimate_metric_size(
                self._custom_metric
            )
        return self._estimate_size

    def data_type(self):
        return DataType.CUSTOM_METRIC

    def get_num_rows(self):
        return self._custom_metric.get_nr_rows()

    def get_metric_id(self):
        return self._custom_metric.get_metric_id()

    def to_iterable(self):
        """
        This is what the payload looks like.
        Note: the metricId is part of the payload we send over the queue but is not part of the
              payload when sending to DataRobot. This is since the agent is getting the metric ID
              as part of the API endpoint.

        payload = {
            "modelId": "634d4cac98e7e9d429a81e85",
            "metricId": "xxxxxxxx" # this is only in the agent payloads
            "buckets": [
                {"timestamp": "2016-12-13T11:12:13.141516Z", "value": 10.0},
                {"timestamp": "2016-12-13T11:12:14.565122Z", "value": 20.0},
            ],
        }
        """
        ret = dict()
        ret[SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME] = (
            self._general_stats.get_model_id()
        )

        if not self._api_format:
            ret[self.METRIC_ID_FIELD_NAME] = self._custom_metric.get_metric_id()

        buckets = []
        for value, timestamp in zip(
            self._custom_metric.get_values(), self._custom_metric.get_timestamps()
        ):
            buckets.append(
                {self.TIMESTAMP_FIELD_NAME: timestamp, self.METRIC_VALUE_FIELD_NAME: value}
            )
        ret[self.BUCKETS_FIELD_NAME] = buckets
        return ret

    @staticmethod
    def iterable_to_api_payload(payload):
        serialized_payload = json_dumps_bytes(payload)
        return serialized_payload

    def to_api_payload(self):
        self._api_format = True
        payload = self.to_iterable()
        return CustomMetricContainer.iterable_to_api_payload(payload)


class PredictionsDataContainer(StatsContainer):
    """
    Features and Predictions data formatter.
    """

    def __init__(self, general_stats, predictions_data, api_format=False):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType(
                "Wrong value type for general_stats. Expected: {}, provided: {}".format(
                    GeneralStats, type(general_stats)
                )
            )
        if not isinstance(predictions_data, PredictionsData):
            raise DRUnsupportedType(
                "Wrong value type for predictions data. Expected: {}, provided: {}".format(
                    PredictionsData, type(predictions_data)
                )
            )

        self._general_stats = general_stats
        self._predictions_data = predictions_data
        self._num_rows = predictions_data.get_num_rows()
        self._estimate_size = None
        self._api_format = api_format

    def get_estimate_size(self):
        # This is a CPU expensive operation so delay doing it until asked.
        if self._estimate_size is None:
            self._estimate_size = (
                estimate_metric_size(self._num_rows)
                + estimate_metric_size(self._general_stats)
                + estimate_metric_size(self._predictions_data)
            )
        return self._estimate_size

    def get_num_rows(self):
        return self._num_rows

    def get_num_prediction_rows(self):
        return self._predictions_data.get_num_prediction_rows()

    def get_num_feature_rows(self):
        if self._has_feature_data:
            return len(self._feature_data)
        else:
            return 0

    def data_type(self):
        return DataType.PREDICTIONS_DATA

    def to_iterable(self):
        predictions_data_object = dict()
        predictions_data_object[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = (
            self._general_stats.get_timestamp()
        )
        if self._general_stats.get_model_id():
            predictions_data_object[SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME] = (
                self._general_stats.get_model_id()
            )

        if self._general_stats.get_batch_id():
            predictions_data_object[SerializationConstants.GeneralConstants.BATCH_ID_FIELD_NAME] = (
                self._general_stats.get_batch_id()
            )

        # If features are specified, include them
        if self._predictions_data.has_feature_data():
            feature_data = self._feature_dataframe_to_feature_dict(
                self._predictions_data.get_feature_data_df()
            )
            if self._api_format:
                feature_data = PredictionsDataContainer._feature_dict_to_api_list(feature_data)

            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.FEATURES_FIELD_NAME
            ] = feature_data

        # If predictions are specified, include them
        if self._predictions_data.get_predictions():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.PREDICTIONS_FIELD_NAME
            ] = self._predictions_data.get_predictions()

        # If association_ids are specified, then include them
        if self._predictions_data.get_association_ids():
            predictions_data_object[
                SerializationConstants.PredictionsStatsConstants.ASSOCIATION_IDS_FIELD_NAME
            ] = self._predictions_data.get_association_ids()

        if self._predictions_data.get_class_names():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.CLASS_NAMES_FIELD_NAME
            ] = self._predictions_data.get_class_names()

        if self._predictions_data.get_request_parameters():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.REQUEST_PARAMETERS_FIELD_NAME
            ] = self._predictions_data.get_request_parameters()

        if self._predictions_data.get_forecast_distance():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.FORECAST_DISTANCE_FIELD_NAME
            ] = self._predictions_data.get_forecast_distance()

        if self._predictions_data.get_row_index():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.ROW_INDEX_FIELD_NAME
            ] = self._predictions_data.get_row_index()

        if self._predictions_data.get_partition():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.PARTITION_FIELD_NAME
            ] = [
                ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                for ts in self._predictions_data.get_partition()
            ]

        if self._predictions_data.get_series_id():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.SERIES_ID_FIELD_NAME
            ] = self._predictions_data.get_series_id()

        # Default value for skip aggregation is False, include them in payload only if they are True
        if self._predictions_data.skip_drift_tracking():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.SKIP_DRIFT_TRACKING_FIELD_NAME
            ] = self._predictions_data.skip_drift_tracking()

        if self._predictions_data.skip_accuracy_tracking():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.SKIP_ACCURACY_TRACKING_FIELD_NAME
            ] = self._predictions_data.skip_accuracy_tracking()
        return predictions_data_object

    @staticmethod
    def _feature_dict_to_api_list(features_dict):
        # Fix the feature part of the payload to be like what MLOps App expects and not
        # what the spooler record expects
        dr_fmt_feature_list = []
        for feature in features_dict:
            dr_fmt_feature_list.append({"name": feature, "values": features_dict[feature]})

        return dr_fmt_feature_list

    def _feature_dataframe_to_feature_dict(self, feature_dataframe):
        if not isinstance(feature_dataframe, pd.DataFrame):
            raise DRUnsupportedType("feature_data argument has to be of type '{}'", pd.DataFrame)

        # Building feature data structure from dataframe
        feature_data = {}

        headers = list(feature_dataframe.columns)
        try:
            values = feature_dataframe.to_numpy()
        except AttributeError:
            # pandas before 0.24 doesn't have .to_numpy()
            values = feature_dataframe.values

        # TODO: Walking through a whole pandas dataframe is not efficient. Orjson supports ndarray
        # natively.

        # save columns of values into a dictionary:
        # {"feature1": [0.1, 0.2, 0.7], "feature2": ["aa", "bb", "cc"]}.
        for i in range(0, len(headers)):
            vals = values[:, i].tolist()
            supported_type = False
            missing_values = 0
            for j in range(0, len(vals)):
                val = vals[j]
                if val is None:
                    # missing features reported from the Java SDK are NoneType
                    missing_values += 1
                    continue
                if isinstance(val, float):
                    # Missing values of any column type are encoded as float nan in the pandas df.
                    # We need to read another column to determine the type of the column.
                    if isnan(val):
                        missing_values += 1
                        continue
                    supported_type = True
                    break
                if isinstance(val, int):
                    supported_type = True
                    break
                if isinstance(val, str):
                    supported_type = True
                    break
                if isinstance(val, Decimal):
                    # Decimal type cannot be json serialized; convert column to float.
                    # TODO: another approach is to convert with a `default` serializer with the
                    # call to `dumps`
                    for k in range(j, len(vals)):
                        vals[k] = float(vals[k])
                    supported_type = True
                    break
                else:
                    # TODO: once we have a logging mechanism, this should be logged and col skipped
                    raise DRUnsupportedType(
                        f"feature_data field type is not supported '{type(vals[j])}'"
                    )

            # If all values are NaN, then also include the feature
            if missing_values == len(vals):
                supported_type = True

            if supported_type:
                feature_data[headers[i]] = vals

        return feature_data

    @staticmethod
    def _adjust_time_series(iterable_input):
        FORECAST = SerializationConstants.PredictionsDataConstants.FORECAST_DISTANCE_FIELD_NAME
        ROW_INDEX = SerializationConstants.PredictionsDataConstants.ROW_INDEX_FIELD_NAME
        PARTITION_FIELD = SerializationConstants.PredictionsDataConstants.PARTITION_FIELD_NAME
        SERIES_ID = SerializationConstants.PredictionsDataConstants.SERIES_ID_FIELD_NAME

        ts = "timeSeriesPredictionsReport"
        ts_dict = dict()

        if FORECAST in iterable_input:
            fc = iterable_input.pop(FORECAST)
            ts_dict[FORECAST] = fc
        if ROW_INDEX in iterable_input:
            ri = iterable_input.pop(ROW_INDEX)
            ts_dict[ROW_INDEX] = ri
        if PARTITION_FIELD in iterable_input:
            pf = iterable_input.pop(PARTITION_FIELD)
            ts_dict[PARTITION_FIELD] = pf
        if SERIES_ID in iterable_input:
            si = iterable_input.pop(SERIES_ID)
            ts_dict[SERIES_ID] = si

        if len(ts_dict) > 0:
            iterable_input[ts] = ts_dict

        return iterable_input

    @staticmethod
    def _adjust_skip_tracking(data_payload):
        SKIP_DRIFT = SerializationConstants.PredictionsDataConstants.SKIP_DRIFT_TRACKING_FIELD_NAME
        SKIP_ACCURACY = (
            SerializationConstants.PredictionsDataConstants.SKIP_ACCURACY_TRACKING_FIELD_NAME
        )

        data_dict = data_payload["data"][0]
        if SKIP_DRIFT in data_dict:
            sd = data_dict.pop(SKIP_DRIFT)
            data_payload[SKIP_DRIFT] = sd
        if SKIP_ACCURACY in data_dict:
            sa = data_dict.pop(SKIP_ACCURACY)
            data_payload[SKIP_ACCURACY] = sa

        return data_payload

    def to_api_payload(self):

        self._api_format = True
        i = self.to_iterable()
        i = self._adjust_time_series(i)
        payload = {"data": [i]}
        payload = self._adjust_skip_tracking(payload)
        serialized_payload = json_dumps_bytes(payload)
        return serialized_payload

    @staticmethod
    def iterable_to_api_payload(payload):
        payload = PredictionsDataContainer._adjust_time_series(payload)
        feature_data_field = SerializationConstants.PredictionsDataConstants.FEATURES_FIELD_NAME
        feature_data = payload.get(feature_data_field)
        if feature_data is not None:
            api_feature_data = PredictionsDataContainer._feature_dict_to_api_list(feature_data)
            payload[feature_data_field] = api_feature_data
        payload = {"data": [payload]}
        payload = PredictionsDataContainer._adjust_skip_tracking(payload)
        serialized_payload = json_dumps_bytes(payload)
        return serialized_payload


class AggregatedStatsContainer(StatsContainer):
    """
    Aggregated Stats formatter.
    """

    def __init__(self, general_stats, aggregated_stats, api_format=False):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType(
                "Wrong value type for general_stats. Expected: {}, provided: {}".format(
                    GeneralStats, type(general_stats)
                )
            )
        if not isinstance(aggregated_stats, AggregatedStats):
            raise DRUnsupportedType(
                "Wrong value type for predictions data. Expected: {}, provided: {}".format(
                    PredictionsData, type(aggregated_stats)
                )
            )
        self._general_stats = general_stats
        self._aggregated_stats = aggregated_stats
        self._estimate_size = None
        self._api_format = api_format

    def get_estimate_size(self):
        # This is a CPU expensive operation so delay doing it until asked.
        if self._estimate_size is None:
            self._estimate_size = estimate_metric_size(self._general_stats) + estimate_metric_size(
                self._aggregated_stats
            )
        return self._estimate_size

    def to_iterable(self):
        aggregated_stat_object = dict()

        aggregated_stat_object[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = (
            self._general_stats.get_timestamp()
        )

        if self._general_stats.get_model_id():
            aggregated_stat_object[SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME] = (
                self._general_stats.get_model_id()
            )

        if self._general_stats.get_batch_id():
            aggregated_stat_object[SerializationConstants.GeneralConstants.BATCH_ID_FIELD_NAME] = (
                self._general_stats.get_batch_id()
            )

        if self._aggregated_stats.get_class_names():
            aggregated_stat_object[
                SerializationConstants.PredictionsDataConstants.CLASS_NAMES_FIELD_NAME
            ] = self._aggregated_stats.get_class_names()

        if self._api_format:
            aggregated_feature_list = (
                AggregationHelper.convert_aggregated_stats_features_to_dr_format(
                    self._aggregated_stats.get_numeric_aggregate_map(),
                    self._aggregated_stats.get_categorical_aggregate_maps(),
                )
            )
            if len(aggregated_feature_list) > 0:
                aggregated_stat_object[
                    SerializationConstants.PredictionsDataConstants.FEATURES_FIELD_NAME
                ] = aggregated_feature_list

            segment_stat_list = (
                AggregationHelper.convert_aggregated_stats_segment_attr_to_dr_format(
                    self._aggregated_stats.get_segment_attributes_aggregated_stats()
                )
            )
            if len(segment_stat_list) > 0:
                aggregated_stat_object[
                    SerializationConstants.AggregatedStatsConstants.SEGMENT_ATTRIBUTES_FIELD_NAME
                ] = segment_stat_list

            predictions_list = AggregationHelper.convert_aggregated_stats_predictions_to_dr_format(
                self._aggregated_stats.get_prediction_aggregate_map()
            )

            if len(predictions_list) > 0:
                if len(predictions_list) == 1:
                    # regressions predictions should not be a list
                    predictions_list = predictions_list[0]
                aggregated_stat_object[
                    SerializationConstants.PredictionsDataConstants.PREDICTIONS_FIELD_NAME
                ] = predictions_list

        else:
            aggregated_stat_object[
                SerializationConstants.AggregatedStatsConstants.NUMERIC_AGGREGATE_MAP
            ] = self._aggregated_stats.get_numeric_aggregate_map()
            aggregated_stat_object[
                SerializationConstants.AggregatedStatsConstants.CATEGORICAL_AGGREGATE_MAP
            ] = self._aggregated_stats.get_categorical_aggregate_maps()
            aggregated_stat_object[
                SerializationConstants.AggregatedStatsConstants.SEGMENT_ATTRIBUTES_AGGREGATE_STATS
            ] = self._aggregated_stats.get_segment_attributes_aggregated_stats()

            aggregated_stat_object[
                SerializationConstants.AggregatedStatsConstants.PREDICTION_AGGREGATE_MAP
            ] = self._aggregated_stats.get_prediction_aggregate_map()

        return aggregated_stat_object

    def data_type(self):
        return DataType.PREDICTION_STATS

    def to_api_payload(self):
        self._api_format = True
        payload = {"data": [self.to_iterable()]}
        serialized_payload = json_dumps_bytes(payload)
        return serialized_payload


class EventContainer(StatsContainer):
    """
    External event data formatter.
    """

    def __init__(self, event):
        if not isinstance(event, Event):
            raise DRUnsupportedType(
                f"Wrong value type for event. Expected: {Event}, provided: {type(event)}"
            )
        self._event = event
        self._estimate_size = None

    def get_estimate_size(self):
        if self._estimate_size is None:
            self._estimate_size = estimate_metric_size(self._event)
        return self._estimate_size

    def data_type(self):
        return DataType.EVENT

    def to_iterable(self):
        ret = dict()
        ret[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = (
            self._event.get_timestamp()
        )
        ret[SerializationConstants.EventConstants.EVENT_TYPE_FIELD_NAME] = (
            self._event.get_event_type()
        )
        ret[SerializationConstants.EventConstants.MESSAGE_FIELD_NAME] = self._event.get_message()
        ret[SerializationConstants.EventConstants.ORG_ID_FIELD_NAME] = self._event.get_org_id()
        ret[SerializationConstants.EventConstants.ENTITY_ID_FIELD_NAME] = (
            self._event.get_entity_id()
        )
        ret[SerializationConstants.EventConstants.DATA_FIELD_NAME] = self._event.get_data()
        return ret

    def to_api_payload(self):
        payload = self.to_iterable()
        serialized_payload = json_dumps_bytes(payload)
        return serialized_payload


def serialize_predictions_data_container_list(
    predictions_data_container_list, skip_drift_tracking, skip_accuracy_tracking
):
    """
    Create the DataRobot API format payload for PredictionsDataContainers
    :param predictions_data_container_list: list of PredictionsDataContainer
    :param whether to skip drift tracking
    :param whether to skip accuracy tracking
    :return: str
    """
    serialized_container_list = []
    for predictions_data_container in predictions_data_container_list:
        serialized_container_list.append(predictions_data_container.serialize(DataFormat.JSON))

    request = {"data": serialized_container_list}
    request["skipDriftTracking"] = skip_drift_tracking
    request["skipAccuracyTracking"] = skip_accuracy_tracking
    payload = json_dumps_bytes(request, default=default_serializer)
    return payload


class AggregationHelper:
    @staticmethod
    def build_aggregated_stats(aggregated_output, class_names):
        numeric_stats = aggregated_output.get("numeric_stats")
        categorical_stats = aggregated_output.get("categorical_stats")
        prediction_stats = aggregated_output.get("prediction_stats")
        segment_attributes_stats = aggregated_output.get("segment_stats")

        return AggregatedStats(
            numeric_aggregate_map=AggregationHelper.convert_stats_to_dict(numeric_stats),
            categorical_aggregate_map=AggregationHelper.convert_stats_to_dict(categorical_stats),
            prediction_aggregate_map=AggregationHelper.convert_predictions_stats_to_dict(
                prediction_stats, class_names
            ),
            segment_attributes_aggregated_stats=AggregationHelper.convert_segments_attributes_stats_to_dict(
                segment_attributes_stats, class_names
            ),
            class_names=class_names,
        )

    @staticmethod
    def aggregated_stat_to_dict(aggregated_stat):
        from datarobot_mlops.stats_aggregator.histogram import CentroidHistogram

        return_dict = dict()
        for k1, v1 in aggregated_stat._asdict().items():
            if isinstance(v1, np.int64):
                return_dict[camelize(k1)] = int(v1)
            elif isinstance(v1, np.floating):
                return_dict[camelize(k1)] = float(v1)
            elif isinstance(v1, CentroidHistogram):
                # convert histogram to spooler format
                return_dict[camelize(k1)] = {
                    "maxLength": v1.max_length,
                    "bucketList": [
                        {"centroid": float(b.centroid), "count": int(b.count)} for b in v1.buckets
                    ],
                }
            else:
                return_dict[camelize(k1)] = v1

        return return_dict

    @staticmethod
    def convert_stats_to_dict(aggregated_stats):
        return {
            k: AggregationHelper.aggregated_stat_to_dict(v) for k, v in aggregated_stats.items()
        }

    @staticmethod
    def convert_predictions_stats_to_dict(prediction_stats, class_names):
        return_dict = {}
        if class_names is None:
            class_names = ["0"]  # Regression

        for class_name, prediction_stat in zip(class_names, prediction_stats):
            return_dict[class_name] = AggregationHelper.aggregated_stat_to_dict(prediction_stat)
        return return_dict

    @staticmethod
    def convert_segments_attributes_stats_to_dict(segment_attributes_stats, class_names):
        agg_cons = SerializationConstants.AggregatedStatsConstants
        return_dict = defaultdict(dict)
        for attribute_name, values in segment_attributes_stats.items():
            for value_name, agg_stats in values.items():
                return_dict[attribute_name][value_name] = {
                    agg_cons.NUMERIC_AGGREGATE_MAP: AggregationHelper.convert_stats_to_dict(
                        agg_stats.get("numeric_stats")
                    ),
                    agg_cons.CATEGORICAL_AGGREGATE_MAP: AggregationHelper.convert_stats_to_dict(
                        agg_stats.get("categorical_stats")
                    ),
                    agg_cons.PREDICTION_AGGREGATE_MAP: AggregationHelper.convert_predictions_stats_to_dict(
                        agg_stats.get("prediction_stats"), class_names
                    ),
                }
        return {"segmentStatsMap": dict(return_dict)}

    # methods to convert dict to DR controller format

    @staticmethod
    def dict_to_histogram(histogram):
        if not histogram or "bucketList" not in histogram:
            return None

        centroids, counts = list(), list()
        for bucket in histogram["bucketList"]:
            centroids.append(bucket["centroid"])
            counts.append(bucket["count"])

        return {"centroids": centroids, "counts": counts}

    @staticmethod
    def convert_stat_format(stat):
        stat.pop("missingCount")
        stat["histogram"] = AggregationHelper.dict_to_histogram(stat["histogram"])
        return stat

    @staticmethod
    def convert_to_numeric_stat(feature_name, stat):
        missing_count = stat.pop("missingCount", 0)
        stat["histogram"] = AggregationHelper.dict_to_histogram(stat["histogram"])
        return {
            "name": feature_name,
            "stats": {
                "numericStats": stat,
                "missingCount": missing_count,
            },
        }

    @staticmethod
    def convert_to_category_stat(feature_name, stat):
        categories, counts = list(), list()
        for category, count in stat["categoryCounts"].items():
            categories.append(category)
            counts.append(count)

        return {
            "name": feature_name,
            "stats": {
                "count": stat["count"],
                "missingCount": stat["missingCount"],
                "categories": {
                    "values": categories,
                    "counts": counts,
                },
            },
        }

    @staticmethod
    def convert_aggregated_stats_features_to_dr_format(numeric_stat=None, category_stat=None):
        feature_list = list()
        if numeric_stat:
            for feature_name, stat in numeric_stat.items():
                feature_list.append(AggregationHelper.convert_to_numeric_stat(feature_name, stat))

        if category_stat:
            for feature_name, stat in category_stat.items():
                feature_list.append(AggregationHelper.convert_to_category_stat(feature_name, stat))

        return feature_list

    @staticmethod
    def convert_aggregated_stats_predictions_to_dr_format(prediction_stats=None):
        """
        1. Removes the "missingCount" field
        2. Changes the format of the histogram data
        3. Returns a list of histogram data, one per class

        :param prediction_stats: input predictions
        :return: prediction histogram data in DataRobot API format

        for regressions, input will look like this:
        {'0':
          {'count': 10,
           'missingCount': 0,
           'min': 7.0,
           'max': 7.0,
           'sum': 70.0,
           'sumOfSquares': 490.0,
           'histogram': {
             'maxLength': 10,
             'bucketList': [
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1},
               {'centroid': 7.0, 'count': 1}]}}}

        for regression, output will look like this:
        [
          {
            'count': 10,
            'min': 7.0,
            'max': 7.0,
            'sum': 70.0,
            'sumOfSquares': 490.0,
            'histogram': {
              'centroids': [7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0],
              'counts': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
          }
        ]
        """
        prediction_list = list()
        if prediction_stats:
            for _, stat in prediction_stats.items():
                prediction_list.append(AggregationHelper.convert_stat_format(stat))
        return prediction_list

    @staticmethod
    def convert_aggregated_stats_segment_attr_to_dr_format(segment_attributes_stats=None):
        if (not segment_attributes_stats) or ("segmentStatsMap" not in segment_attributes_stats):
            return None

        segment_attributes_stats_map = segment_attributes_stats["segmentStatsMap"]
        segment_list = list()
        for attribute_name, values in segment_attributes_stats_map.items():
            segment_attr = list()
            for value_name, stats in values.items():
                segment_attr.append(
                    {
                        "value": value_name,
                        "features": AggregationHelper.convert_aggregated_stats_features_to_dr_format(
                            stats.get(
                                SerializationConstants.AggregatedStatsConstants.NUMERIC_AGGREGATE_MAP
                            ),
                            stats.get(
                                SerializationConstants.AggregatedStatsConstants.CATEGORICAL_AGGREGATE_MAP
                            ),
                        ),
                        "predictions": AggregationHelper.convert_aggregated_stats_predictions_to_dr_format(
                            stats.get(
                                SerializationConstants.AggregatedStatsConstants.PREDICTION_AGGREGATE_MAP
                            )
                        ),
                    }
                )
            segment_list.append({"name": attribute_name, "data": segment_attr})
        return segment_list

    @staticmethod
    def validate_feature_types(feature_types):
        try:
            from datarobot_mlops.stats_aggregator.types import FeatureDescriptor
        except ImportError:
            message = (
                "Large-Scale Monitoring failed; missing package; "
                "need to `pip install {}[aggregator]`".format(Constants.OFFICIAL_NAME)
            )
            raise RuntimeError(message)

        if not isinstance(feature_types, list):
            raise DRApiException("feature_types needs to be a list.")

        if len(feature_types) == 0:
            raise DRApiException("feature_types is empty.")

        for feature_desc in feature_types:
            if isinstance(feature_desc, FeatureDescriptor):
                continue
            elif isinstance(feature_desc, dict):
                if "name" not in feature_desc:
                    raise DRApiException("feature_types does not contains field[name].")

                if "feature_type" not in feature_desc:
                    raise DRApiException("feature_types does not contains field[feature_type].")
            else:
                raise DRApiException("feature_types items should be a FeatureDescriptor or dict.")

    @staticmethod
    def convert_feature_format(feature):
        # FeatureType is defined in mlops-stats-aggregator library and are the types
        # currently supported, this mostly correspond to EdaTypeEnum in DR side.
        # Note: types not cover here (percentage, length, currency) are mapped to numeric after
        # formatting.
        from datarobot_mlops.stats_aggregator.types import FeatureType

        feature_type = feature.get("featureType")

        if feature_type == "Categorical":
            feature_type = FeatureType.CATEGORY
        elif feature_type == "Binary":
            feature_type = FeatureType.BOOLEAN
        elif feature_type == "Numeric":
            feature_type = FeatureType.NUMERIC
        elif feature_type == "Text":
            feature_type = FeatureType.TEXT_WORDS
        elif feature_type == "Date":
            feature_type = FeatureType.DATE

        return {
            "name": feature.get("name"),
            "feature_type": feature_type,
            "format": feature.get("dateFormat"),
        }

    @staticmethod
    def convert_dict_to_feature_types(feature_types):
        if feature_types is None:
            return None

        from datarobot_mlops.stats_aggregator.types import FeatureDescriptor

        feature_names = [
            feature.name if isinstance(feature, FeatureDescriptor) else feature.get("name")
            for feature in feature_types
        ]
        sanitizer = NameSanitizer(feature_names)

        result = []
        for feature in feature_types:
            feature_descriptor = None
            if isinstance(feature, FeatureDescriptor):
                sanitized_name = sanitizer.get(feature.name)
                feature_descriptor = FeatureDescriptor(
                    sanitized_name, feature.feature_type, feature.format
                )
            elif isinstance(feature, dict):
                sanitized_name = sanitizer.get(feature.get("name"))
                feature_descriptor = FeatureDescriptor(
                    sanitized_name, feature.get("feature_type"), feature.get("format")
                )

            result.append(feature_descriptor)

        return result


class PingMsgContainer(StatsContainer):
    def __init__(self, general_stats, ping_msg):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType(
                "Wrong value type for general_stats. Expected: {}, provided: {}".format(
                    GeneralStats, type(general_stats)
                )
            )
        if not isinstance(ping_msg, str):
            raise DRUnsupportedType(
                "Wrong value type for ping msg. Expected: {}, provided: {}".format(
                    str, type(ping_msg)
                )
            )
        self._general_stats = general_stats
        self.ping_msg = ping_msg
        self.created_timestamp = math.floor((time.time() + time.timezone) * 1000)

    def to_iterable(self):
        ret = dict()
        ret[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = (
            self._general_stats.get_timestamp()
        )
        ret[SerializationConstants.PingMsgConstants.MESSAGE_FIELD_NAME] = self.ping_msg
        ret[SerializationConstants.PingMsgConstants.CREATED_TIMESTAMP] = self.created_timestamp
        return ret

    def to_api_payload(self):
        return {}

    def get_estimate_size(self):
        return 0

    def data_type(self):
        return DataType.PING_MSG
