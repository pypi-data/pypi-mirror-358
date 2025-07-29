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
import logging
from contextlib import suppress
from hashlib import sha256
from typing import Optional
from typing import Union

from datarobot_mlops.common import config
from datarobot_mlops.common.config import ConfigConstants
from datarobot_mlops.common.exception import DRApiException
from datarobot_mlops.common.exception import DRConfigKeyNotFound

"""
Hash Based Sampling Logic:

1. Divide the hash space in 2 parts.  Division is based on the "sampling percentage" configured
   by the user
2. Calculate the hash(association_id) for each row
3. If the hash(association_id) falls in the lower part, algorithm selects that row, else
   the row is rejected

    <---------------------------------- 2 ** 512 hash entries --------------------------------->
             X % of
    <------- hash ------->
             space
    +---------------------+--------------------------------------------------------------------+
    |                     |                                                                    |
    +---------------------+--------------------------------------------------------------------+

        where X = Sampling Percentage (configured by the user)

    Because hash of an "association id" is calculated, the algorithm will "deterministically" choose
    the rows to be sampled.  This is important, because we want to ensure same association id
    rows are sampled when reporting predictions and actuals (so that accuracy can be calculated)

    Uniform distribution of the hash values is critical.  This will ensure right amount of sampling
    even when the problem space is small (100 to 1000 rows).
"""
MAX_HASH = 2 ** (sha256().digest_size * 8)

logger = logging.getLogger(__name__)


def _get_hash(association_id):
    # Calculate hash of the association id
    return int.from_bytes(sha256(str(association_id).encode()).digest(), "big")


def _should_be_sampled(association_id, fraction):
    # If hash(association_id) is in the lower section of hash space, sample that row
    return _get_hash(association_id) < fraction * MAX_HASH


def sample_dataframe(df, association_id_column_name, sampling_percentage):
    if df is None:
        return None

    if not sampling_percentage:
        return None

    if sampling_percentage == 100.0:
        return df

    if not isinstance(sampling_percentage, float):
        return None

    if association_id_column_name not in df.columns:
        return None

    fraction = float(sampling_percentage / float(100))
    mask = df[association_id_column_name].apply(_should_be_sampled, fraction=fraction)
    return df[mask]


def validate_sampling_percentage(auto_sampling_pct: Union[int, float, str]) -> float:
    if auto_sampling_pct is None:
        raise DRApiException("auto_sampling_pct is empty.")
    try:
        auto_sampling_pct = float(auto_sampling_pct)
    except (ValueError, TypeError):
        raise DRApiException(f"auto_sampling_pct {auto_sampling_pct} is not a number")
    if not 0.0 <= auto_sampling_pct <= 100.0:
        raise DRApiException(
            f"Invalid value for auto sampling percentage {auto_sampling_pct}."
            "  Value should be between 0 to 100"
        )
    return auto_sampling_pct


def get_sampling_pct(
    lib_sampling_pct: Optional[float], current_sampling_pct: Union[int, float, str]
) -> float:
    with suppress(DRConfigKeyNotFound):
        env_sampling_pct: float = config.get_config(
            ConfigConstants.STATS_AGGREGATION_AUTO_SAMPLING_PERCENTAGE
        )
        try:
            env_sampling_pct = validate_sampling_percentage(env_sampling_pct)
            logger.info(
                f"Using auto sampling percent value {env_sampling_pct} from environment variable"
            )
            return env_sampling_pct
        except Exception:
            logger.warning(
                f"Invalid auto sampling percent value {env_sampling_pct} "
                "set using environment variable, ignoring it"
            )

    if lib_sampling_pct is not None:
        logger.info(
            f"Using auto sampling percent value {lib_sampling_pct}" " set using MLOps API call"
        )
        return lib_sampling_pct

    current_sampling_pct = validate_sampling_percentage(current_sampling_pct)
    logger.info(
        f"Using auto sampling percent value {current_sampling_pct} from the report API call"
    )
    return current_sampling_pct
