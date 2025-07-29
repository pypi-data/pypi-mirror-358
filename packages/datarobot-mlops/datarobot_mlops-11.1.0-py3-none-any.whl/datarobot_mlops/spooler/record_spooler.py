#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
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

import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import List

from datarobot_mlops.channel.record import Record
from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.enums import DataFormat
from datarobot_mlops.common.enums import MLOpsSpoolAction
from datarobot_mlops.common.exception import DRCommonException


class RecordSpooler:
    __metaclass__ = ABCMeta
    BYTES_PER_ROW_OF_DATA = 1024 * 10  # This is a rough estimate
    BYTES_PER_CUSTOM_METRIC_ROW = 100
    JSON_DATA_FORMAT_STR = "JSON"
    BINARY_DATA_FORMAT_STR = "BYTE_ARRAY"
    DEFAULT_DEQUEUE_ACK_RECORDS = True
    DEFAULT_CONSUMER_MAX_FETCH_BEFORE_SET_EMPTY = 5

    def __init__(self):
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._spool_data_format = DataFormat.JSON
        self.enable_dequeue_ack_record = config.get_config_default(
            ConfigConstants.SPOOLER_DEQUEUE_ACK_RECORDS, self.DEFAULT_DEQUEUE_ACK_RECORDS
        )
        self._records_pending_ack = {}
        self._empty_count = 0

    def _update_empty_count(self, count):
        self._empty_count = 0 if count > 0 else self._empty_count + 1

    @abstractmethod
    def open(self, action=MLOpsSpoolAction.ENQUEUE):
        pass

    @abstractmethod
    def close(self):
        pass

    def get_spooler_data_format(self):
        return self._spool_data_format

    @abstractmethod
    def get_type(self):
        pass

    def submit(self, record_list):
        return self.enqueue(record_list)

    def get_message_byte_size_limit(self):
        """
        Returning the message size limit in bytes.
        :return: -1 (no limit)
        """
        return -1

    def get_feature_data_rows_in_a_message(self):
        """
        Returning how many feature data rows in one message.
        Return -1 means no need to split records.
        :return: -1 (no record splitting)
        """
        max_message_byte_size_limit = self.get_message_byte_size_limit()
        if max_message_byte_size_limit < 0:
            return -1

        default_rows = max_message_byte_size_limit // self.BYTES_PER_ROW_OF_DATA
        rows = config.get_config_default(
            ConfigConstants.FEATURE_DATA_ROWS_IN_ONE_MESSAGE, default_rows
        )
        return rows

    def get_max_feature_data_rows_per_chunk(self):
        return config.get_config_default(
            ConfigConstants.PREDICTIONS_DATA_MAX_LINES_PER_CHUNK,
            config.DEFAULT_PREDICTIONS_DATA_MAX_LINES_PER_CHUNK,
        )

    def get_custom_metric_rows_in_a_message(self):
        """
        Returning how many custom metrics rows (ts, value) in one message.
        Return -1 means no need to split records.
        :return: -1 (no record splitting)
        """
        max_message_byte_size_limit = self.get_message_byte_size_limit()
        if max_message_byte_size_limit < 0:
            return -1

        default_rows = max_message_byte_size_limit // self.BYTES_PER_CUSTOM_METRIC_ROW
        rows = config.get_config_default(
            ConfigConstants.CUSTOM_METRIC_ROWS_IN_ONE_MESSAGE, default_rows
        )
        return rows

    def get_missing_config(self):
        missing = []
        required = self.get_required_config()
        for req in required:
            try:
                config.get_config(req)
            except DRCommonException:
                missing.append(req)
        return missing

    @abstractmethod
    def __dict__(self):
        pass

    def _add_pending_record(self, record_id, record):
        if not self.enable_dequeue_ack_record:
            return
        self._records_pending_ack[record_id] = record

    def ack_records(self, records_id_list):
        if not self.enable_dequeue_ack_record:
            return

        for record_id in records_id_list:
            self._records_pending_ack.pop(record_id, None)

    @abstractmethod
    def dequeue(self) -> List[Record]:
        raise NotImplementedError(
            f"Dequeue operation is not yet implemented for the {self.get_type()} spooler"
        )

    @abstractmethod
    def enqueue(self, record_list: List[Record]):
        raise NotImplementedError(
            f"Enqueue operation is not yet implemented for the {self.get_type()} spooler"
        )
