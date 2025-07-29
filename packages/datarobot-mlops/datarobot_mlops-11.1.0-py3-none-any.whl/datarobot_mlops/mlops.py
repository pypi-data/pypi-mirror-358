#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2024.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
"""
mlops library for reporting statistics.

MLOps library can be used to report ML metrics to DataRobot MLOps for centralized monitoring.
"""

import atexit
import json
import logging
import os
from enum import Enum

from datarobot_mlops.agent import Agent
from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRAlreadyInitialized
from datarobot_mlops.common.exception import DRApiException
from datarobot_mlops.common.sampling import get_sampling_pct
from datarobot_mlops.common.sampling import sample_dataframe
from datarobot_mlops.common.sampling import validate_sampling_percentage
from datarobot_mlops.common.sanitize import NameSanitizer
from datarobot_mlops.constants import Constants
from datarobot_mlops.metric import AggregationHelper
from datarobot_mlops.model import Model

logger = logging.getLogger(__name__)


class MLOpsLibMode(Enum):
    EMBEDED_AGENT_MODE = 1
    DAEMON_AGENT_MODE = 2


class MLOps:

    # ------------------------------------------------------
    #  INTERNAL FUNCTIONS
    # ------------------------------------------------------

    def __init__(self):
        self._initialized = False
        self._model = None
        self._libmode = MLOpsLibMode.DAEMON_AGENT_MODE
        self._agent = None
        self._default_deployment_id = None
        self._default_model_id = None
        self._feature_types = None
        self._auto_sampling_pct = None
        self._association_id_column_name = None

    def _cleanup(self):
        if self._agent is not None:
            self._agent.cleanup()

    def _validate(self):
        if not self._initialized:
            raise DRApiException(
                "MLOps library is not initialized." "Make sure to call `init()` function."
            )

    @staticmethod
    def _normalize_feature_names(features_df):
        if features_df is not None:
            sanitizer = NameSanitizer(features_df.columns.to_list())
            features_df.rename(columns=sanitizer.get_mapping(), inplace=True)

    @staticmethod
    def _validate_input_positive_num(num, field_name):
        if num <= 0:
            raise DRApiException(field_name + " needs to be a positive number.")

    @staticmethod
    def _validate_input_string(string, field_name):
        if not string:
            raise DRApiException(field_name + " is empty.")

    def _get_id(self, id_param, config_constant):
        _id = id_param

        if _id is None:
            if config_constant == ConfigConstants.DEPLOYMENT_ID:
                _id = self._default_deployment_id
            elif config_constant == ConfigConstants.MODEL_ID:
                _id = self._default_model_id
            if _id is None:
                raise DRApiException(
                    "Config key '{}' not found. Export as an environment variable "
                    "or set programmatically.".format(config_constant.name)
                )
        return _id

    # ------------------------------------------------------
    #  STARTUP, SHUTDOWN, ETC.
    # ------------------------------------------------------

    @staticmethod
    def get_version():
        """
        Return the version
        """
        return Constants.MLOPS_VERSION

    def init(self):
        """
        Finalize the initialization of the MLOps instance. Reporting can be done only
        after calling this method.

        :raises: DRAlreadyInitialized if MLOps library is already initialized
        :returns: the MLOps instance
        :rtype: MLOps
        """
        if self._initialized:
            raise DRAlreadyInitialized("MLOps library already initialized.")

        if self._libmode is MLOpsLibMode.EMBEDED_AGENT_MODE and self._agent is not None:
            self._agent.validate_and_init_config()
            self._agent.start()
            self._agent.connect_to_gateway()

        self._default_deployment_id = config.get_config_default(ConfigConstants.DEPLOYMENT_ID, None)
        self._default_model_id = config.get_config_default(ConfigConstants.MODEL_ID, None)

        self._model = Model(feature_types=self._feature_types)
        self._initialized = True
        return self

    def shutdown(self, timeout_sec=0):
        """
        Safe MLOps shutdown.
        Ensures that all metrics are processed and forwarded to the configured output.
        """
        if self._libmode == MLOpsLibMode.EMBEDED_AGENT_MODE and self._agent is not None:
            submitted_stats = self._model.get_stats_counters()
            self._agent.wait_for_stats_sent_to_mmm(submitted_stats, timeout_sec)
            self._agent.stop()
            self._agent = None

        config.clear_config()
        self._model.shutdown(timeout_sec=timeout_sec)
        del self._model
        self._initialized = False

        return

    def agent(
        self,
        mlops_service_url=None,
        mlops_api_token=None,
        agent_jar_path=None,
        path_prefix=None,
        verify_ssl=True,
    ):
        """
        Setup agent in an "embedded" mode. The MLOps SDK will transparently manage to configure
        and run the agent.
        When this mode is enabled, the agent service should not be started separately.

        In versions prior to 9.0, the agent JAR is included with the mlops-py WHL file.
        After 9.0, the agent JAR must be installed separately either via the agent TAR file or
        from a public maven repository.

        :param mlops_service_url: URL of the DataRobot MLOps service
        :type mlops_service_url: str
        :param mlops_api_token: DataRobot MLOps API token
        :type mlops_api_token: str
        :param agent_jar_path: path to the agent JAR file
        :type agent_jar_path: str, optional
        :param path_prefix: Path prefix used to store spool / logs of agent. By default,
            it will be a temporary directory.
        :type path_prefix: str, optional
        :param verify_ssl: Whether to verify the SSL certificate. By default, this is `True`.
        :type verify_ssl: bool, optional
        :returns: the MLOps instance
        :rtype: MLOps
        """

        # Note that these take the parameter over the environment variable, which is the
        # opposite of what is used in the rest of the system.
        if agent_jar_path is None:
            agent_jar_path = config.get_config_default(
                ConfigConstants.MLOPS_MONITORING_AGENT_JAR_PATH, None
            )
        if mlops_service_url is None:
            mlops_service_url = config.get_config_default(ConfigConstants.MLOPS_SERVICE_URL, None)
        if mlops_api_token is None:
            mlops_api_token = config.get_config_default(ConfigConstants.MLOPS_API_TOKEN, None)

        verify_ssl_string = config.get_config_default(
            ConfigConstants.MLOPS_VERIFY_SSL, str(verify_ssl)
        )
        final_verify_ssl = verify_ssl_string.lower() == "true"

        self._agent = Agent(
            mlops_service_url, mlops_api_token, agent_jar_path, path_prefix, final_verify_ssl
        )
        self._libmode = MLOpsLibMode.EMBEDED_AGENT_MODE

        # register call back for cleanup
        atexit.register(self._cleanup)

        return self

    # ------------------------------------------------------
    #  GENERAL CONFIGURATION
    # ------------------------------------------------------

    def set_deployment_id(self, deployment_id):
        """
        Set the default deployment ID of the deployment for which the reporting will be targeted.

        :param deployment_id: the unique deployment ID
        :type deployment_id: str
        :returns: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(deployment_id, "deployment_id")
        config.set_config(ConfigConstants.DEPLOYMENT_ID, deployment_id)
        return self

    def set_model_id(self, model_id):
        """
        Set the default model ID for which the reporting information is related.

        :param model_id: a unique model ID that identifies the given model
        :type model_id: str
        :returns: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(model_id, "model_id")
        config.set_config(ConfigConstants.MODEL_ID, model_id)
        return self

    def set_async_reporting(self, async_reporting=True):
        """
        Set mode of reporting metrics. Asynchronous mode buffers the reported metrics in memory
        while a background process sends them to the spooler.

        :param async_reporting: whether to report asynchronously
        :type async_reporting: bool
        :returns: the MLOps instance
        :rtype: MLOps
        """
        config.set_config(ConfigConstants.ASYNC_REPORTING, async_reporting)
        return self

    def set_association_id_column_name(self, association_id_column_name):
        """
        Set the default association ID column name for which the reporting will be targeted.
        :param association_id_column_name: Name of the association id column
        :type association_id_column_name: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(association_id_column_name, "association_id_column_name")
        self._association_id_column_name = association_id_column_name
        return self

    # ------------------------------------------------------
    #  SPOOLER CONFIGURATION
    # ------------------------------------------------------

    def set_no_spooler(self):
        """
        Set no spooler. This disables MLOps reporting.

        :returns: the MLOps instance
        :rtype: MLOps
        """
        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.NONE.name)
        return self

    def set_stdout_spooler(self):
        """
        Use STDOUT in place of a spooler. Any reported metrics will go to stdout instead of
        being routed to the agent.

        :returns: the MLOps instance
        :rtype: MLOps
        """
        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.STDOUT.name)
        return self

    def set_filesystem_spooler(self, directory):
        """
        Set the spooler type to FILESYSTEM and set its output to the directory specified.

        :param directory: a local filesystem directory path
        :type directory: str
        :returns: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(directory, "directory")
        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.FILESYSTEM.name)
        config.set_config(ConfigConstants.FILESYSTEM_DIRECTORY, directory)
        return self

    def set_pubsub_spooler(self, project_id, topic_name):
        """
        Set the spooler type to PUBSUB. Note that PubSub only supports Python3.

        :param project_id: GCP PubSub project id. This should be the full project id path.
        :type project_id: str
        :param topic_name: GCP PubSub topic name. This should be the name of the topic within the
          project, not the full topic path that includes the project id.
        :type topic_name: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(project_id, "project_id")
        self._validate_input_string(topic_name, "topic_name")
        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.PUBSUB.name)
        config.set_config(ConfigConstants.PUBSUB_PROJECT_ID, project_id)
        config.set_config(ConfigConstants.PUBSUB_TOPIC_NAME, topic_name)
        return self

    def set_sqs_spooler(self, queue):
        """
        Set the spooler type to SQS.

        :param queue: AWS SQS queue name or queue URL. If the parameter begins with "http", it is
          assumed to be the queue URL. Otherwise, it is assumed to be the queue name.
        :type queue: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(queue, "queue_url")
        if queue.startswith("http"):
            config.set_config(ConfigConstants.SQS_QUEUE_URL, queue)
        else:
            config.set_config(ConfigConstants.SQS_QUEUE_NAME, queue)

        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.SQS.name)
        return self

    def set_rabbitmq_spooler(
        self,
        queue_url,
        queue_name,
        ca_certificate_path=None,
        certificate_path=None,
        keyfile_path=None,
        tls_version=None,
    ):
        """
        Set the spooler type to RABBITMQ.

        :param queue_url: RabbitMQ queue URL
        :type queue_url: str
        :param queue_name: RabbitMQ queue name
        :type queue_name: str
        :param ca_certificate_path: the path for CA certificate (only used for mTLS connections)
        :type ca_certificate_path: str, optional
        :param certificate_path: the path for client certificate (only used for mTLS connections)
        :type certificate_path: str, optional
        :param keyfile_path: the client key file path (only used for mTLS connections)
        :type keyfile_path: str, optional
        :param tls_version: the tls client version (only used for mTLS connections)
        :type tls_version: str, optional
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(queue_url, "queue_url")
        self._validate_input_string(queue_name, "queue_name")
        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.RABBITMQ.name)
        config.set_config(ConfigConstants.RABBITMQ_QUEUE_URL, queue_url)
        config.set_config(ConfigConstants.RABBITMQ_QUEUE_NAME, queue_name)
        if ca_certificate_path:
            config.set_config(ConfigConstants.RABBITMQ_SSL_CA_CERTIFICATE_PATH, ca_certificate_path)
        if certificate_path:
            config.set_config(ConfigConstants.RABBITMQ_SSL_CERTIFICATE_PATH, certificate_path)
        if keyfile_path:
            config.set_config(ConfigConstants.RABBITMQ_SSL_KEYFILE_PATH, keyfile_path)
        if tls_version:
            config.set_config(ConfigConstants.RABBITMQ_SSL_TLS_VERSION, tls_version)

        return self

    def set_kafka_spooler(self, topic_name, bootstrap_servers=None):
        """
        Set the spooler type to KAFKA.

        :param topic_name: Kafka topic name
        :type topic_name: str
        :param bootstrap_servers: the 'host[:port]' string (or list of 'host[:port]' strings)
            that the consumer should contact to bootstrap initial cluster metadata.
        :type bootstrap_servers: str, optional
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(topic_name, "topic_name")
        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.KAFKA.name)
        config.set_config(ConfigConstants.KAFKA_TOPIC_NAME, topic_name)

        if bootstrap_servers:
            config.set_config(ConfigConstants.KAFKA_BOOTSTRAP_SERVERS, bootstrap_servers)

        return self

    def set_api_spooler(self, mlops_service_url=None, mlops_api_token=None):
        """
        Send messages directly to the DataRobot API instead of a spooler.
        There is no agent needed in this case.

        :param mlops_service_url: URL of the DataRobot MLOps service
        :type mlops_service_url: str, optional
        :param mlops_api_token: DataRobot MLOps API token
        :type mlops_api_token: str, optional
        :returns: the MLOps instance
        :rtype: MLOps
        """
        config.set_config(ConfigConstants.SPOOLER_TYPE, SpoolerType.API.name)
        if mlops_service_url:
            config.set_config(ConfigConstants.MLOPS_SERVICE_URL, mlops_service_url)
        if mlops_api_token:
            config.set_config(ConfigConstants.MLOPS_API_TOKEN, mlops_api_token)
        return self

    def set_channel_config(self, channel_config, record_delimiter=";", key_value_separator="="):
        """
        Set the channel configuration using a list of settings in a semicolon separated string,
        for example, "spooler_type=filesystem;directory=/this/directory"

        :param channel_config: key=value params separated by semicolon
        :param record_delimiter: override default record delimiter (by default ';')
        :param key_value_separator: override default key value separator (by default '=')
        :type channel_config: str
        :type record_delimiter: str,optional
        :type key_value_separator: str,optional
        :return: the MLOps instance
        :rtype: MLOps
        """
        config.set_channel_config_from_str(
            channel_config,
            record_delimiter=record_delimiter,
            key_value_separator=key_value_separator,
        )
        return self

    # ------------------------------------------------------
    #  PREDICTION REPORTING CONFIGURATION
    # ------------------------------------------------------

    def set_feature_data_rows_in_one_message(self, rows):
        """
        Advanced. Set how many feature data rows will be in one message.
        For spoolers which have a message size limit, data reported by the
        `report_predictions_data` call will
        be split into messages with a maximum of this many rows.

        :param rows: how many feature data rows will be in one message
        :type rows: int
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_positive_num(rows, "feature_data_rows_in_one_message")
        config.set_config(ConfigConstants.FEATURE_DATA_ROWS_IN_ONE_MESSAGE, rows)
        return self

    def set_feature_types(self, feature_types):
        """
        Set feature types for aggregation purposes.
        This must be set before calling `report_aggregated_predictions_data()`.

        :param feature_types: list of dict that contains name, type and format for each feature.
        :type feature_types: list of dict
        :return: the MLOps instance
        :rtype: MLOps

        Example input:

        .. code-block:: json

            [
              {
                "name": "f1",
                "feature_type": "numeric"
              },
              {
                "name": "f2_date",
                "feature_type": "date",
                "format": "MM-dd-yy"
              }
            ]

        """
        if self._feature_types is not None:
            raise DRApiException("feature types is already set")
        if self._initialized:
            raise DRApiException(
                "MLOps is already initialized, default features types cannot be modified"
            )
        AggregationHelper.validate_feature_types(feature_types)
        self._feature_types = AggregationHelper.convert_dict_to_feature_types(feature_types)
        return self

    def set_feature_types_filename(self, feature_type_filename):
        """
        See `set_feature_types()`.
        This function allows you to specify the feature type information in
        a file. The contents should be in json format.

        :param feature_type_filename: file path
        :type feature_type_filename: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        if self._feature_types is not None:
            raise DRApiException("feature types is already set")
        if self._initialized:
            raise DRApiException(
                "MLOps is already initialized, default features types cannot be modified"
            )

        self._validate_input_string(feature_type_filename, "features_type_filename")
        with open(feature_type_filename, "rb") as f:
            feature_types = json.load(f)
            AggregationHelper.validate_feature_types(feature_types)
            self._feature_types = AggregationHelper.convert_dict_to_feature_types(feature_types)
        return self

    def set_feature_types_json(self, feature_type_json):
        """
        See `set_feature_types()`.
        This function allows you to specify the feature type information as a json string.

        :param feature_type_json: json of feature types
        :type feature_type_json: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        if self._feature_types is not None:
            raise DRApiException("feature types is already set")
        if self._initialized:
            raise DRApiException(
                "MLOps is already initialized, default features types cannot be modified"
            )

        self._validate_input_string(feature_type_json, "feature_type_json")
        feature_types = json.loads(feature_type_json)
        AggregationHelper.validate_feature_types(feature_types)
        self._feature_types = AggregationHelper.convert_dict_to_feature_types(feature_types)
        return self

    def set_segment_attributes(self, segment_attributes_column):
        """
        Specify the segment_attributes when using aggregation functions.
        This must be set before calling `report_aggregated_predictions_data()`
        when monitoring with segmented attributes.

        :param segment_attributes_column: column name that contains the segmented attributes
        :type segment_attributes_column: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(segment_attributes_column, "segment_attributes")
        config.set_config(
            ConfigConstants.STATS_AGGREGATION_SEGMENT_ATTRIBUTES, segment_attributes_column
        )
        return self

    def set_prediction_timestamp_column(
        self, prediction_timestamp_column_name, prediction_timestamp_column_format
    ):
        """
        When monitoring historical predictions,
        this allows you to specify which column of the "feature" dataframe contains the
        prediction timestamp.
        This must be set before calling `report_aggregated_predictions_data()` if that
        data will include the prediction timestamp.

        :param prediction_timestamp_column_name: name of the timestamp column
        :type prediction_timestamp_column_name: str
        :param prediction_timestamp_column_format: format of the timestamp, e.g., "%Y%M%D"
        :type prediction_timestamp_column_format: str
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_string(
            prediction_timestamp_column_name, "prediction_timestamp_column_name"
        )
        self._validate_input_string(
            prediction_timestamp_column_format, "prediction_timestamp_column_format"
        )
        config.set_config(
            ConfigConstants.STATS_AGGREGATION_PREDICTION_TS_COLUMN_NAME,
            prediction_timestamp_column_name,
        )
        config.set_config(
            ConfigConstants.STATS_AGGREGATION_PREDICTION_TS_COLUMN_FORMAT,
            prediction_timestamp_column_format,
        )
        return self

    def set_auto_sampling_percentage(self, auto_sampling_pct):
        """
        Set the percentage of data to be sampled from the input dataset to report as raw data for
        the challenger analysis and accuracy tracking
        :param auto_sampling_pct: Percentage of input data to be reported as raw for challenger
            analysis and accuracy tracking.
        :type auto_sampling_pct: int | float
        :return: the MLOps instance
        :rtype: MLOps
        """

        self._auto_sampling_pct = validate_sampling_percentage(auto_sampling_pct)
        return self

    # ------------------------------------------------------
    #  ADVANCED PREDICTION REPORTING CONFIGURATION
    # ------------------------------------------------------
    def set_histogram_bin_count(self, histogram_bin_count):
        """
        Advanced.
        Set the number of histogram bins to use during aggregation.
        This overrides the default when calling `report_aggregated_predictions_data()`.

        :param histogram_bin_count: the number of histogram bins
        :type histogram_bin_count: int
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_positive_num(histogram_bin_count, "histogram_bin_count")
        config.set_config(
            ConfigConstants.STATS_AGGREGATION_HISTOGRAM_BIN_COUNT, histogram_bin_count
        )
        return self

    def set_distinct_category_count(self, distinct_category_count):
        """
        Advanced.
        Set the number of distinct categories to use during aggregation.
        This overrides the default when calling `report_aggregated_prediction_data()`.

        :param distinct_category_count: the number of categories
        :type distinct_category_count: int
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_positive_num(distinct_category_count, "distinct_category_count")
        config.set_config(
            ConfigConstants.STATS_AGGREGATION_DISTINCT_CATEGORY_COUNT, distinct_category_count
        )
        return self

    def set_aggregation_max_records(self, aggregation_max_records):
        """
        [Deprecated] All records are aggregated and dispatched to spooler at every call
        to reporting function.

        Advanced.
        Set the max number of records to aggregate.
        This overrides the default when calling `report_aggregated_prediction_data()`.
        :param aggregation_max_records: the max number of records to aggregate
        :type aggregation_max_records: int
        :return: the MLOps instance
        :rtype: MLOps
        """
        return self

    def set_segment_value_per_attribute_count(self, segment_value_per_attribute_count):
        """
        Advanced.
        Set the max number of segment attribute values tracked per segment attribute.
        This overrides the default when calling `report_aggregated_predictions_data()`
        when segmented attributes are used.

        :param segment_value_per_attribute_count: the max number of segment attribute values
        :type segment_value_per_attribute_count: int
        :return: the MLOps instance
        :rtype: MLOps
        """
        self._validate_input_positive_num(
            segment_value_per_attribute_count, "segment_value_per_attribute_count"
        )
        config.set_config(
            ConfigConstants.STATS_AGGREGATION_SEGMENT_VALUE_COUNT, segment_value_per_attribute_count
        )
        return self

    # ------------------------------------------------------
    #  REPORTING CALLS
    # ------------------------------------------------------

    def report_deployment_stats(
        self,
        num_predictions,
        execution_time_ms,
        user_error=False,
        system_error=False,
        deployment_id=None,
        model_id=None,
        batch_id=None,
    ):
        """
        Report the number of predictions and execution time
        to DataRobot MLOps.

        :param num_predictions: number of predictions
        :type num_predictions: int
        :param execution_time_ms: time in milliseconds
        :type execution_time_ms: float
        :param user_error: did the request have a user error
        :type user_error: bool
        :param system_error: did the request have a system error
        :type system_error: bool
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :param batch_id: the batch for these metrics
        :type batch_id: str
        :raises: DRApiException if parameters have the wrong type
        """
        self._validate()
        if not isinstance(num_predictions, int):
            raise DRApiException("num_predictions must be an integer.")
        if not isinstance(execution_time_ms, int) and not isinstance(execution_time_ms, float):
            raise DRApiException("execution_time_ms must be a float.")
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        _model_id = self._get_id(model_id, ConfigConstants.MODEL_ID)
        self._model.report_deployment_stats(
            _deployment_id,
            _model_id,
            num_predictions,
            user_error,
            system_error,
            execution_time_ms,
            batch_id,
        )

    def report_predictions_data(
        self,
        features_df=None,
        predictions=None,
        association_ids=None,
        class_names=None,
        deployment_id=None,
        model_id=None,
        skip_drift_tracking=False,
        skip_accuracy_tracking=False,
        batch_id=None,
    ):
        """
        Report features and predictions to DataRobot MLOps for tracking and monitoring.

        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe, optional
        :param predictions: List of predictions.  For Regression deployments, this is a 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type. For LLM
            deployments it is the list of completions
            Regression Predictions: e.g., [1, 2, 4, 3, 2]
            Binary Classification: e.g., [[0.2, 0.8], [0.3, 0.7]].
            TextGeneration predictions: eg. ["Completion 1", "Completion 2"]
        :type predictions: list, optional

        At least one of `features` or `predictions` must be specified.

        :param association_ids: an optional list of association IDs corresponding to each
            prediction. Used for accuracy calculations.  Association IDs have to be unique for each
            prediction to report.  The number of `predictions` should be equal to number of
            `association_ids` in the list
        :type association_ids: list, optional
        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list, optional
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str, optional
        :param model_id: the model for these metrics
        :type model_id: str, optional
        :param skip_drift_tracking: Should the DataRobot App skip drift calculation for this raw
            data
        :type skip_drift_tracking: bool, optional
        :param skip_accuracy_tracking: Should the DataRobot App skip accuracy calculation for
            these predictions
        :type skip_accuracy_tracking: bool, optional
        :param batch_id: ID of the batch these statistics belong to
        :type batch_id: str
        """
        self._validate()
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        _model_id = self._get_id(model_id, ConfigConstants.MODEL_ID)
        self._model.report_predictions_data(
            _deployment_id,
            _model_id,
            features_df,
            predictions,
            association_ids,
            class_names,
            skip_drift_tracking=skip_drift_tracking,
            skip_accuracy_tracking=skip_accuracy_tracking,
            batch_id=batch_id,
        )

    def _get_association_id_column_name(self, association_id_column_name):
        env_association_id_column_name = config.get_config_default(
            ConfigConstants.ASSOCIATION_ID_COLUMN_NAME, None
        )
        if env_association_id_column_name is not None:
            logger.info(
                f"Using association id column name {env_association_id_column_name}"
                " from environment variable"
            )
            return env_association_id_column_name

        if self._association_id_column_name is not None:
            logger.info(
                f"Using association id column name {self._association_id_column_name}"
                " set using MLOps API call"
            )
            return self._association_id_column_name

        return association_id_column_name

    def _divide_predictions(self, predictions, raw_df):
        """
        We have sampled the input_df and created a raw_df.  Now we want to also extract out
        predictions corresponding to the sampled rows in raw_df.
        """
        if not predictions:
            return None

        if raw_df is None:
            # Essentially, no features, but only predictions are input.  In this
            # case challenger analysis and accuracy analysis is not possible.
            return None

        # raw_df.index gives us the indexes of the rows in original df that were sampled
        # in raw_df.  We want predictions at same indexes.
        return [predictions[index] for index in raw_df.index]

    def report_aggregated_predictions_data(
        self,
        features_df=None,
        predictions=None,
        class_names=None,
        deployment_id=None,
        model_id=None,
        batch_id=None,
        # Setting Non-Zero default value will force the API to send some data in raw form, which
        # may not be desirable from the performance point of view, because client side aggregation
        # is all about performance. So, if no sampling percentage is available, then don't send any
        # raw data and aggregate everything.
        sampling_pct=0.0,
        association_id_column_name=None,
    ):
        """
        Report features and predictions to DataRobot MLOps for tracking and monitoring.
        The data will be aggregated before being enqueued on the spooler.
        Before using this method, you must call `set_feature_types()`.

        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe, optional
        :param predictions: List of predictions.  For Regression deployments, this is a 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type
            Regression Predictions: e.g. [1, 2, 4, 3, 2]
            Binary Classification: e.g. [[0.2, 0.8], [0.3, 0.7]].
        :type predictions: list, optional

        At least one of `features` or `predictions` must be specified.

        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list, optional
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str, optional
        :param model_id: the model for these metrics
        :type model_id: str, optional
        :param batch_id: ID of the batch these statistics belong to
        :type batch_id: str
        :param sampling_pct: Percentage of input data to be reported as raw for challenger
            analysis and optional accuracy tracking
        :type sampling_pct: float
        :param association_id_column_name: Name of the association id column name.  If this
            column is present in the input dataframe, accuracy tracking is enabled for the
            sampled raw data
        :type association_id_column_name: str
        """
        self._validate()
        self._normalize_feature_names(features_df)
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        _model_id = self._get_id(model_id, ConfigConstants.MODEL_ID)
        sampling_pct = get_sampling_pct(self._auto_sampling_pct, sampling_pct)
        association_id_column_name = self._get_association_id_column_name(
            association_id_column_name
        )
        raw_df = sample_dataframe(features_df, association_id_column_name, sampling_pct)
        raw_predictions = self._divide_predictions(predictions, raw_df)
        self._model.report_aggregated_predictions_data(
            _deployment_id,
            _model_id,
            features_df=features_df,
            predictions=predictions,
            class_names=class_names,
            batch_id=batch_id,
        )
        if raw_df is not None and not raw_df.empty:
            raw_df.reset_index(drop=True, inplace=True)
            if raw_predictions is None:
                association_ids = None
                skip_accuracy_tracking = True
            else:
                association_ids = raw_df[association_id_column_name].astype(str).tolist()
                skip_accuracy_tracking = False
            raw_df = raw_df.drop(columns=association_id_column_name)

            self._model.report_predictions_data(
                _deployment_id,
                _model_id,
                raw_df,
                raw_predictions,
                association_ids=association_ids,
                class_names=class_names,
                skip_drift_tracking=True,
                skip_accuracy_tracking=skip_accuracy_tracking,
                batch_id=batch_id,
            )

    def report_raw_time_series_predictions_data(
        self,
        features_df=None,
        predictions=None,
        association_ids=None,
        class_names=None,
        request_parameters=None,
        forecast_distance=None,
        row_index=None,
        partition=None,
        series_id=None,
        deployment_id=None,
        model_id=None,
        skip_drift_tracking=False,
        skip_accuracy_tracking=False,
    ):
        """
        Report features and predictions to DataRobot MLOps for tracking and monitoring
        of an external time series deployment

        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe, optional
        :param predictions: List of predictions.  For Regression deployments, this is a 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type
            Regression Predictions: e.g. [1, 2, 4, 3, 2]
            Binary Classification: e.g. [[0.2, 0.8], [0.3, 0.7]].
        :type predictions: list, optional
        :param association_ids: an optional list of association IDs corresponding to each
            prediction. Used for accuracy calculations.  Association IDs have to be unique for each
            prediction to report.  The number of `predictions` should be equal to number of
            `association_ids` in the list
        :type association_ids: list, optional
        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list, optional
        :param request_parameters: Request parameters used to make these predictions, either
            forecast point or bulk parameters
        :type request_parameters: dict[str, datetime], optional
        :param forecast_distance: list of forecast distance value used for each
            corresponding prediction
        :type forecast_distance: list[int], optional
        :param row_index: Indexes of the rows in the input for which these predictions are made
        :type row_index: list[int], optional
        :param partition: List of forecast dates for which these time series predictions are made
        :type partition: list[datetime], optional
        :param series_id: List of series ids indicating the time series each prediction belongs to
        :type series_id: list[str], optional
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str, optional
        :param model_id: the model for these metrics
        :type model_id: str, optional
        :param skip_drift_tracking: Should the DataRobot App skip drift calculation for this raw
            data
        :type skip_drift_tracking: bool, optional
        :param skip_accuracy_tracking: Should the DataRobot App skip accuracy calculation for
            these predictions
        :type skip_accuracy_tracking: bool, optional

        At least one of `features` or `predictions` must be specified.

        """
        self._validate()
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        _model_id = self._get_id(model_id, ConfigConstants.MODEL_ID)
        self._model.report_raw_time_series_predictions_data(
            _deployment_id,
            _model_id,
            features_df=features_df,
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

    def report_event(self, event, deployment_id=None):
        """
        Report an external event to DataRobot MLOps.

        :param event: an Event object specifying type, message, and other attributes
        :type: event: Event
        :param deployment_id: the deployment for these metrics
        :type deployment_id: str, optional
        """
        self._validate()
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        self._model.report_event(_deployment_id, None, event)

    def send_ping_to_agent(self, message):
        """
        Send a message into spooler to test enqueue capability, agent will not forward this message

        :param message: any string message
        :return:
        """
        self._validate()
        self._model.send_ping_to_agent(message)

    def report_deployment_metric(
        self, metric_id, value, timestamp=None, deployment_id=None, model_id=None
    ):
        """
        Report a custom deployment metric back to DataRobot MLOps.
        The metric must be created prior to reporting.
        This method reports a deployment metric.

        :param metric_id: Metric ID to report
        :type metric_id: str
        :param value: The numeric value to report for the metric
        :type value: float
        :param timestamp: Timestamp to use for reporting the metric
        :type timestamp: str, optional
        :param deployment_id: Deployment to report metric for
        :type deployment_id: str, optional
        """
        self._validate()
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        self._model.report_custom_metric(_deployment_id, model_id, metric_id, value, timestamp)

    def report_model_metric(
        self, metric_id, value, timestamp=None, deployment_id=None, model_id=None
    ):
        """
        Report a custom model metric back to DataRobot MLOps.
        The metric must be created prior to reporting.
        This method reports a model metric, so both deployment and model IDs are required to be
        available.

        :param metric_id:
        :type metric_id: str
        :param value: The numeric value to report for the metric
        :type value: float
        :param timestamp:
        :param deployment_id: Deployment Id to use for reporting the metric - if None, then taking
                    from environment or using the default deployment if set.
        :type deployment_id: str, optional
        :param model_id: Model ID to use for reporting the metric - if None, then taking from
                    configuration.
        :type model_id: str, optional
        """
        self._validate()
        _deployment_id = self._get_id(deployment_id, ConfigConstants.DEPLOYMENT_ID)
        _model_id = self._get_id(model_id, ConfigConstants.MODEL_ID)
        self._model.report_custom_metric(_deployment_id, _model_id, metric_id, value, timestamp)

    # ------------------------------------------------------
    #  PICKLING MLOPS
    # ------------------------------------------------------

    def __getstate__(self):
        """
        Simply store the config parameters for this MLOps object into a dictionary.  Make sure
        even the environment variables are saved.  This is sufficient information to reconstruct
        the MLOps object

        In order to serialize the MLOps object, we are not going to verify if the current config
        is valid or not.  We will simply serialize the current state
        :return: dictionary containing MLOps config
        """
        return config.dump_config()

    def __setstate__(self, state):
        """
        Build the MLOps object using the config.  Simply export all the keys in the 'state'
        as environment variables and call init().  As long as all the config values are exported as
        environment variables, MLOps library will use it correctly for its operation.
        :param state: Configuration dictionary
        """
        self.__init__()
        for key in state:
            os.environ[key] = str(state[key])

        self.init()
