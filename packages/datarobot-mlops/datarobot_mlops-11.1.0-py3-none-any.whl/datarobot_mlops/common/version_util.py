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


# Note: keep this class in sync with it's cousin class in
#  common/src/main/java/com/datarobot/mlops/common/client/DataRobotAppVersion.java
class DataRobotAppVersion:
    def __init__(self, string_version=None, major=None, minor=None, patch=None, suffix=None):
        if string_version is not None:
            # Support semver, (i.e. 1.10.2-beta.1) where `-` is used to split the main part of the
            # version from a suffix modifier. This class only cares about the left-hand side.
            semver = string_version.split("-", 1)
            versions = semver[0].split(".")
            if len(versions) < 3:
                raise ValueError(
                    'DataRobot App version in string form should have syntax "x.y.z" '
                    "where x, y and z are integers"
                )
            major = versions[0]
            minor = versions[1]
            patch = versions[2]
            if len(semver) == 2:
                suffix = semver[1]
        elif major is None or minor is None or patch is None:
            raise ValueError(
                'DataRobot App version needs to be specified either as a string "x.y.z" '
                "or integer values for major, minor, patch"
            )

        self._major = int(major)
        self._minor = int(minor)
        self._patch = int(patch)
        self._suffix = suffix

    def __str__(self):
        # TODO: we may want to expose the suffix eventually but for now to keep APIs consistent
        # we will just ignore the suffix.
        return f"{self._major}.{self._minor}.{self._patch}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self._major == other.major
                and self._minor == other.minor
                and self._patch == other.patch
            )
        elif isinstance(other, str):
            return self == type(self)(string_version=other)
        else:
            raise TypeError(f"Cannot compare {self.__class__} to {other.__class__}")

    def __hash__(self):
        return hash((self._major, self._minor, self._patch))

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    @property
    def suffix(self):
        return self._suffix

    def is_newer_or_equal(self, datarobot_app_compare_version):
        """
        Checks if "this" version is newer or equal to the version input as an argument
        :param datarobot_app_compare_version:
        :return:
        """
        # TODO: add support for version suffix according to SemVer (https://semver.org)
        # but this is a little involved and not needed yet -- suffix is ignored for
        # version ordering currently.
        if self._major > datarobot_app_compare_version.major:
            return True
        if self._major < datarobot_app_compare_version.major:
            return False
        # At this point major versions are equal
        if self._minor > datarobot_app_compare_version.minor:
            return True
        if self._minor < datarobot_app_compare_version.minor:
            return False
        # At this point major and minor versions are equal
        return self._patch >= datarobot_app_compare_version.patch
