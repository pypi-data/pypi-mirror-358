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

import ssl
import sys
from time import sleep
from time import time

import pika
from pika.connection import SSLOptions
from pika.exceptions import AMQPConnectionError
from pika.exceptions import NackError
from pika.exceptions import UnroutableError

from datarobot_mlops.channel.record import Record
from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.enums import MLOpsSpoolAction
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRSpoolerException
from datarobot_mlops.spooler.record_spooler import RecordSpooler


class RabbitMQRecordSpooler(RecordSpooler):

    RABBITMQ_MAX_RECORDS_TO_DEQUEUE = 10
    RABBITMQ_MESSAGE_SIZE_LIMIT_IN_BYTE = 1024 * 1024 * 50
    DEFAULT_PUBLISH_ATTEMPTS = 5
    DEFAULT_PUBLISH_INTERVAL = 0.2  # in seconds

    def __init__(self):
        super().__init__()
        self.publish_attempts = self.DEFAULT_PUBLISH_ATTEMPTS
        self.publish_interval = self.DEFAULT_PUBLISH_INTERVAL
        self.refresh_conn_time = float("inf")
        self._last_connect_time = 0
        self.initialized = False

        self._queue_url = None
        self._queue_name = None
        self._ssl_ca_certificate_path = None
        self._ssl_certificate_path = None
        self._ssl_key_path = None
        self._tls_version = None
        self._enable_ssl = False

        self.rabbitmq_params = None
        self._connection = None
        self._channel = None

    @staticmethod
    def get_type():
        return SpoolerType.RABBITMQ

    def get_required_config(self):
        return [ConfigConstants.RABBITMQ_QUEUE_URL, ConfigConstants.RABBITMQ_QUEUE_NAME]

    def get_optional_config(self):
        return []

    def set_config(self):
        missing = super().get_missing_config()
        if len(missing) > 0:
            raise DRSpoolerException(f"Configuration values missing: {missing}")

        data_format_str = config.get_config_default(
            ConfigConstants.SPOOLER_DATA_FORMAT, self.JSON_DATA_FORMAT_STR
        )
        if data_format_str != self.JSON_DATA_FORMAT_STR:
            raise DRSpoolerException(
                f"Data Format: '{data_format_str}' is not support for the RabbitMQ Spooler"
            )
        self._queue_url = config.get_config(ConfigConstants.RABBITMQ_QUEUE_URL)
        self._queue_name = config.get_config(ConfigConstants.RABBITMQ_QUEUE_NAME)

        self._ssl_ca_certificate_path = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_CA_CERTIFICATE_PATH, None
        )
        self._ssl_certificate_path = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_CERTIFICATE_PATH, None
        )
        self._ssl_key_path = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_KEYFILE_PATH, None
        )
        tls_version_str = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_TLS_VERSION, "TLSv1.2"
        )
        self._tls_version = self._convert_tls_version(tls_version_str)

        self._enable_ssl = (
            self._ssl_ca_certificate_path and self._ssl_certificate_path and self._ssl_key_path
        )

        self._validate_url(self._queue_url)
        self.rabbitmq_params = pika.URLParameters(self._queue_url)

        if self._enable_ssl:
            ssl_context = ssl.create_default_context(
                ssl.Purpose.CLIENT_AUTH, capath=self._ssl_ca_certificate_path
            )
            ssl_context.load_cert_chain(
                certfile=self._ssl_certificate_path,
                keyfile=self._ssl_key_path,
            )
            self.rabbitmq_params.ssl_options = SSLOptions(context=ssl_context)

    def open(self, action=MLOpsSpoolAction.ENQUEUE):
        self.set_config()
        try:
            self._connection = pika.BlockingConnection(self.rabbitmq_params)
            self._channel = self._connection.channel()
            self._channel.confirm_delivery()
            self._channel.queue_declare(queue=self._queue_name, durable=True)
            self._logger.debug(
                "Successfully connected to {}, using queue: {}".format(
                    self._queue_url, self._queue_name
                )
            )
            self.initialized = True
        except (AMQPConnectionError, ssl.SSLCertVerificationError) as ex:
            msg = f"Fail to establish connection to RabbitMQ: {ex}"
            self._logger.error(msg)
            raise DRSpoolerException(msg)

    def close(self):
        if self._channel and not self._channel.is_closed:
            self._channel.close()
            self._channel = None

        if self._connection and not self._connection.is_closed:
            self._connection.close()

    def reconnect(self):
        self.close()
        self.open()

    @staticmethod
    def _validate_url(url):
        if not url:
            raise DRSpoolerException("Invalid URL - " + url)

    @staticmethod
    def _convert_tls_version(tls_version_str):
        if tls_version_str == "TLSv1.1":
            return ssl.PROTOCOL_TLSv1_1
        elif tls_version_str == "TLSv1.2":
            return ssl.PROTOCOL_TLSv1_2
        return None

    def get_message_byte_size_limit(self):
        return self.RABBITMQ_MESSAGE_SIZE_LIMIT_IN_BYTE

    def publish_single_message(self, message):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        will_reconnect = self._channel is None or (
            time() - self._last_connect_time >= self.refresh_conn_time
        )

        for attempt in range(self.publish_attempts):
            # Sleep before second attempt; Increase sleep time exponentially
            if attempt > 0:
                sleep(attempt * self.publish_interval)

            if will_reconnect:
                try:
                    self.reconnect()
                except pika.exceptions.ProbableAccessDeniedError:
                    # If credentials are invalid, there is no sense to sleep and reconnect
                    raise DRSpoolerException(
                        "Access denied error when publishing a message to RabbitMQ"
                    )
                except Exception as ex:
                    self._logger.warning(
                        f"Reconnection error when publishing a message to RabbitMQ - {ex}"
                    )
                    reason = "reconnection error"
                    continue

            try:
                self._channel.basic_publish(
                    exchange="",
                    routing_key=self._queue_name,
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                return
            except (UnroutableError, NackError):
                raise DRSpoolerException("RabbitMQ: Delivery confirmation not received")
            except pika.exceptions.AMQPConnectionError:
                self._logger.debug("Connection error when publishing a message to RabbitMQ")
                reason = "connection error"
            except pika.exceptions.ChannelClosed:
                self._logger.info("Channel closed when publishing a message to RabbitMQ")
                reason = "channel close"
            except Exception as ex:
                raise DRSpoolerException(
                    f"Unexpected exception when publishing a message to RabbitMQ - {ex}"
                )

            will_reconnect = True

        raise DRSpoolerException(f"Failed to publish a message to RabbitMQ, reason: {reason}")

    def enqueue(self, record_list):
        self._logger.debug(f"About to publish {len(record_list)} messages")

        for record in record_list:
            record_json = record.to_json()

            # Check size limit
            record_size = sys.getsizeof(record_json)
            if record_size > self.get_message_byte_size_limit():
                raise DRSpoolerException(f"Cannot enqueue record size: {record_size}")

            self.publish_single_message(record_json)

        self._logger.debug(f"Published {len(record_list)} messages")

    # Used by mlops-cli for dequeue
    def empty(self):
        q = self._channel.queue_declare(self._queue_name, durable=True)
        q_len = q.method.message_count
        return q_len == 0

    def dequeue(self):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        record_list = []
        try:
            for _ in range(self.RABBITMQ_MAX_RECORDS_TO_DEQUEUE):
                method, _, body = self._channel.basic_get(
                    self._queue_name, auto_ack=(not self.enable_dequeue_ack_record)
                )
                if body is None:
                    break

                record = Record.from_json(body)
                record_list.append(record)
                self._add_pending_record(record.get_id(), method)
        except Exception as e:
            self._logger.error(
                "Failed to dequeue message from RabbitMQ[{}],"
                "with error: {}".format(self._queue_url, str(e))
            )

        return record_list

    def ack_records(self, records_id_list):
        if not self.enable_dequeue_ack_record:
            return

        for record_id in records_id_list:
            method = self._records_pending_ack.get(record_id)
            if method is not None:
                self._channel.basic_ack(delivery_tag=method.delivery_tag, multiple=False)

    def __dict__(self):
        return {
            ConfigConstants.SPOOLER_TYPE.name: SpoolerType.RABBITMQ.name,
            ConfigConstants.RABBITMQ_QUEUE_NAME.name: self._queue_name,
            ConfigConstants.RABBITMQ_QUEUE_URL.name: self._queue_url,
        }
