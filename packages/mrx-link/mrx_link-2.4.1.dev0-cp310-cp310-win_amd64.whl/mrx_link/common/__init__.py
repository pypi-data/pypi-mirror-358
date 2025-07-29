#
#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2021] MakinaRocks Co., Ltd.
#  All Rights Reserved.
#
#  NOTICE:  All information contained herein is, and remains
#  the property of MakinaRocks Co., Ltd. and its suppliers, if any.
#  The intellectual and technical concepts contained herein are
#  proprietary to MakinaRocks Co., Ltd. and its suppliers and may be
#  covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law. Dissemination
#  of this information or reproduction of this material is
#  strictly forbidden unless prior written permission is obtained
#  from MakinaRocks Co., Ltd.
#
import re
from typing import Optional

from IPython import InteractiveShell

from . import credential, info, singleton

KERNEL_ID_REGEX = r"(?P<kernel_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"


def get_ipykernel_id(ipython_shell: Optional[InteractiveShell]) -> str:
    """extract kernel id w/ regex"""
    if ipython_shell is None:
        return ""

    connection_file: Optional[str] = ipython_shell.config.get("IPKernelApp", {}).get("connection_file", None)
    if connection_file is None:
        return ""

    matched_kernel_id = re.search(KERNEL_ID_REGEX, connection_file)
    if matched_kernel_id is None:
        return ""

    return matched_kernel_id.group()


__all__ = ["credential", "info", "singleton"]
