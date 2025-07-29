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

import json
from pathlib import Path
from typing import Any

__all__ = ["__version__"]


def _fetchVersion() -> Any:
    # pylint: disable=invalid-name
    HERE = Path(__file__).parent.resolve()
    try:
        pkg_json = json.loads((HERE / "labextension" / "package.json").read_bytes())
        version = pkg_json["version"]
    except:  # pylint: disable=bare-except  # noqa
        version = "2.4.1.dev0"

    return version


__version__ = _fetchVersion()
