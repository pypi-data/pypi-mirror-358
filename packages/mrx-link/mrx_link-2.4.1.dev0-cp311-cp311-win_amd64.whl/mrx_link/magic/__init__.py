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
import datetime
import logging
import os
from typing import TYPE_CHECKING

from mrx_link_core.common.utils import APP_TEMP_DIRECTORY

from .magics import MRXLinkMagics

if TYPE_CHECKING:
    from ipykernel.zmqshell import ZMQInteractiveShell


def load_ipython_extension(ipython: "ZMQInteractiveShell") -> None:
    # pylint: disable=missing-function-docstring
    log = logging.getLogger("IPyKernelApp")
    log.setLevel(logging.INFO)

    os.makedirs(str(APP_TEMP_DIRECTORY), exist_ok=True)

    log.info("%s: MRXLink magic extension requested", datetime.datetime.now())
    ipython.register_magics(MRXLinkMagics)
    log.info("%s: Completed MRXLink magic extension loading", datetime.datetime.now())

    log.info("%s: MRXLink converter configuration requested", datetime.datetime.now())
    log.info("%s: Completed MRXLink converter configuration loading", datetime.datetime.now())


__all__ = ["MRXLinkMagics"]
