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


class DRCommonException(Exception):
    pass


class DRConfigKeyNotFound(DRCommonException):
    pass


class DRConfigKeyAlreadyAssigned(DRCommonException):
    pass


class DRUnsupportedType(DRCommonException):
    pass


class DRInvalidValue(DRCommonException):
    pass


class DRVarNotFound(DRCommonException):
    pass


class DRAlreadyInitialized(DRCommonException):
    pass


class DRApiException(DRCommonException):
    pass


class DRSpoolerException(DRCommonException):
    pass


class DRNotFoundException(DRCommonException):
    pass


class ColumnNameError(DRCommonException):
    def __init__(self, message, **kwargs):
        formatted_args = self.format_args(kwargs)
        error_message = message.format(**formatted_args)
        super().__init__(error_message)

    @classmethod
    def format_args(cls, error_args):
        return {key: str(value) for key, value in error_args.items()}


class AmbiguousColumnNameError(ColumnNameError):
    """Raised if two column names in a dataset are sanitized to the same value.

    Example:
        header = 'foo$bar,foo.bar'
    """

    message = (
        "Column named '{name}' conflicts with a different column with name '{previous}'. "
        "This means that the dataset contains two columns with the same name after "
        "replacing illegal name characters. For example ('datarobot' and 'datarobot') or "
        "('data$robot' and 'data.robot')."
    )

    def __init__(self, **kwargs):
        super().__init__(self.message, **kwargs)


class UnnamedColumnError(ColumnNameError):
    """Raised if there are two blank columns in a dataset

    Example:
        header = ',a,,b'
    """

    message = (
        "Datasets can only contain one unnamed column. A second unnamed column was found "
        "in position {position} in the dataset."
    )

    def __init__(self, **kwargs):
        super().__init__(self.message, **kwargs)


class ColumnOnlyContainsSpacesError(ColumnNameError):
    """Raised if a column name contains only spaces.

    Example:
        header = ' ,a,b'
        header = '    ,a,b'
    """

    message = "Column in position {position} in the dataset contains only spaces."

    def __init__(self, **kwargs):
        super().__init__(self.message, **kwargs)
