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

import abc
import atexit
import logging
import time
from multiprocessing import Event
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Value
from queue import Empty
from queue import Full

from datarobot_mlops.channel.record import Record
from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.enums import DataFormat
from datarobot_mlops.common.enums import DataType
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRCommonException
from datarobot_mlops.json_shim import json_dumps_bytes
from datarobot_mlops.metric import CustomMetricContainer
from datarobot_mlops.metric import PredictionsDataContainer
from datarobot_mlops.metric import SerializationConstants
from datarobot_mlops.spooler.record_spooler_factory import RecordSpoolerFactory


class OutputChannelQueue:
    __metaclass__ = abc.ABCMeta

    TIMESTAMP = SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME
    MODEL_ID = SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME
    BATCH_ID = SerializationConstants.GeneralConstants.BATCH_ID_FIELD_NAME
    FEATURES = SerializationConstants.PredictionsDataConstants.FEATURES_FIELD_NAME
    PREDICTIONS = SerializationConstants.PredictionsDataConstants.PREDICTIONS_FIELD_NAME
    ASSOCIATION_IDS = SerializationConstants.PredictionsDataConstants.ASSOCIATION_IDS_FIELD_NAME
    CLASS_NAMES = SerializationConstants.PredictionsDataConstants.CLASS_NAMES_FIELD_NAME
    FORECAST = SerializationConstants.PredictionsDataConstants.FORECAST_DISTANCE_FIELD_NAME
    ROW_INDEX = SerializationConstants.PredictionsDataConstants.ROW_INDEX_FIELD_NAME
    PARTITION_FIELD = SerializationConstants.PredictionsDataConstants.PARTITION_FIELD_NAME
    SERIES_ID = SerializationConstants.PredictionsDataConstants.SERIES_ID_FIELD_NAME
    REQUEST_PARAMS = SerializationConstants.PredictionsDataConstants.REQUEST_PARAMETERS_FIELD_NAME
    SKIP_DRIFT = SerializationConstants.PredictionsDataConstants.SKIP_DRIFT_TRACKING_FIELD_NAME
    SKIP_ACCURACY = (
        SerializationConstants.PredictionsDataConstants.SKIP_ACCURACY_TRACKING_FIELD_NAME
    )
    METRIC_ID = SerializationConstants.CustomMetricStatsConstants.METRIC_ID_FIELD_NAME
    BUCKETS = SerializationConstants.CustomMetricStatsConstants.BUCKETS_FIELD_NAME
    VALUE = SerializationConstants.CustomMetricStatsConstants.METRIC_VALUE_FIELD_NAME

    def shutdown(self, timeout_sec=0, final_shutdown=True):
        if self._output_channel is not None:
            self._output_channel.close()
        self._output_channel = None

    @abc.abstractmethod
    def submit(self, record, deployment_id):
        pass

    @abc.abstractmethod
    def get_queue_size_bytes(self):
        pass

    def extract_prediction_data_range(self, data_input, start_index, end_index):
        """
        Given an iterable dictionary of prediction data, extract a range given the indexes.
        :param data_input: dictionary containing all prediction data
        :param start_index: start of subset to extract
        :param end_index: end of subset to extract
        :return: a dictionary in same format as input
        """

        data_out = dict()
        data_out[self.TIMESTAMP] = data_input[self.TIMESTAMP]
        data_out[self.MODEL_ID] = data_input[self.MODEL_ID]

        if self.BATCH_ID in data_input:
            data_out[self.BATCH_ID] = data_input[self.BATCH_ID]

        # Split feature data
        if self.FEATURES in data_input:
            feature_dict = data_input[self.FEATURES]
            feature_keys = feature_dict.keys()
            first_key = list(feature_keys)[0]
            total_feature_rows = len(feature_dict[first_key])
            if start_index < total_feature_rows:
                end_feature_index = min(end_index, total_feature_rows)
                split_feature_data = {}
                for key, value in data_input[self.FEATURES].items():
                    split_feature_data[key] = value[start_index:end_feature_index]
                data_out[self.FEATURES] = split_feature_data

        # split predictions
        if self.PREDICTIONS in data_input:
            total_prediction_rows = len(data_input[self.PREDICTIONS])

            if start_index < total_prediction_rows:
                end_prediction_index = min(end_index, total_prediction_rows)
                data_out[self.PREDICTIONS] = data_input[self.PREDICTIONS][
                    start_index:end_prediction_index
                ]

                # split association_ids
                if self.ASSOCIATION_IDS in data_input:
                    data_out[self.ASSOCIATION_IDS] = data_input[self.ASSOCIATION_IDS][
                        start_index:end_prediction_index
                    ]

                if self.FORECAST in data_input:
                    data_out[self.FORECAST] = data_input[self.FORECAST][
                        start_index:end_prediction_index
                    ]

                if self.ROW_INDEX in data_input:
                    data_out[self.ROW_INDEX] = data_input[self.ROW_INDEX][
                        start_index:end_prediction_index
                    ]

                if self.PARTITION_FIELD in data_input:
                    data_out[self.PARTITION_FIELD] = data_input[self.PARTITION_FIELD][
                        start_index:end_prediction_index
                    ]

                if self.SERIES_ID in data_input:
                    data_out[self.SERIES_ID] = data_input[self.SERIES_ID][
                        start_index:end_prediction_index
                    ]

        # copy class_names
        if self.CLASS_NAMES in data_input:
            data_out[self.CLASS_NAMES] = data_input[self.CLASS_NAMES]

        if self.REQUEST_PARAMS in data_input:
            data_out[self.REQUEST_PARAMS] = data_input[self.REQUEST_PARAMS]

        if self.SKIP_DRIFT in data_input:
            data_out[self.SKIP_DRIFT] = data_input[self.SKIP_DRIFT]

        if self.SKIP_ACCURACY in data_input:
            data_out[self.SKIP_ACCURACY] = data_input[self.SKIP_ACCURACY]

        return data_out

    def split_prediction_data_and_create_records(
        self, output_channel, deployment_id, stats_serializer, data_format, api_format
    ):
        """
        Convert a dataframe into an iterable dictionary.
        If needed, split the feature data into multiple records  sized to fit the output channel.

        :param output_channel: Output channel (sqs, file, ..)
        :param deployment_id: The deployment id
        :param stats_serializer: predictions_data_container, contains dataframe
        :param data_format: format of record (json, byte array)
        :param api_format: whether the serialization should use api format
        :return: list of records
        """
        byte_limit = output_channel.get_message_byte_size_limit()
        iterable_predictions_data_container = stats_serializer.to_iterable()
        total_size_in_byte = len(json_dumps_bytes(iterable_predictions_data_container))
        record_list = []

        # Split into multiple records if:
        #   1. estimated message size is larger than spooler limit, or
        #   2. number of rows is larger than configured

        # max_rows is based on the estimated bytes in the message
        max_rows_in_one_message = output_channel.get_feature_data_rows_in_a_message()

        # max_features is the API limit for how many rows per chunk
        # Each API message can have a configurable number of chunks (default 10) and
        # a configurable number of rows per chunk (default 10000).
        # Here we split each message into something that would fit into a single chunk.
        # The agent may group the chunks together into a single message for better efficiency,
        # but we do not leverage that here.
        max_features_in_one_chunk = output_channel.get_max_feature_data_rows_per_chunk()
        num_rows_in_one_message = min(max_rows_in_one_message, max_features_in_one_chunk)

        total_rows = stats_serializer.get_num_rows()
        if 0 < byte_limit < total_size_in_byte or total_rows > num_rows_in_one_message:
            self._logger.debug(
                "Splitting record. Max features %s. max rows %s. byte limit %s",
                max_features_in_one_chunk,
                max_rows_in_one_message,
                byte_limit,
            )

            start_index = 0
            end_index = min(num_rows_in_one_message, total_rows)

            while end_index <= total_rows:
                predictions_data_split = self.extract_prediction_data_range(
                    iterable_predictions_data_container, start_index, end_index
                )
                if api_format:
                    payload = PredictionsDataContainer.iterable_to_api_payload(
                        predictions_data_split
                    )
                else:
                    payload = stats_serializer.serialize_iterable(
                        data_format, predictions_data_split
                    )
                record_list.append(
                    Record(
                        deployment_id,
                        DataType.PREDICTIONS_DATA,
                        data_format,
                        payload,
                    )
                )

                if end_index == total_rows:
                    break
                start_index = end_index
                end_index = min(num_rows_in_one_message + end_index, total_rows)
        else:
            # Split is NOT required
            record_list.append(
                Record(
                    deployment_id,
                    DataType.PREDICTIONS_DATA,
                    data_format,
                    stats_serializer.serialize(data_format, api_format),
                )
            )
        return record_list

    def extract_custom_metric_range(self, custom_metric, start_index, end_index, api_format):
        """
        Given an iterable dictionary of custom metric data, extract a range given the indexes.
        :param custom_metric: dictionary containing all custom metric data
        :param start_index: start of subset to extract
        :param end_index: end of subset to extract
        :param api_format: whether to omit the metric ID
        :return: a dictionary in same format as input
        """
        if api_format:
            return {
                self.MODEL_ID: custom_metric[self.MODEL_ID],
                self.BUCKETS: custom_metric[self.BUCKETS][start_index:end_index],
            }

        return {
            self.METRIC_ID: custom_metric[self.METRIC_ID],
            self.MODEL_ID: custom_metric[self.MODEL_ID],
            self.BUCKETS: custom_metric[self.BUCKETS][start_index:end_index],
        }

    def split_custom_metric_and_create_records(
        self, output_channel, deployment_id, stats_serializer, data_format, api_format
    ):
        """
        Convert a custom metric values into a record
        If needed, split the custom metric value multiple records sized to fit the output channel.

        :param output_channel: Output channel (sqs, file, ..)
        :param deployment_id: The deployment id
        :param stats_serializer: predictions_data_container, contains dataframe
        :param data_format: format of record (json, byte array)
        :param api_format: whether the container should be serialized into api format
        :return: list of records
        """
        byte_limit = output_channel.get_message_byte_size_limit()
        metric_id = stats_serializer.get_metric_id()
        reserved = {"metric_id": metric_id} if api_format else ""
        custom_metric_object = stats_serializer.to_iterable()
        total_size_in_byte = len(json_dumps_bytes(custom_metric_object)) + 4 * 1024
        record_list = []

        # Split into multiple records if:
        #   output channel requires split
        #   and current size is bigger than limit
        if 0 < byte_limit < total_size_in_byte:
            num_rows = stats_serializer.get_num_rows()
            num_rows_in_one_message = output_channel.get_custom_metric_rows_in_a_message()

            start_index = 0
            end_index = min(num_rows_in_one_message, num_rows)

            while end_index <= num_rows:
                predictions_data_split = self.extract_custom_metric_range(
                    custom_metric_object, start_index, end_index, api_format
                )
                record_list.append(
                    Record(
                        deployment_id,
                        DataType.CUSTOM_METRIC,
                        data_format,
                        CustomMetricContainer.iterable_to_api_payload(predictions_data_split),
                        reserved=reserved,
                    )
                )

                if end_index == num_rows:
                    break
                start_index = end_index
                end_index = min(num_rows_in_one_message + end_index, num_rows)
        else:
            # Split is NOT required
            record_list.append(
                Record(
                    deployment_id,
                    DataType.CUSTOM_METRIC,
                    data_format,
                    stats_serializer.serialize(data_format, api_format),
                    reserved=reserved,
                )
            )
        return record_list

    def create_record_list(self, output_channel, deployment_id, stats_serializer):
        data_type = stats_serializer.data_type()
        api_format = False
        if output_channel.get_type() == SpoolerType.FILESYSTEM:
            if output_channel.get_spooler_data_format() == DataFormat.JSON:
                data_format = DataFormat.JSON
            else:
                data_format = DataFormat.BYTE_ARRAY
        else:
            data_format = DataFormat.JSON
            if output_channel.get_type() == SpoolerType.API:
                api_format = True

        if data_type == DataType.PREDICTIONS_DATA:
            return self.split_prediction_data_and_create_records(
                output_channel, deployment_id, stats_serializer, data_format, api_format
            )
        elif data_type == DataType.CUSTOM_METRIC:
            return self.split_custom_metric_and_create_records(
                output_channel, deployment_id, stats_serializer, data_format, api_format
            )
        else:
            return [
                Record(
                    deployment_id,
                    data_type,
                    data_format,
                    stats_serializer.serialize(data_format, api_format),
                )
            ]


class OutputChannelQueueSync(OutputChannelQueue):
    def get_queue_size_bytes(self):
        # This is a Synchronous queue, so we don't keep data in queue
        return 0

    def __init__(self):
        self._logger = logging.getLogger(OutputChannelQueueSync.__name__)
        output_type = SpoolerType.from_name(config.get_config(ConfigConstants.SPOOLER_TYPE))
        self._output_channel = RecordSpoolerFactory().create(output_type)
        self._output_channel.open()

    def submit(self, stats_serializer, deployment_id):
        record_list = self.create_record_list(self._output_channel, deployment_id, stats_serializer)
        self._output_channel.submit(record_list)


class OutputChannelQueueAsync(OutputChannelQueue):

    DEFAULT_REPORT_QUEUE_MAX_SIZE = 512 * 1024 * 1024  # 512MB
    DEFAULT_TIMEOUT_PROCESS_QUEUE_MS = 1000
    DEFAULT_QUEUE_OPERATION_TIMEOUT_SEC = 0.1
    DEFAULT_WORKER_TIMEOUT_SEC = 10

    def __init__(self):
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._output_channel = None

        # set timeouts
        timeout_process_queue_msec = config.get_config_default(
            ConfigConstants.TIMEOUT_PROCESS_QUEUE_MS, self.DEFAULT_TIMEOUT_PROCESS_QUEUE_MS
        )
        self._timeout_process_queue_sec = timeout_process_queue_msec / 1000

        # Create queue
        self._worker_queue = Queue()
        self._worker_ready_event = Event()

        # Set max and current size
        self._queue_max_size_bytes = config.get_config_default(
            ConfigConstants.REPORT_QUEUE_MAX_SIZE, self.DEFAULT_REPORT_QUEUE_MAX_SIZE
        )
        self._queue_current_size_bytes = Value("i", 0)
        self._process_records = Value("i", True)

        # Worker is a separate process that dequeues records from the shared queue
        # and sends records to spooler asynchronously.
        self._worker = Process(
            target=self.process_records,
            args=(self._worker_queue, self._queue_current_size_bytes, self._worker_ready_event),
            name="OutputChannelQueueAsyncWorker",
        )
        self._worker.daemon = True
        self._worker.start()

        self._worker_ready_event.wait(self.DEFAULT_WORKER_TIMEOUT_SEC)
        if not self._worker_ready_event.is_set():
            raise DRCommonException("Worker asynchronous process failed to start")

        atexit.register(self.shutdown)

    def get_queue_size_bytes(self):
        return self._queue_current_size_bytes.value

    def shutdown(self, timeout_sec=0, final_shutdown=True):
        # We registered an atexit hook to ensure the background process is shutdown
        # due to an interruption. If that happens, then this function will be executed
        # once with the final_shutdown value == True.
        # If this is a normal shutdown, the final_shutdown parameter should initially be
        # set to False by the caller. Then, on exit, this function will be called again
        # with the final_shutdown value set to the default of True.

        if final_shutdown:
            self._logger.debug("Calling final shutdown")
            timeout_sec = 1

        # Enqueue 'END' to mark the queue end to the background process
        if self._worker.is_alive():
            self._logger.debug("Adding END to queue")
            self._worker_queue.put(("END", None))

            # Wait for the background process to empty the queue
            endtime = time.time() + timeout_sec
            self._logger.debug(f"Queue shutdown. Timeout is {timeout_sec}")
            num_waits = 0
            while self._worker_ready_event.is_set() and self._queue_current_size_bytes.value > 0:
                time.sleep(self._timeout_process_queue_sec)
                num_waits += 1
                if num_waits % 10:
                    self._logger.info(
                        "Shutting down background reporting queue {} bytes remaining.".format(
                            self._queue_current_size_bytes.value
                        )
                    )
                if timeout_sec > 0 and time.time() > endtime:
                    self._logger.info("Shutdown timeout exceeded; queued calls will be dropped.")
                    self._logger.info(
                        "To avoid dropping messages, "
                        "increase or omit the MLOps.shutdown() timeout parameter."
                    )
                    break

            # Set the flag for background process to stop processing records.
            # If it hasn't emptied the queue yet, this gives it a chance
            # to end on a message boundary.
            self._worker_ready_event.clear()
            self._logger.debug("Set process_records to False.")

            # If the user provided no timeout, wait patiently for the join to complete.
            # Otherwise, wait the longer of the two: the remaining timeout or a minimum.
            if timeout_sec > 0:
                wait = max(endtime - time.time(), self.DEFAULT_WORKER_TIMEOUT_SEC)
                self._logger.debug(f"Waiting for join {wait}")
                self._worker.join(wait)
            else:
                self._logger.debug("Waiting for join for as long as it takes")
                self._worker.join()
            self._logger.debug("Join completed")

        # If this is the final exit call, close the queue and terminate the worker.
        if final_shutdown:
            self._logger.debug("Closing worker_queue")
            self._worker_queue.close()

            if self._worker.is_alive():
                self._logger.debug("Calling worker terminate")
                self._worker.terminate()
                self._logger.debug("Worker terminated")

        self._logger.debug("Shutdown complete")

    def process_records(self, worker_queue, queue_size, ready_event):
        """
        Multiprocessing Process that continuously reads records from the shared
        queue and sends them to the spooler.

        :param queue_size:     current size of queue in bytes
        :param worker_queue:   shared queue between main process
        :param ready_event:    event that indicates that worker is ready
        :return:
        """
        output_channel = RecordSpoolerFactory().create(
            spooler_type=SpoolerType.from_name(config.get_config(ConfigConstants.SPOOLER_TYPE))
        )
        output_channel.open()
        ready_event.set()

        try:
            while ready_event.is_set():
                try:
                    stats_serializer, deployment_id = worker_queue.get(
                        block=True, timeout=self.DEFAULT_QUEUE_OPERATION_TIMEOUT_SEC
                    )
                    if stats_serializer == "END":
                        break

                    with queue_size.get_lock():
                        queue_size.value -= stats_serializer.get_estimate_size()

                    # TODO: Need to handle status of each record.  Async channel should have
                    # a method to query the status of particular operation and then library
                    # can query the status of async submit.  Too advance for now
                    record_list = self.create_record_list(
                        output_channel, deployment_id, stats_serializer
                    )
                    try:
                        output_channel.submit(record_list)
                    except (Exception,):
                        self._logger.exception(
                            "Failed to submit records to output channel - discarding and continuing"
                        )
                        continue
                except Empty:
                    continue
        finally:
            while not worker_queue.empty():
                worker_queue.get(block=False)
            worker_queue.close()
            output_channel.close()
            del output_channel

    def submit(self, stats_serializer, deployment_id):
        """
        Append record to active list, if active list is full then move it to the shared queue

        :param stats_serializer:  record to be enqueued
        :param deployment_id: deployment_id for the record
        :return: True on success, False on failure
        """

        # check current queue usage
        current_queue_size = self._queue_current_size_bytes.value
        if (current_queue_size + stats_serializer.get_estimate_size()) > self._queue_max_size_bytes:
            raise DRCommonException(
                "Failed to report metric; current queue size '{}' "
                "exceeds limit '{}'".format(current_queue_size, self._queue_max_size_bytes)
            )

        try:
            self._worker_queue.put(
                (stats_serializer, deployment_id),
                block=True,
                timeout=self.DEFAULT_QUEUE_OPERATION_TIMEOUT_SEC,
            )
            with self._queue_current_size_bytes.get_lock():
                self._queue_current_size_bytes.value += stats_serializer.get_estimate_size()
        except Full:
            raise DRCommonException("Failed to report metric; mlops library record buffer is full.")
