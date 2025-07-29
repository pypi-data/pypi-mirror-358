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
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from mrx_link_core.common.utils import APP_TEMP_DIRECTORY

from . import magic, server
from ._version import __version__

if TYPE_CHECKING:
    from jupyterlab.labapp import LabApp


HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open(encoding="utf-8") as fid:
    data = json.load(fid)

os.makedirs(APP_TEMP_DIRECTORY, exist_ok=True)
os.makedirs(APP_TEMP_DIRECTORY / "pipelines", exist_ok=True)
os.makedirs(APP_TEMP_DIRECTORY / "executors", exist_ok=True)


def _jupyter_labextension_paths() -> List[Dict[str, Any]]:
    return [{"src": "labextension", "dest": data["name"]}]


def _jupyter_server_extension_points() -> List[Dict[str, Any]]:
    return [{"module": "mrx_link"}]


def _load_jupyter_server_extension(server_app: "LabApp") -> None:
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    # pylint: disable=import-outside-toplevel
    from .server import setup_application

    setup_application(server_app.web_app)
    server_app.log.info("Registered MakinaRocks Link extension at URL path /mrx-link")


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension

__all__ = ["common", "magic", "server"]
