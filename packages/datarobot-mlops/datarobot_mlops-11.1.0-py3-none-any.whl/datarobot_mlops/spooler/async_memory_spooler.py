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

import multiprocessing
import sys
import time
from multiprocessing import Event
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Value
from multiprocessing.connection import Client
from multiprocessing.connection import Listener
from queue import Empty
from urllib.parse import urlparse

from datarobot_mlops.channel.record import Record
from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.enums import MLOpsSpoolAction
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRCommonException
from datarobot_mlops.common.exception import DRSpoolerException
from datarobot_mlops.spooler.record_spooler import RecordSpooler

# Known issues with 'spawn' on python-3.7+, hence forcing the fork
try:
    multiprocessing.set_start_method("fork")
except RuntimeError:
    # If it fails, it is most likely that it is already set correctly
    # so ignore it and move on
    pass


class AsyncMemoryRecordSpooler(RecordSpooler):
    DEFAULT_MAX_QUEUE_SIZE = 1024 * 1024 * 1024  # 1G
    MAX_RECORDS_TO_DEQUEUE = 10
    DEFAULT_QUEUE_OPERATION_TIMEOUT = 0.1
    DEFAULT_SERVER_TIMEOUT_SEC = 10

    DEFAULT_URL = "http://localhost:6000"
    DEFAULT_START_AS_SERVER = False

    def __init__(self, start_as_server=False):
        super().__init__()

        self._queue = None
        self._queue_size = None
        self._max_queue_size = self.DEFAULT_MAX_QUEUE_SIZE
        self._initialized = False

        self._server = None
        self._server_address = None
        self._start_as_server = start_as_server
        self._connection = None
        self._enqueue_delay_sec = 0
        self._dequeue_delay_sec = 0

    def set_config(self):
        data_format_str = config.get_config_default(ConfigConstants.SPOOLER_DATA_FORMAT, None)
        if data_format_str:
            raise DRSpoolerException(
                "Data Format: '{}' is not support for the Async Memory Spooler".format(
                    data_format_str
                )
            )
        self._max_queue_size = config.get_config_default(
            ConfigConstants.MEMORY_MAX_QUEUE_SIZE, self.DEFAULT_MAX_QUEUE_SIZE
        )
        server_address_uri = urlparse(
            config.get_config_default(ConfigConstants.ASYNC_MEMORY_URL, self.DEFAULT_URL)
        )
        self._server_address = (server_address_uri.hostname, server_address_uri.port)
        self._enqueue_delay_sec = (
            config.get_config_default(ConfigConstants.ASYNC_MEMORY_ENQUEUE_DELAY_MS, 0) / 1000
        )
        self._dequeue_delay_sec = (
            config.get_config_default(ConfigConstants.ASYNC_MEMORY_DEQUEUE_DELAY_MS, 0) / 1000
        )

    def server_process(self, queue, queue_size, ready_event):
        listener = Listener(self._server_address)
        ready_event.set()
        self._connection = listener.accept()
        try:
            while True:
                msg = self._connection.recv()
                message_size = sys.getsizeof(msg)
                if queue_size.value < (self._max_queue_size - message_size):
                    queue.put(msg)
                    with queue_size.get_lock():
                        queue_size.value += message_size
                    self._logger.debug(f"Enqueue message of size {message_size}")
        except EOFError as e:
            self._logger.warning(f"client was closed - {e}")

    def open(self, action=MLOpsSpoolAction.ENQUEUE):
        if not self._initialized:
            self.set_config()
            if self._start_as_server:
                self._queue = Queue()
                self._queue_size = Value("i", 0)
                self._server_ready_event = Event()

                self._server = Process(
                    target=self.server_process,
                    args=(self._queue, self._queue_size, self._server_ready_event),
                    name="AsyncMemoryRecordSpoolerServer",
                )
                self._server.daemon = True
                self._server.start()
                self._server_ready_event.wait(self.DEFAULT_SERVER_TIMEOUT_SEC)
                if not self._server_ready_event.is_set():
                    raise DRCommonException("AsyncMemoryRecordSpooler server failed to start")
            else:
                self._connection = Client(self._server_address)
            self._initialized = True

    def close(self):
        if self._server:
            self._server.terminate()

    def delete(self):
        self.close()
        self._queue = None
        self._initialized = False

    def get_type(self):
        return SpoolerType.ASYNC_MEMORY

    def get_required_config(self):
        return []

    def get_optional_config(self):
        return []

    def reset(self):
        self.delete()
        self.open()

    def get_message_byte_size_limit(self):
        return self._max_queue_size

    def enqueue_single_message(self, message_json):
        if not self._initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        # Check size limit
        message_size = sys.getsizeof(message_json)
        if message_size > self.get_message_byte_size_limit():
            raise DRSpoolerException(f"Cannot enqueue record size: {message_size}")

        self._connection.send(message_json)

    def enqueue(self, record_list):
        if not self._initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        if self._enqueue_delay_sec > 0:
            time.sleep(self._enqueue_delay_sec)

        for r in record_list:
            self.enqueue_single_message(r.to_json())
        self._logger.debug(f"Published {len(record_list)} messages")

    def dequeue_single_message(self):
        if not self._initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        if self._dequeue_delay_sec > 0:
            time.sleep(self._dequeue_delay_sec)

        try:
            message_json = self._queue.get(block=True, timeout=self.DEFAULT_QUEUE_OPERATION_TIMEOUT)
            message_size = sys.getsizeof(message_json)
            self._logger.debug(f"Dequeue message of size {message_size}")
            with self._queue_size.get_lock():
                self._queue_size.value -= message_size
            return message_json
        except Empty:
            return None

    def dequeue(self):
        record_list = []
        for _ in range(self.MAX_RECORDS_TO_DEQUEUE):
            message_json = self.dequeue_single_message()
            if message_json:
                record_list.append(Record.from_json(message_json))

        return record_list

    def __dict__(self):
        return {
            ConfigConstants.SPOOLER_TYPE.name: SpoolerType.ASYNC_MEMORY.name,
            ConfigConstants.ASYNC_MEMORY_URL.name: self._server_address[0]
            + ":"
            + str(self._server_address[1]),
            ConfigConstants.ASYNC_MEMORY_DEQUEUE_DELAY_MS.name: self._dequeue_delay_sec,
            ConfigConstants.ASYNC_MEMORY_ENQUEUE_DELAY_MS.name: self._enqueue_delay_sec,
            ConfigConstants.MEMORY_MAX_QUEUE_SIZE.name: self._max_queue_size,
        }
