#  Copyright (c) 2023 DataRobot, Inc. and its affiliates. All rights reserved.
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

import datetime
import logging
import math
import time
import warnings
from functools import partial

import aiohttp
import requests

from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.config import get_config_default
from datarobot_mlops.common.datarobot_url_helper import DataRobotEndpoint
from datarobot_mlops.common.enums import HTTPStatus
from datarobot_mlops.common.exception import DRNotFoundException
from datarobot_mlops.common.exception import DRUnsupportedType
from datarobot_mlops.common.prediction_util import get_predictions
from datarobot_mlops.common.version_util import DataRobotAppVersion
from datarobot_mlops.constants import Constants
from datarobot_mlops.json_shim import json_dumps_bytes
from datarobot_mlops.metric import AggregatedStats
from datarobot_mlops.metric import AggregatedStatsContainer
from datarobot_mlops.metric import CustomMetric
from datarobot_mlops.metric import CustomMetricContainer
from datarobot_mlops.metric import DeploymentStats
from datarobot_mlops.metric import DeploymentStatsContainer
from datarobot_mlops.metric import GeneralStats
from datarobot_mlops.metric import PredictionsData
from datarobot_mlops.metric import PredictionsDataContainer
from datarobot_mlops.metric import SerializationConstants
from datarobot_mlops.metric import serialize_predictions_data_container_list

from .connected_exception import DRMLOpsConnectedException
from .datarobot_url_helper import DataRobotUrlBuilder

logger = logging.getLogger(__name__)

agg_stats_data_keys = SerializationConstants.AggregatedStatsConstants
predictions_data_keys = SerializationConstants.PredictionsDataConstants
common_fields_keys = SerializationConstants.GeneralConstants
custom_metric_keys = SerializationConstants.CustomMetricStatsConstants

DATAROBOT_APP_VERSION_WITH_SKIP_AGGREGATION_SUPPORT = DataRobotAppVersion(major=8, minor=0, patch=6)


class ApiLimits:
    DATA_REPORTING_MAX_CHUNKS = 1000
    DATA_REPORTING_MAX_LINES_PER_CHUNK = 10000
    DATA_REPORTING_MAX_ROWS_PER_API_CALL = 10000
    ACTUALS_REPORTING_MAX_LINES = 10000
    CUSTOM_METRICS_REPORTING_MAX_LINES = 10000


class ReportingApiClient:
    """
    This class provides helper methods to communicate with
    DataRobot MLOps.
    *Note*: These class methods can only be run from a node
    with connectivity to DataRobot MLOps.

    :param service_url: DataRobot MLOps URL
    :type service_url: str
    :param api_key: DataRobot MLOps user API key
    :type api_key: str
    :returns: class instance
    :rtype: ReportingApiClient
    """

    AUTHORIZATION_TOKEN_PREFIX = "Bearer "
    RESPONSE_STATUS_KEY = "status"
    RESPONSE_FULL_API_VERSION = "versionString"
    RESPONSE_API_MAJOR_VERSION = "major"
    RESPONSE_API_MINOR_VERSION = "minor"
    RESPONSE_LOCATION_KEY = "Location"

    ASYNC_STATUS_ACTIVE = "active"
    ASYNC_STATUS_ERROR = "error"
    ASYNC_STATUS_ABORT = "abort"
    ASYNC_STATUS_INITIALIZED = "initialized"
    ASYNC_STATUS_RUNNING = "running"
    ASYNC_WAIT_SLEEP_TIME = 2

    def __init__(
        self, service_url, api_key, verify=True, dry_run=False, datarobot_app_version=None
    ):
        self._service_url = service_url
        self._api_key = ReportingApiClient.AUTHORIZATION_TOKEN_PREFIX + api_key
        self._verify = verify
        self._common_headers = {"Authorization": self._api_key}
        self._api_version = None
        self._api_major_version = None
        self._api_minor_version = None
        self._datarobot_url_builder = DataRobotUrlBuilder(self._service_url)
        self._datarobot_app_version = DataRobotAppVersion(string_version=Constants.MLOPS_VERSION)
        self.__session = None

        if dry_run:
            return

        self.update_api_version()
        self.update_datarobot_app_version()

        # If the DataRobot App Version is not input, we use the current MLOps library version
        # This is because, "typically", for every DataRobot App release, we have a corresponding
        # MLOps package release
        if datarobot_app_version:
            self._datarobot_app_version = DataRobotAppVersion(string_version=datarobot_app_version)

        major = 2
        minor = 18
        error = (
            "Tracking Agent can work with DataRobot API version '{}.{}' and above."
            "Current version: {} is old.".format(major, minor, self._api_version)
        )

        if self.is_api_version_older_than(2, 18):
            raise DRMLOpsConnectedException(error)

        if not self._verify:
            logger.warning("SSL certificates will not be verified.")

    def is_api_version_older_than(self, reference_major_version, reference_minor_version):
        if self._api_major_version < reference_major_version:
            return True
        return (
            self._api_major_version == reference_major_version
            and self._api_minor_version < reference_minor_version
        )

    def api_version_smaller_than(self, major, minor):
        if self._api_major_version < major:
            return True

        if self._api_major_version == major and self._api_minor_version < minor:
            return True

        return False

    def update_api_version(self):
        url = self._service_url + "/" + DataRobotEndpoint.API_VERSION
        headers = dict(self._common_headers)
        try:
            response = requests.get(url, headers=headers, verify=self._verify)
            if response.ok:
                self._api_version = response.json()[ReportingApiClient.RESPONSE_FULL_API_VERSION]
                self._api_major_version = response.json()[
                    ReportingApiClient.RESPONSE_API_MAJOR_VERSION
                ]
                self._api_minor_version = response.json()[
                    ReportingApiClient.RESPONSE_API_MINOR_VERSION
                ]
            else:
                if response.status_code == 401:
                    raise DRMLOpsConnectedException(
                        "Call {} failed: invalid Authorization header. "
                        "Make sure you have supplied a valid API token.".format(url)
                    )
                raise DRMLOpsConnectedException(f"Call {url} failed; text: [{response.text}]")
        except requests.exceptions.ConnectionError as e:
            raise DRMLOpsConnectedException(
                f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
            )

    def update_datarobot_app_version(self):
        """
        Placeholder method to query the DataRobot App version if and when it is available
        :return:
        """
        return

    @property
    def _session(self):
        # Lazily create the ClientSession so users don't have to remember to call shutdown()
        # if they didn't actually end up needing an async client.
        if self.__session is None:
            self.__session = aiohttp.ClientSession()
        return self.__session

    @staticmethod
    def _validate_col_exists(df, col_name):
        if col_name not in df.columns:
            raise Exception(f"Data does not include {col_name} column")

    @staticmethod
    def _get_correct_actual_value(value, deployment_type="Regression"):
        if deployment_type == "Regression":
            return float(value)
        return str(value)

    @staticmethod
    def _get_correct_flag_value(value_str):
        if value_str == "True":
            return True
        return False

    async def post_message(self, url, serialized_payload):
        headers = dict(self._common_headers)
        headers.update({"Content-Type": "application/json"})
        # TODO: make sure version is in the header

        response = await self._session.post(
            url, headers=headers, data=serialized_payload, ssl=self._verify
        )
        if response.status == HTTPStatus.NOT_FOUND:
            raise DRNotFoundException(f"URL {url} not found.")
        if response.status != HTTPStatus.ACCEPTED:
            message = await response.text()
            raise DRMLOpsConnectedException(f"Failed to post to {url}: {message}")
        if response.ok:
            json_response = await response.text()
            return json_response
        message = await response.text()
        raise DRMLOpsConnectedException(f"Call {url} failed; text: [{message}]")

    def _build_deployment_stats_container(
        self,
        model_id,
        timestamp,
        num_predictions,
        execution_time_ms=None,
        batch_id=None,
        user_error=False,
        system_error=False,
    ):
        deployment_stats = DeploymentStats(
            num_predictions, execution_time_ms, user_error, system_error
        )
        deployment_stats_container = DeploymentStatsContainer(
            GeneralStats(model_id, timestamp, batch_id), deployment_stats
        )

        return deployment_stats_container

    async def report_deployment_stats(
        self,
        deployment_id,
        model_id,
        num_predictions,
        execution_time_ms=None,
        timestamp=None,
        dry_run=False,
        batch_id=None,
        user_error=False,
        system_error=False,
    ):
        url = self._datarobot_url_builder.report_deployment_stats(deployment_id)

        container = self._build_deployment_stats_container(
            model_id,
            timestamp,
            num_predictions,
            execution_time_ms,
            batch_id,
            user_error,
            system_error,
        )
        serialized_container = container.to_api_payload()

        if dry_run:
            return {"message": "ok"}

        try:
            await self.post_message(url, serialized_container)

        except requests.exceptions.ConnectionError as e:
            raise DRMLOpsConnectedException(
                f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
            )

    def _build_prediction_data_container_list(
        self,
        model_id,
        data,
        association_ids=None,
        assoc_id=None,
        predictions=None,
        target_col=None,
        prediction_cols=None,
        class_names=None,
        timestamp=None,
        batch_id=None,
    ):
        """
        Builds the payload to report to MLOps

        Association ids can be passed using 'association_ids' parameter or as part of 'data'
        DataFrame and passing column name in 'assoc_id'.  If both are specified,
        'association_ids' is used.

        Similarly, predictions can be passed using 'predictions' parameter or as part of 'data'
        DataFrame and passing column name in 'target_col'.  If both are specified,
        'predictions' is used

        :param model_id:
        :param data:
        :param association_ids:
        :param assoc_id:
        :param predictions:
        :param target_col:
        :param prediction_cols:
        :param class_names:
        :param timestamp:
        :param batch_id:
        :return:
        """

        predictions = get_predictions(
            df=data,
            predictions=predictions,
            target_col=target_col,
            prediction_cols=prediction_cols,
            class_names=class_names,
        )

        # For 6.0 we should not drop the column
        if self._api_version == "2.20":
            feature_data = data
        else:
            if target_col is not None and target_col in data.columns:
                feature_data = data.drop(columns=target_col)
            else:
                feature_data = data

        assoc_id_list = None
        if association_ids is not None:
            assoc_id_list = association_ids
        elif assoc_id:
            if feature_data is None or assoc_id not in feature_data.columns:
                raise Exception(f"Error: assoc_id column '{assoc_id}' is not present in DataFrame")
            assoc_ids = feature_data[assoc_id].tolist()
            assoc_id_list = list(map(str, assoc_ids))

        if assoc_id is not None and feature_data is not None and assoc_id in feature_data.columns:
            feature_data = feature_data.drop(columns=assoc_id)

        nr_lines = len(data) if data is not None else len(predictions)
        max_lines_per_chunk = get_config_default(
            ConfigConstants.MLOPS_SAMPLES_GROUP_SIZE_FOR_MLOPS_API_ENDPOINT,
            ApiLimits.DATA_REPORTING_MAX_LINES_PER_CHUNK,
        )
        nr_chunks = math.ceil(nr_lines / max_lines_per_chunk)
        max_chunks = get_config_default(
            ConfigConstants.MLOPS_MAX_GROUPS_FOR_MLOPS_API_ENDPOINT,
            ApiLimits.DATA_REPORTING_MAX_CHUNKS,
        )
        if nr_chunks > max_chunks:
            raise Exception(
                "The dataset provided for data reporting is too big. Currently supporting "
                " up to {} samples per MLOps API call".format(max_lines_per_chunk * max_chunks)
            )

        container_list = []
        for chunk_idx in range(0, nr_chunks):
            from_line = chunk_idx * max_lines_per_chunk
            to_line = (chunk_idx + 1) * max_lines_per_chunk
            if to_line > nr_lines:
                to_line = nr_lines

            assoc_id_list_section = None
            if assoc_id_list:
                assoc_id_list_section = assoc_id_list[from_line:to_line]
            features_df = None
            if feature_data is not None and len(feature_data.columns) > 0:
                features_df = feature_data[from_line:to_line]
            predictions_data = PredictionsData(
                features_df,
                predictions[from_line:to_line],
                association_ids=assoc_id_list_section,
                class_names=class_names,
            )

            if batch_id and self.is_api_version_older_than(2, 31):
                print(
                    "Current API version: '{}' does not support batch monitoring via batch ID,"
                    " it is supported from API version '2.31', ignoring batch_id: {}".format(
                        self._api_version, batch_id
                    )
                )
                batch_id = None
            predictions_data_container = PredictionsDataContainer(
                GeneralStats(model_id, timestamp, batch_id=batch_id),
                predictions_data,
                api_format=True,
            )

            container_list.append(predictions_data_container)

        return container_list

    async def report_prediction_data(
        self,
        deployment_id,
        model_id,
        data,
        association_ids=None,
        assoc_id_col=None,
        predictions=None,
        target_col=None,
        prediction_cols=None,
        class_names=None,
        timestamp=None,
        skip_drift_tracking=False,
        skip_accuracy_tracking=False,
        batch_id=None,
        dry_run=False,
    ):
        """
        Report prediction data for a given model and deployment

        :param deployment_id: deployment ID to use for reporting
        :type deployment_id: str
        :param model_id: Model ID to report prediction data for
        :type model_id: str
        :param data: DataFrame containing both the feature data and the prediction result
        :type data: pandas.Dataframe
        :param association_ids: List of association ids if not part of the 'data' DataFrame
        :type association_ids: Optional(list(str))
        :param assoc_id_col: Name of column containing association ids
        :type assoc_id_col: Optional(str)
        :param predictions: List of predictions ids if not part of the 'data' DataFrame
        :type predictions: Optional(list(?))
        :param target_col: Name of the target column (label)
        :type target_col: str
        :param prediction_cols: List of names of the prediction columns
        :type prediction_cols: list
        :param class_names: List of target class names
        :type class_names: list
        :param timestamp: RFC3339 Timestamp of this prediction data
        :type timestamp: str
        :param skip_drift_tracking
        :type skip_drift_tracking: bool
        :param skip_accuracy_tracking
        :type skip_accuracy_tracking: bool
        param batch_id: ID of the batch these predictions belong to
        :type batch_id: str
        :returns: Tuple (response from MLOps, size of payload sent)
        :rtype: Tuple
        :raises DRMLOpsConnectedException: if request fails
        """
        url = self._datarobot_url_builder.report_prediction_data(deployment_id)
        input_row_count = data.shape[0] if data is not None else len(predictions)
        start = 0
        max_lines_per_chunk = get_config_default(
            ConfigConstants.MLOPS_SAMPLES_GROUP_SIZE_FOR_MLOPS_API_ENDPOINT,
            ApiLimits.DATA_REPORTING_MAX_LINES_PER_CHUNK,
        )
        max_chunks = get_config_default(
            ConfigConstants.MLOPS_MAX_GROUPS_FOR_MLOPS_API_ENDPOINT,
            ApiLimits.DATA_REPORTING_MAX_CHUNKS,
        )
        max_rows_per_api_call = get_config_default(
            ConfigConstants.MLOPS_MAX_ROWS_FOR_MLOPS_API_ENDPOINT,
            ApiLimits.DATA_REPORTING_MAX_ROWS_PER_API_CALL,
        )

        size = min(max_rows_per_api_call, max_lines_per_chunk * max_chunks)

        aggregate_payload_size = 0
        last_response = {}
        while start < input_row_count:
            end = start + size
            if end > input_row_count:
                end = input_row_count
            data_chunk = data[start:end] if data is not None else None
            _predictions = predictions[start:end] if predictions is not None else None
            _association_ids = association_ids[start:end] if association_ids is not None else None
            container_list = self._build_prediction_data_container_list(
                model_id=model_id,
                data=data_chunk,
                association_ids=_association_ids,
                assoc_id=assoc_id_col,
                predictions=_predictions,
                prediction_cols=prediction_cols,
                target_col=target_col,
                class_names=class_names,
                timestamp=timestamp,
                batch_id=batch_id,
            )

            serialized_payload = serialize_predictions_data_container_list(
                container_list, skip_drift_tracking, skip_accuracy_tracking
            )

            try:
                if dry_run:
                    payload_size = len(serialized_payload)
                    aggregate_payload_size += payload_size
                    start = end
                    last_response = {"message": "ok"}
                else:
                    last_response = await self.post_message(url, serialized_payload)
                    payload_size = len(serialized_payload)
                    aggregate_payload_size += payload_size
                    start = end
                continue

            except requests.exceptions.ConnectionError as e:
                raise DRMLOpsConnectedException(
                    f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
                )

        return last_response, aggregate_payload_size

    def _build_aggregated_stats_container(
        self,
        model_id,
        numeric_aggregate_map,
        categorical_aggregate_map,
        prediction_aggregate_map,
        segment_attributes_aggregated_stats,
        class_names,
        timestamp=None,
        batch_id=None,
    ):
        aggregated_stats = AggregatedStats(
            numeric_aggregate_map=numeric_aggregate_map,
            categorical_aggregate_map=categorical_aggregate_map,
            prediction_aggregate_map=prediction_aggregate_map,
            segment_attributes_aggregated_stats=segment_attributes_aggregated_stats,
            class_names=class_names,
        )

        general_stats = GeneralStats(model_id, timestamp, batch_id)
        container = AggregatedStatsContainer(general_stats, aggregated_stats, api_format=True)
        return container

    async def report_aggregated_prediction_data(
        self, deployment_id, model_id, payload=None, batch_id=None, dry_run=False
    ):
        """
        Report aggregated stats data for a given model and deployment

        :param deployment_id: deployment ID to use for reporting
        :type deployment_id: str
        :param model_id: Model ID to report prediction data for
        :type model_id: str
        :param payload: data read from spooler
        :param batch_id: ID of the batch these predictions belong to
        :type batch_id: str
        :param dry_run: if set, record will not be reported to DR app
        :returns: Tuple (response from MLOps, size of payload sent)
        :rtype: Tuple
        :raises DRMLOpsConnectedException: if request fails
        """

        url = self._datarobot_url_builder.report_aggregated_prediction_data(deployment_id)

        container = self._build_aggregated_stats_container(
            model_id=model_id,
            numeric_aggregate_map=payload.get(agg_stats_data_keys.NUMERIC_AGGREGATE_MAP),
            categorical_aggregate_map=payload.get(agg_stats_data_keys.CATEGORICAL_AGGREGATE_MAP),
            prediction_aggregate_map=payload.get(agg_stats_data_keys.PREDICTION_AGGREGATE_MAP),
            segment_attributes_aggregated_stats=payload.get(
                agg_stats_data_keys.SEGMENT_ATTRIBUTES_AGGREGATE_STATS
            ),
            class_names=payload.get(predictions_data_keys.CLASS_NAMES_FIELD_NAME),
            timestamp=payload[common_fields_keys.TIMESTAMP_FIELD_NAME],
            batch_id=batch_id,
        )

        serialized_container = container.to_api_payload()

        if dry_run:
            return {"message": "ok"}

        try:
            await self.post_message(url, serialized_container)

        except requests.exceptions.ConnectionError as e:
            raise DRMLOpsConnectedException(
                f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
            )

    def _get_correct_custom_metrics_timestamp(self, x, timestamp_format=None):
        if timestamp_format:
            micro_ts = datetime.datetime.strptime(x, timestamp_format).strftime(
                "%Y-%m-%d %H:%M:%S.%f%z"
            )
            return micro_ts[0:23] + micro_ts[26:]
        return x

    def _build_custom_metric_container(self, model_id, custom_metric_id, values, timestamps):
        custom_metric = CustomMetric(custom_metric_id, values, timestamps)
        custom_metric_container = CustomMetricContainer(
            GeneralStats(model_id, None, batch_id=None), custom_metric, api_format=True
        )
        return custom_metric_container

    async def submit_custom_metrics_from_dataframe(
        self,
        deployment_id,
        model_id,
        custom_metric_id,
        input_df,
        timestamp_col,
        value_col,
        timestamp_format=None,
        dry_run=False,
        progress_callback=None,
    ):
        self._validate_col_exists(input_df, timestamp_col)
        self._validate_col_exists(input_df, value_col)

        dataframe = input_df[[timestamp_col, value_col]]
        dataframe[timestamp_col].apply(
            partial(self._get_correct_custom_metrics_timestamp, timestamp_format=timestamp_format)
        )

        url = self._datarobot_url_builder.report_custom_metrics(deployment_id, custom_metric_id)
        total_number_of_values = len(dataframe.index)
        start = 0
        aggregate_payload_size = 0
        requests_sent = 0
        while start < total_number_of_values:
            end = start + ApiLimits.CUSTOM_METRICS_REPORTING_MAX_LINES
            if end > total_number_of_values:
                end = total_number_of_values
            custom_metrics_chunk = dataframe[start:end]
            container = self._build_custom_metric_container(
                model_id,
                custom_metric_id,
                custom_metrics_chunk[value_col].to_numpy(),
                custom_metrics_chunk[timestamp_col].to_numpy(),
            )

            serialized_container = container.to_api_payload()

            try:
                start_time = time.time()
                if dry_run:
                    last_response = {"message": "ok"}

                else:
                    last_response = await self.post_message(url, serialized_container)

                end_time = time.time()
                payload_size = custom_metrics_chunk.shape[0]
                aggregate_payload_size += payload_size
                start = end
                requests_sent += 1
            except requests.exceptions.ConnectionError as e:
                raise DRMLOpsConnectedException(
                    f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
                )
            if progress_callback:
                progress_callback(
                    total_number_of_values,
                    requests_sent * ApiLimits.CUSTOM_METRICS_REPORTING_MAX_LINES,
                    end_time - start_time,
                )
        return last_response, aggregate_payload_size

    async def report_custom_metrics(
        self,
        deployment_id,
        model_id,
        custom_metric_id,
        buckets,
        dry_run=False,
    ):

        url = self._datarobot_url_builder.report_custom_metrics(deployment_id, custom_metric_id)
        number_of_values = len(buckets)

        payload = {
            common_fields_keys.MODEL_ID_FIELD_NAME: model_id,
            custom_metric_keys.BUCKETS_FIELD_NAME: buckets,
        }

        serialized_payload = json_dumps_bytes(payload)

        try:
            if dry_run:
                response = {"message": "ok"}

            else:
                response = await self.post_message(url, serialized_payload)

        except requests.exceptions.ConnectionError as e:
            raise DRMLOpsConnectedException(
                f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
            )

        return response, number_of_values

    # -------------------------------------------------------------------------
    # The next few functions have to do with submitting actuals.
    # There is not yet an MLOps call for submitting actuals in the Python SDK.
    # As such, these are not currently getting refactored to be handled by the
    # Python API spooler.
    # However, I'm leaving these functions in this file because at some point,
    # they should be included in the Python SDK and properly refactored.
    # -------------------------------------------------------------------------

    def _get_url_request_response(self, url, allow_redirects=True, params=None):
        return requests.get(
            url,
            headers=self._common_headers,
            allow_redirects=allow_redirects,
            verify=self._verify,
            params=params,
        )

    def _wait_for_async_completion(self, async_location, max_wait):
        """
        Wait for successful resolution of the provided async_location.

        :param async_location: The URL we are polling for resolution.
        :type async_location: str
        :param max_wait: The number of seconds to wait before giving up.
        :type max_wait: int
        :returns: True on success.
        :rtype: bool
        :returns: The URL of the now-finished resource
        :rtype str
        :raises: DRMLOpsConnectedException if status is error
        :raises: RuntimeError if the resource did not resolve in time
        """
        start_time = time.time()

        while time.time() < start_time + max_wait:
            response = self._get_url_request_response(async_location, allow_redirects=False)
            if response.status_code == HTTPStatus.SEE_OTHER:
                return response.headers[ReportingApiClient.RESPONSE_LOCATION_KEY]
            if response.status_code != HTTPStatus.OK:
                raise DRMLOpsConnectedException(
                    f"Call {async_location} failed; text: [{response.text}]"
                )
            data = response.json()
            if ReportingApiClient.RESPONSE_STATUS_KEY in data:
                async_status = data[ReportingApiClient.RESPONSE_STATUS_KEY].lower()
                if async_status in [
                    ReportingApiClient.ASYNC_STATUS_INITIALIZED,
                    ReportingApiClient.ASYNC_STATUS_RUNNING,
                ]:
                    pass
                elif async_status in [ReportingApiClient.ASYNC_STATUS_ACTIVE]:
                    return True
                elif async_status in [
                    ReportingApiClient.ASYNC_STATUS_ABORT,
                    ReportingApiClient.ASYNC_STATUS_ERROR,
                ]:
                    raise DRMLOpsConnectedException(str(data))
                else:
                    raise DRMLOpsConnectedException(f"Task status '{async_status}' is not valid")
            else:
                return True
            logger.debug(
                "Retrying request to %s in %s seconds.",
                async_location,
                ReportingApiClient.ASYNC_WAIT_SLEEP_TIME,
            )
            time.sleep(ReportingApiClient.ASYNC_WAIT_SLEEP_TIME)
        raise RuntimeError(f"Client timed out waiting for {async_location} to resolve")

    async def submit_actuals(self, deployment_id, actuals, wait_for_result=True, timeout=180):
        """
        :param deployment_id: ID of the deployment for which the actuals are being submitted
        :param actuals: List of actuals with schema:
                        Regression: {"actualValue": 23, "wasActedOn": False / True,
                        "timestamp": RFC3339 timestamp, "associationId": "x_23423_23423"}
                        Binary: {"actualValue": "<className>", "wasActedOn": False / True,
                        "timestamp": RFC3339 timestamp, "associationId": "x_23423_23423"}
        :param wait_for_result: if True, wait for operation to finish. If False, return immediately.
        :type wait_for_result: bool
        :param timeout: if wait_for_result is True, how long to wait for async completion
        :type timeout: int
        """

        if len(actuals) == 0:
            raise DRMLOpsConnectedException("Empty actuals list to post")

        for actual in actuals:
            if Constants.ACTUALS_VALUE_KEY not in actual:
                raise DRMLOpsConnectedException(
                    f"'{Constants.ACTUALS_VALUE_KEY}' missing in '{str(actual)}'"
                )
            if (
                not isinstance(actual[Constants.ACTUALS_VALUE_KEY], float)
                and not isinstance(actual[Constants.ACTUALS_VALUE_KEY], str)
                and not isinstance(actual[Constants.ACTUALS_VALUE_KEY], int)
            ):
                raise DRUnsupportedType(
                    "'{}' must be either string, int or float, '{}'".format(
                        Constants.ACTUALS_VALUE_KEY, str(actual)
                    )
                )

            if Constants.ACTUALS_ASSOCIATION_ID_KEY not in actual:
                raise DRMLOpsConnectedException(
                    f"'{Constants.ACTUALS_ASSOCIATION_ID_KEY}' missing in '{str(actual)}'"
                )

            if Constants.ACTUALS_WAS_ACTED_ON_KEY in actual and not isinstance(
                actual[Constants.ACTUALS_WAS_ACTED_ON_KEY], bool
            ):
                raise DRUnsupportedType(
                    "'{}' should be bool, '{}'".format(
                        Constants.ACTUALS_WAS_ACTED_ON_KEY, str(actual)
                    )
                )

        url = self._datarobot_url_builder.report_actuals(deployment_id)
        headers = dict(self._common_headers)
        headers.update({"Content-Type": "application/json"})
        data = {"data": actuals}
        try:
            response = await self._session.post(
                url, headers=headers, data=json_dumps_bytes(data), ssl=self._verify
            )
            if response.status == HTTPStatus.NOT_FOUND:
                raise DRNotFoundException(f"Deployment ID {deployment_id} not found.")
            if response.status != HTTPStatus.ACCEPTED:
                message = await response.text()
                raise DRMLOpsConnectedException(f"Failed to post actuals: {message}")
            if response.ok:
                json_response = await response.json(content_type=None)
                if wait_for_result:
                    self._wait_for_async_completion(
                        response.headers[ReportingApiClient.RESPONSE_LOCATION_KEY], timeout
                    )
                return json_response
            message = await response.text()
            raise DRMLOpsConnectedException(f"Call {url} failed; text: [{message}]")
        except requests.exceptions.ConnectionError as e:
            raise DRMLOpsConnectedException(
                f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
            )

    async def submit_actuals_from_dataframe(
        self,
        deployment_id,
        deployment_type,
        dataframe,
        assoc_id_col=Constants.ACTUALS_ASSOCIATION_ID_KEY,
        actual_value_col=Constants.ACTUALS_VALUE_KEY,
        was_act_on_col=Constants.ACTUALS_WAS_ACTED_ON_KEY,
        timestamp_col=Constants.ACTUALS_TIMESTAMP_KEY,
        progress_callback=None,
        dry_run=False,
    ):
        """
        Submit actuals to MLOps App from the given DataFrame.
        This call will specific columns of the DataFrame to extract the association ids,
        actual values of predictions and other information. The data will be submitted to the
        MLOps app chunk by chunk, where the maximal chunk size is 10K lines.

        :param deployment_id: ID of deployment to report actual on
        :type deployment_id: str
        :param dataframe: DataFrame containing all the data
        :type dataframe: pandas.DataFrame
        :param assoc_id_col: Name of column containing the unique id for each prediction
        :type assoc_id_col: str
        :param actual_value_col: Name of column containing the actual value
        :type actual_value_col: str
        :param was_act_on_col: Name of column which indicates if there was an action taken on this
                               prediction
        :type was_act_on_col: str
        :param timestamp_col: Name of column containing a timestamp for the action
        :type timestamp_col: str
        :param progress_callback: A function to call after each chunk is sent to the MLOps App.
         Function signature is:
           progress_callback(total_number_of_actuals,
                             actuals_sent_so_far,
                             time_sending_last_chunk_in_seconds)

        :returns: The status of the last request to submit actuals. see the submit_actuals method
        :raises DRMLOpsConnectedException: If there was an error connecting to the MLOps app.

        """
        # Sanity check that we have all needed columns in our data
        self._validate_col_exists(dataframe, actual_value_col)
        self._validate_col_exists(dataframe, assoc_id_col)

        # Renaming the columns in case the columns needed are not in the expected name
        cols_to_rename = {}
        if assoc_id_col != Constants.ACTUALS_ASSOCIATION_ID_KEY:
            cols_to_rename[assoc_id_col] = Constants.ACTUALS_ASSOCIATION_ID_KEY
        if actual_value_col != Constants.ACTUALS_VALUE_KEY:
            cols_to_rename[actual_value_col] = Constants.ACTUALS_VALUE_KEY
        if was_act_on_col and was_act_on_col != Constants.ACTUALS_WAS_ACTED_ON_KEY:
            cols_to_rename[was_act_on_col] = Constants.ACTUALS_WAS_ACTED_ON_KEY
        if timestamp_col and timestamp_col != Constants.ACTUALS_TIMESTAMP_KEY:
            cols_to_rename[timestamp_col] = Constants.ACTUALS_TIMESTAMP_KEY
        dataframe = dataframe.rename(columns=cols_to_rename)

        # Taking only the columns we need for the actuals reporting
        cols_to_take = [Constants.ACTUALS_VALUE_KEY, Constants.ACTUALS_ASSOCIATION_ID_KEY]
        if Constants.ACTUALS_TIMESTAMP_KEY in dataframe.columns:
            cols_to_take.append(Constants.ACTUALS_TIMESTAMP_KEY)
        if Constants.ACTUALS_WAS_ACTED_ON_KEY in dataframe.columns:
            cols_to_take.append(Constants.ACTUALS_WAS_ACTED_ON_KEY)

        dataframe = dataframe[cols_to_take]
        # ensure the association ID is a string
        dataframe[Constants.ACTUALS_ASSOCIATION_ID_KEY] = dataframe[
            Constants.ACTUALS_ASSOCIATION_ID_KEY
        ].map(str)

        dataframe[Constants.ACTUALS_VALUE_KEY].apply(
            partial(self._get_correct_actual_value, deployment_type=deployment_type)
        )
        if Constants.ACTUALS_WAS_ACTED_ON_KEY in dataframe.columns:
            dataframe[Constants.ACTUALS_WAS_ACTED_ON_KEY].apply(
                partial(self._get_correct_flag_value)
            )

        url = self._datarobot_url_builder.report_actuals(deployment_id)
        headers = dict(self._common_headers)
        headers.update({"Content-Type": "application/json"})
        total_number_of_actuals = len(dataframe.index)
        start = 0
        aggregate_payload_size = 0
        requests_sent = 0
        while start < total_number_of_actuals:
            end = start + ApiLimits.ACTUALS_REPORTING_MAX_LINES
            if end > total_number_of_actuals:
                end = total_number_of_actuals
            actuals_chunk = dataframe[start:end]
            data = {"data": actuals_chunk.to_dict(orient="records")}
            try:
                start_time = time.time()
                if dry_run:
                    last_response = {"message": "ok"}
                else:
                    response = await self._session.post(
                        url, headers=headers, data=json_dumps_bytes(data), ssl=self._verify
                    )
                    if response.status == HTTPStatus.NOT_FOUND:
                        raise DRNotFoundException(f"Deployment ID {deployment_id} not found.")
                    if response.status != HTTPStatus.ACCEPTED:
                        message = await response.text()
                        raise DRMLOpsConnectedException(f"Failed to post actuals data: {message}")
                    if response.ok:
                        json_response = await response.json(content_type=None)
                        last_response = json_response
                    else:
                        message = await response.text()
                        raise DRMLOpsConnectedException(f"Call {url} failed; text:[{message}]")
                end_time = time.time()
                payload_size = actuals_chunk.shape[0]
                aggregate_payload_size += payload_size
                start = end
                requests_sent += 1
            except requests.exceptions.ConnectionError as e:
                raise DRMLOpsConnectedException(
                    f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
                )
            if progress_callback:
                progress_callback(
                    total_number_of_actuals,
                    requests_sent * ApiLimits.ACTUALS_REPORTING_MAX_LINES,
                    end_time - start_time,
                )
        return last_response, aggregate_payload_size

    async def report_actuals_data(self, deployment_id, actuals, dry_run=False):
        """
        Report actuals data for a given deployment.

        :param deployment_id: deployment ID to use for reporting
        :type deployment_id: str
        :param association_id: association ID of the record
        :type association_id: str
        :param actuals_value: the actual value of a prediction
        :type actuals_value: str
        :param was_acted_on: whether or not the prediction was acted on
        :type was_acted_on: bool
        :param timestamp: RFC3339 Timestamp of this prediction data
        :type timestamp: str

        """
        try:
            if dry_run:
                return {"message": "ok"}
            else:
                await self.submit_actuals(deployment_id, actuals)
        except requests.exceptions.ConnectionError as e:
            raise DRMLOpsConnectedException(
                f"Connection to DataRobot MLOps [{self._service_url}] refused: {e}"
            )

    async def shutdown(self):
        if self.__session is not None:
            await self.__session.close()

    def __del__(self):
        if self.__session is not None and not self.__session.closed:
            warnings.warn(
                f"Client was not properly shutdown() {repr(self)}",
                ResourceWarning,
            )
