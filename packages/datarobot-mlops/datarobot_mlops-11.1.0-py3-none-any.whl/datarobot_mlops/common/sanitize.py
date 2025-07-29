#  ---------------------------------------------------------------------------------
#  Copyright (c) 2023 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2024.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#  ---------------------------------------------------------------------------------
import numpy as np

from datarobot_mlops.common.exception import AmbiguousColumnNameError
from datarobot_mlops.common.exception import ColumnOnlyContainsSpacesError
from datarobot_mlops.common.exception import UnnamedColumnError


def sanitize_name(name):
    """
    The `-` is used for derived feature names.
    The `$` and `.` are not allowed in R.

    IMPORTANT: Any changes here should be duplicated in:
    * https://github.com/datarobot/datasets-service/blob/master/ds/utils/sanitize.py
    """
    if isinstance(name, (int, float, np.int64, np.float64)):
        name = str(name)
    safe = name.strip().replace("-", "_").replace("$", "_").replace(".", "_")
    safe = safe.replace("{", "_").replace("}", "_")
    safe = safe.replace('"', "_")
    safe = safe.replace("\n", "_")
    safe = safe.replace("\r", "_")
    return safe


class NameSanitizer(object):
    """A stateful sanitizer that will prevent us from name collisions.

    Parameters
    ----------
    source_names : list
        These should all be unique names of columns of the dataframe.
    """

    def __init__(self, source_names: list):
        self.source_names = source_names
        self.sanitized_map = {}
        self._check_unnamed_columns()
        self._check_duplicates()

    def _check_unnamed_columns(self):
        count = 0
        for idx, col in enumerate(self.source_names):
            # allow only a single empty column name
            if col == b"" or col == "":
                count += 1
                if count > 1:
                    raise UnnamedColumnError(position=idx + 1)
            elif isinstance(col, str) and col.isspace():
                # don't allow columns with only spaces
                raise ColumnOnlyContainsSpacesError(position=idx + 1)

    def _check_duplicates(self):
        seen = {}
        for idx, col in enumerate(self.source_names):
            sanitized = sanitize_name(col)
            if sanitized in seen:
                raise AmbiguousColumnNameError(name=col, previous=seen[sanitized])
            seen[sanitized] = col
            self.sanitized_map[col] = sanitized

        if "" in self.sanitized_map.keys():
            pos = self.source_names.index("")
            renamed_col = "Unnamed: {}".format(pos)
            if renamed_col in self.sanitized_map:
                raise UnnamedColumnError(position=pos + 1)
            self.sanitized_map[""] = renamed_col

    def get(self, original_column: str):
        return self.sanitized_map.get(original_column)

    def get_mapping(self) -> dict:
        return self.sanitized_map
