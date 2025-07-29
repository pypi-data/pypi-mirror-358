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

import logging
import time

import requests

from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.enums import HTTPStatus
from datarobot_mlops.constants import Constants

from .connected_exception import DRMLOpsConnectedException

logger = logging.getLogger(__name__)


class ApiSync:
    """
    This class provides helper methods to communicate with
    DataRobot MLOps using synchronous requests.
    *Note*: These class methods can only be run from a node
    with connectivity to DataRobot MLOps.

    :param api_key: DataRobot MLOps user API key
    :type api_key: str
    :returns: class instance
    :rtype: ApiSync
    """

    AUTHORIZATION_TOKEN_PREFIX = "Bearer "
    DEFAULT_HTTP_RETRIES = 3
    DEFAULT_HTTP_TIMEOUT_SECONDS = 30
    DEFAULT_API_RETRY_WAIT_SECONDS = 1

    def __init__(self):

        self._api_key = config.get_config_default(ConfigConstants.MLOPS_API_TOKEN, None)
        if self._api_key is None:
            raise DRMLOpsConnectedException("MLOPS_API_TOKEN must be set.")

        self._verify = config.get_config_default(ConfigConstants.MLOPS_VERIFY_SSL, True)

        if not self._verify:
            logger.warning("Verify SSL is disabled.")

        self._num_retries = config.get_config_default(
            ConfigConstants.API_HTTP_RETRY, self.DEFAULT_HTTP_RETRIES
        )
        self._timeout_secs = config.get_config_default(
            ConfigConstants.API_POST_TIMEOUT_SECONDS, self.DEFAULT_HTTP_TIMEOUT_SECONDS
        )
        self._retry_wait_secs = config.get_config_default(
            ConfigConstants.API_HTTP_RETRY_WAIT_SECONDS, self.DEFAULT_API_RETRY_WAIT_SECONDS
        )
        agent_type = Constants.OFFICIAL_NAME + Constants.MLOPS_VERSION
        self._common_headers = {
            "Authorization": f"{ApiSync.AUTHORIZATION_TOKEN_PREFIX} {self._api_key}",
            "User-Agent": agent_type,
        }

    def post_message(self, url, serialized_payload):
        headers = self._common_headers.copy()
        headers.update({"Content-Type": "application/json"})

        retry_codes = {
            HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
            HTTPStatus.BAD_GATEWAY,  # 502
            HTTPStatus.SERVICE_UNAVAIL,  # 503
            HTTPStatus.GATEWAY_TIMEOUT,  # 504
        }

        emsg = ""
        for r in range(self._num_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    data=serialized_payload,
                    verify=self._verify,
                    timeout=self._timeout_secs,
                )

                if response.ok:
                    logger.debug("Successfully sent request to %s", url)
                    return

                if response.status_code in retry_codes:
                    logger.debug(
                        "Request to %s failed %s time(s). Retry in %s seconds.",
                        url,
                        r + 1,
                        self._retry_wait_secs,
                    )
                    time.sleep(self._retry_wait_secs)
                    continue

                emsg = response.text
                if response.status_code == HTTPStatus.NOT_FOUND:
                    raise DRMLOpsConnectedException(f"URL not found {url}. Check deployment ID.")

                # Note that we do not retry this here. The wait time indicated in the error
                # message is likely to be higher than we want to wait for interactive calls.
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    logger.error("Too many requests. Consider reporting aggregated metrics.")
                    raise DRMLOpsConnectedException(f"Too many requests for {url}: {emsg}")

                logger.debug("ERROR payload: %s", serialized_payload)
                response.raise_for_status()
                break

            except requests.exceptions.MissingSchema as e:
                raise DRMLOpsConnectedException(f"URL schema error for {url}: {e} {emsg}")

            except requests.exceptions.URLRequired as e:
                raise DRMLOpsConnectedException(f"URL required for {url}: {e} {emsg}")

            # Below are all the exception types from raise_for_status
            except requests.exceptions.HTTPError as e:
                raise DRMLOpsConnectedException(f"Request error for {url}: {e} {emsg}")

            except requests.exceptions.ConnectTimeout as e:
                msg = "API timeout exceeded. It can be increased by setting MLOPS_API_POST_TIMEOUT_SECONDS."
                raise DRMLOpsConnectedException(f"Connection timeout for {url}: {e} {msg} {emsg}")

            except requests.exceptions.ReadTimeout as e:
                msg = "API timeout exceeded. It can be increased by setting MLOPS_API_POST_TIMEOUT_SECONDS."
                raise DRMLOpsConnectedException(f"Read timeout for {url}: {e} {msg} {emsg}")

            except requests.exceptions.ConnectionError as e:
                raise DRMLOpsConnectedException(f"Connection error for {url}: {e} {emsg}")

            except requests.exceptions.TooManyRedirects as e:
                raise DRMLOpsConnectedException(f"Too many redirects for {url}: {e} {emsg}")

            # the most generic Exception for requests, encapsulates all of the above
            except requests.exceptions.RequestException as e:
                raise DRMLOpsConnectedException(f"Request exception for {url}: {e} {emsg}")

        raise DRMLOpsConnectedException(f"Unable to complete request to {url} {emsg}")
