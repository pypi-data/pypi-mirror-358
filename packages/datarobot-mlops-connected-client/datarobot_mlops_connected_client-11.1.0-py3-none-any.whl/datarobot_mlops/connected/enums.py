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

from enum import Enum


class DatasetSourceType(Enum):
    """
    Dataset association type.
    Used to mark uploaded dataset as TRAINING or SCORING
    for a deployment within DataRobot MLOps.
    """

    TRAINING = "training"
    SCORING = "scoring"


class ExitCode(Enum):
    """
    Custom exit codes to surface additional information about errors.
    """

    OK = 0
    DEFAULT = 1
    INVALID_CLI_INPUT = 2
    DR_CONNECTED = 3
    DR_NOT_FOUND = 4
    INTERNAL_SERVER = 5
    UNSPECIFIED = 6
    FILE_NOT_FOUND = 7
