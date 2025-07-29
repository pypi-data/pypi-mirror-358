#  ---------------------------------------------------------------------------------
#  Copyright (c) 2022 DataRobot, Inc. and its affiliates. All rights reserved.
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
#  ---------------------------------------------------------------------------------

from datarobot_mlops.common.exception import DRCommonException


class DRMLOpsConnectedException(DRCommonException):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
