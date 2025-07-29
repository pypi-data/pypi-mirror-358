#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
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

from datarobot_mlops.common import config
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRConfigKeyNotFound
from datarobot_mlops.common.exception import DRUnsupportedType
from datarobot_mlops.common.singleton import singleton
from datarobot_mlops.constants import Constants
from datarobot_mlops.spooler.async_memory_spooler import AsyncMemoryRecordSpooler
from datarobot_mlops.spooler.filesystem_spooler import FSRecordSpooler
from datarobot_mlops.spooler.memory_spooler import MemoryRecordSpooler
from datarobot_mlops.spooler.stdout_spooler import StdoutRecordSpooler


@singleton
class RecordSpoolerFactory:
    def create(self, spooler_type):

        if spooler_type == SpoolerType.STDOUT:
            return StdoutRecordSpooler()

        elif spooler_type == SpoolerType.FILESYSTEM:
            return FSRecordSpooler()

        elif spooler_type == SpoolerType.SQS:
            try:
                from datarobot_mlops.spooler.sqs_spool import SQSRecordSpooler
            except ImportError:
                message = (
                    "SqsSpoolChannel failed; missing package; "
                    "need to `pip install {}[aws]`".format(Constants.OFFICIAL_NAME)
                )
                raise RuntimeError(message)
            return SQSRecordSpooler()

        elif spooler_type == SpoolerType.RABBITMQ:
            try:
                from datarobot_mlops.spooler.rabbitmq_spooler import RabbitMQRecordSpooler
            except ImportError:
                message = (
                    "RabbitMqSpoolChannel failed; missing package; "
                    "need to `pip install {}[rabbitmq]`".format(Constants.OFFICIAL_NAME)
                )
                raise RuntimeError(message)
            return RabbitMQRecordSpooler()

        elif spooler_type == SpoolerType.PUBSUB:
            # install package as needed; conflict with DR packages; AGENT-1375
            try:
                from datarobot_mlops.spooler.pubsub_spooler import PubSubRecordSpooler
            except ImportError:
                message = (
                    "PubSubSpoolChannel failed; missing package; "
                    "need to `pip install {}[google]`".format(Constants.OFFICIAL_NAME)
                )
                raise RuntimeError(message)
            return PubSubRecordSpooler()

        elif spooler_type == SpoolerType.MEMORY:
            return MemoryRecordSpooler()

        elif spooler_type == SpoolerType.ASYNC_MEMORY:
            return AsyncMemoryRecordSpooler()
        elif spooler_type == SpoolerType.NONE:
            return None

        elif spooler_type == SpoolerType.KAFKA:
            # Install package as needed, which includes pre-built binary of the librdkafka.
            # To enable TLS / Kerberos support, the librdkafka should be re-compiled with
            # libssl-dev and libsasl2-dev. See https://github.com/edenhill/librdkafka#requirements.
            try:
                from datarobot_mlops.spooler.kafka_spooler import KafkaRecordSpooler
            except ImportError:
                message = (
                    "KafkaSpoolChannel failed; missing package; "
                    "need to `pip install {}[kafka]`".format(Constants.OFFICIAL_NAME)
                )
                raise RuntimeError(message)
            return KafkaRecordSpooler()

        elif spooler_type == SpoolerType.API:
            try:
                from datarobot_mlops.spooler.api_spooler import ApiRecordSpooler
            except ImportError:
                message = (
                    "APISpoolChannel failed; missing package; "
                    "need to `pip install {}[api]`".format(Constants.OFFICIAL_NAME)
                )
                raise RuntimeError(message)
            return ApiRecordSpooler()
        else:
            raise DRUnsupportedType(f"Unsupported spooler type: {spooler_type}")

    def get_current_configured_spooler(self):
        # Try to read the spooler configuration from environment variables
        try:
            spooler_type = SpoolerType.from_name(
                config.get_config(config.ConfigConstants.SPOOLER_TYPE)
            )
        except DRConfigKeyNotFound:
            return None

        spooler = self.create(spooler_type)
        if spooler is not None:
            spooler.set_config()

        return spooler
