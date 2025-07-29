#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
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

import os
from decimal import Decimal


# For loading JSON, both libraries have similar enough APIs that we can use the same function
def json_loads(data):
    return loads(data)


# Orjson is a Python 3 only library that has been measured to be much faster than all other
# JSON libraries. However, it is also **not** a drop-in replacement for the standard library
# so a shim is required until we can drop Python 2 support.
if os.environ.get("MLOPS_DISABLE_FAST_JSON") == "1":
    from json import dumps
    from json import loads

    import numpy

    def json_dumps_str(obj, default=None):
        return dumps(obj, default=default)

    # to be compatible with orjson we need to encode str output as UTF-8 (bytes)
    def json_dumps_bytes(obj, default=None):
        return dumps(obj, default=default).encode("utf-8")

    # Using a `default` argument can impact performance so we leave it on the responsibility of the
    # caller to pass this function in when they think it is necessary
    def default_serializer(obj):
        """
        Help serialize a few extra datatypes we commonly see, especially in Prediction Data payloads.
        """
        if isinstance(obj, Decimal):
            return float(obj)  # close enough approximation for our needs
        if isinstance(obj, numpy.generic):
            return obj.item()
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        raise TypeError(f"Type {type(obj)} not JSON serializable: {obj}")

else:
    from orjson import OPT_SERIALIZE_NUMPY
    from orjson import dumps
    from orjson import loads

    def json_dumps_bytes(obj, default=None):
        return dumps(obj, default=default, option=OPT_SERIALIZE_NUMPY)

    # to be compatible with std-lib we need a version that returns a str
    def json_dumps_str(obj, default=None):
        return dumps(obj, default=default, option=OPT_SERIALIZE_NUMPY).decode("utf-8")

    # Using a `default` argument can impact performance so we leave it on the responsibility of the
    # caller to pass this function in when they think it is necessary. Since orjson has built in
    # handling of NumPy types we only need to deal with Decimal types.
    def default_serializer(obj):
        """
        Help serialize a few extra datatypes we commonly see, especially in Prediction Data payloads.
        """
        if isinstance(obj, Decimal):
            return float(obj)  # close enough approximation for our needs
        raise TypeError  # orjson doesn't use exception message so don't bother
