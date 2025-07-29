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

from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.enums import MLOpsSpoolAction
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRSpoolerException
from datarobot_mlops.spooler.record_spooler import RecordSpooler


class StdoutRecordSpooler(RecordSpooler):
    def __init__(self):
        super().__init__()
        self.initialized = False

    @staticmethod
    def get_type():
        return SpoolerType.STDOUT

    def get_required_config(self):
        return []

    def get_optional_config(self):
        return []

    def get_message_byte_size_limit(self):
        return -1

    def set_config(self):
        missing = super().get_missing_config()
        if len(missing) > 0:
            raise DRSpoolerException(f"Configuration values missing: {missing}")
        data_format_str = config.get_config_default(ConfigConstants.SPOOLER_DATA_FORMAT, None)
        if data_format_str:
            raise DRSpoolerException(
                f"Data Format: '{data_format_str}' is not supported for the Stdout Spooler"
            )

    def open(self, action=MLOpsSpoolAction.ENQUEUE):
        self.set_config()
        self.initialized = True

    def enqueue(self, record_list):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        for record in record_list:
            print(record)

    def dequeue(self):
        pass

    def close(self):
        pass

    def __dict__(self):
        return {
            ConfigConstants.SPOOLER_TYPE.name: SpoolerType.STDOUT.name,
        }
