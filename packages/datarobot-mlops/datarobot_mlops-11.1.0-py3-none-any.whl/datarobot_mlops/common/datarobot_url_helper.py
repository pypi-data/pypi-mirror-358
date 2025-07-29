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

from urllib.parse import urlencode


def build_datarobot_url(host_base_url, *res, **params):
    """
    Function to build url. Examples:
    build_url('http://localhost:8080', 'deployments') => http://localhost:8080/deployments/
    build_url('https://localhost:8080', 'deployments', name="test_deployment") =>
    https://localhost:8080/deployments/?name=test_deployment
    The DataRobot API will redirect the client if the path does not end in '/'.
    :param host_base_url: REST service url base.
    :param res: path components
    :param params: REST request parameters.
    """

    url = host_base_url.rstrip("/")
    for r in res:
        if r is not None:
            url = f"{url}/{r}"
    if not url.endswith("/"):
        url += "/"
    if params:
        url = f"{url}?{urlencode(params)}"

    return url


class DataRobotEndpointPrefix:
    DEPLOYMENT = "api/v2/deployments"
    EVENTS = "api/v2/remoteEvents"


class DataRobotEndpoint:
    API_VERSION = "api/v2/version/"
    PREDICTION_REQUESTS_FROM_JSON = "predictionRequests/fromJSON"
    PREDICTION_INPUT_FROM_JSON = "predictionInputs/fromJSON"
    PREDICTION_STATS_FROM_JSON = "predictionStats/fromJSON"
    ACTUALS_FROM_JSON = "actuals/fromJSON/"
    CUSTOM_METRICS = "customMetrics"
    FROM_JSON = "fromJSON"


class DataRobotUrlBuilder:
    def __init__(self, service_url):
        service_url = service_url.replace("/api/v2", "")
        self._service_url = service_url

    def report_deployment_stats(self, deployment_id):
        return build_datarobot_url(
            self._service_url,
            DataRobotEndpointPrefix.DEPLOYMENT,
            deployment_id,
            DataRobotEndpoint.PREDICTION_REQUESTS_FROM_JSON,
        )

    def report_prediction_data(self, deployment_id):
        return build_datarobot_url(
            self._service_url,
            DataRobotEndpointPrefix.DEPLOYMENT,
            deployment_id,
            DataRobotEndpoint.PREDICTION_INPUT_FROM_JSON,
        )

    def report_aggregated_prediction_data(self, deployment_id):
        return build_datarobot_url(
            self._service_url,
            DataRobotEndpointPrefix.DEPLOYMENT,
            deployment_id,
            DataRobotEndpoint.PREDICTION_STATS_FROM_JSON,
        )

    def report_actuals(self, deployment_id):
        return build_datarobot_url(
            self._service_url,
            DataRobotEndpointPrefix.DEPLOYMENT,
            deployment_id,
            DataRobotEndpoint.ACTUALS_FROM_JSON,
        )

    def report_custom_metrics(self, deployment_id, metrics_id):
        return build_datarobot_url(
            self._service_url,
            DataRobotEndpointPrefix.DEPLOYMENT,
            deployment_id,
            DataRobotEndpoint.CUSTOM_METRICS,
            metrics_id,
            DataRobotEndpoint.FROM_JSON,
        )

    def report_event(self):
        return build_datarobot_url(self._service_url, DataRobotEndpointPrefix.EVENTS)
