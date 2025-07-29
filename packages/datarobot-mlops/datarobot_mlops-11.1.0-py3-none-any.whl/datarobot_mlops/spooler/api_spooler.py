#  Copyright (c) 2023 DataRobot, Inc. and its affiliates. All rights reserved.
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

from datarobot_mlops.common import config
from datarobot_mlops.common.api_sync import ApiSync
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.datarobot_url_helper import DataRobotUrlBuilder
from datarobot_mlops.common.enums import DataType
from datarobot_mlops.common.enums import MLOpsSpoolAction
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRSpoolerException
from datarobot_mlops.spooler.record_spooler import RecordSpooler


class ApiRecordSpooler(RecordSpooler):
    DEFAULT_MAX_MESSAGE_SIZE = 1024 * 1024

    def __init__(self):
        super().__init__()
        self.initialized = False
        self._api_sync = None
        self._datarobot_url = None
        self._url_builder = None

    @staticmethod
    def get_type():
        return SpoolerType.API

    def get_required_config(self):
        return [ConfigConstants.MLOPS_SERVICE_URL, ConfigConstants.MLOPS_API_TOKEN]

    def get_optional_config(self):
        return [ConfigConstants.MLOPS_VERIFY_SSL, ConfigConstants.API_POST_TIMEOUT_SECONDS]

    def get_message_byte_size_limit(self):
        return config.get_config_default(
            ConfigConstants.API_MAX_MESSAGE_SIZE, self.DEFAULT_MAX_MESSAGE_SIZE
        )

    def set_config(self):
        missing = super().get_missing_config()
        if len(missing) > 0:
            raise DRSpoolerException(f"Configuration values missing: {missing}")

        data_format_str = config.get_config_default(
            ConfigConstants.SPOOLER_DATA_FORMAT, self.JSON_DATA_FORMAT_STR
        )
        if data_format_str != self.JSON_DATA_FORMAT_STR:
            raise DRSpoolerException(
                f"Data Format: '{data_format_str}' is not support for the API spooler"
            )

        self._datarobot_url = config.get_config(ConfigConstants.MLOPS_SERVICE_URL)
        self._url_builder = DataRobotUrlBuilder(self._datarobot_url)
        self._api_sync = ApiSync()

    def open(self, action=MLOpsSpoolAction.ENQUEUE):
        self.set_config()
        self.initialized = True

    def enqueue(self, record_list):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        for record in record_list:
            deployment_id = record.get_deployment_id()
            data_type = record.get_data_type()
            serialized_container = record.get_payload()

            if data_type == DataType.DEPLOYMENT_STATS:
                url = self._url_builder.report_deployment_stats(deployment_id)
                self._api_sync.post_message(url, serialized_container)

            elif data_type == DataType.PREDICTIONS_DATA:
                url = self._url_builder.report_prediction_data(deployment_id)
                self._api_sync.post_message(url, serialized_container)

            elif data_type == DataType.CUSTOM_METRIC:
                reserved = record.get_reserved()
                metric_id = reserved["metric_id"]
                url = self._url_builder.report_custom_metrics(deployment_id, metric_id)
                self._api_sync.post_message(url, serialized_container)

            elif data_type == DataType.PREDICTION_STATS:
                url = self._url_builder.report_aggregated_prediction_data(deployment_id)
                self._api_sync.post_message(url, serialized_container)

            elif data_type == DataType.EVENT:
                url = self._url_builder.report_event()
                self._api_sync.post_message(url, serialized_container)

            else:
                raise DRSpoolerException("Unsupported data_type: ", DataType)

    def dequeue(self):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        # There is no dequeue for the API spooler
        pass

    def close(self):
        pass

    def __dict__(self):
        # The API token should be taken from environment variables
        return {
            ConfigConstants.SPOOLER_TYPE.name: SpoolerType.API.name,
            ConfigConstants.MLOPS_SERVICE_URL: self._datarobot_url,
        }
