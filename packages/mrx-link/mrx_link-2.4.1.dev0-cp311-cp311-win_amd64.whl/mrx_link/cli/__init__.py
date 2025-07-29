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
from typing import Any, Dict

import click

from .commands import convert, run

CONTEXT_SETTINGS: Dict[str, Any] = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
def mrx_link_cli() -> None:
    """
    CLI for mrx-link command.
    Link pipeline on Link ipynb can be utilized through command.
    Currently provides only execution function.
    """


mrx_link_cli.add_command(run)
mrx_link_cli.add_command(convert)
