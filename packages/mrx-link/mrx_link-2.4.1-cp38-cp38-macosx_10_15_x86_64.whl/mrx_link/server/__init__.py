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
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join
from mrx_link_core.common.info import APP_NAME

from mrx_link.common import KERNEL_ID_REGEX

from .handlers.cache import (
    CACHE_HANDLER_INFO,
    CacheExportHandler,
    CacheImportHandler,
    ClearCacheDirHandler,
)
from .handlers.dag_handler import DAGHandler
from .handlers.dataset_diff_handler import DataSetDiffHandler, SingleDataSetDiffHandler
from .handlers.info import CacheInfoHandler, MRXLinkInfoHandler, ServerAppInfoHandler
from .handlers.pipeline_export import (
    KfpPipelineExportHandler,
    MRXLinkPipelineExportHandler,
    PyPipelineExportHandler,
)
from .handlers.pipeline_import import (
    KfpPipelineImportHandler,
    MRXLinkPipelineImportHandler,
)
from .handlers.runway import (
    MRXRunwayInfoHandler,
    MRXRunwayModelRegistryHandler,
    MRXRunwayPipelineExportHandler,
    MRXRunwayProjectHandler,
    MRXRunwayUpdateHandler,
    MRXRunwayUserInfoHandler,
    MRXRunwayUserLoginHandler,
    MRXRunwayUserLogoutHandler,
    MRXRunwayWorkspaceHandler,
)
from .handlers.runway.dataset_info_handler import (
    MRXRunwayDatasetHandler,
    MRXRunwayDatasetVersionHandler,
    MRXRunwayImportCodeSnippetHandler,
    MRXRunwayTabularCodeSnippetHandler,
)
from .handlers.utils import PathCheckHandler
from .handlers.ws_handler import MRXLinkWebSocketHandler


def setup_application(web_app: ServerApp) -> None:
    """setup whole handlers to web Application

    Args:
        web_app (ServerApp): Jupyter Server Application
    """
    # pylint: disable=too-many-locals
    # origin web_app.settings["serverapp"].max_body_size = 512 * 1024 * 1024 = 512MB
    # we can check this info on jupyter_server.serverapp.ServerApp
    if "serverapp" in web_app.settings:
        CACHE_HANDLER_INFO["cache_buffer_size"] = web_app.settings["serverapp"].max_body_size
        web_app.settings["serverapp"].max_body_size = 20 * web_app.settings["serverapp"].max_body_size

    host_pattern: str = ".*$"
    base_url = web_app.settings["base_url"]

    dag_route = url_path_join(base_url, APP_NAME, "dag", "kernels", KERNEL_ID_REGEX)
    ws_route = url_path_join(base_url, APP_NAME, "ws")

    kfp_pipeline_export_route = url_path_join(base_url, APP_NAME, "pipeline", "export")
    link_pipeline_export_route = url_path_join(base_url, APP_NAME, "link-pipeline", "export")
    py_pipeline_export_route = url_path_join(base_url, APP_NAME, "python", "export")
    runway_pipeline_export_route = url_path_join(base_url, APP_NAME, "runway", "pipeline", "export")

    kfp_pipeline_import_route = url_path_join(base_url, APP_NAME, "pipeline", "import")
    link_pipeline_import_route = url_path_join(base_url, APP_NAME, "link-pipeline", "import")

    cache_export_route = url_path_join(base_url, APP_NAME, "cache", "export")
    cache_import_route = url_path_join(base_url, APP_NAME, "cache", "import")
    cache_clear_route = url_path_join(base_url, APP_NAME, "cache", "clear")

    info_extension_route = url_path_join(base_url, APP_NAME, "info", "extension")
    info_serverapp_route = url_path_join(base_url, APP_NAME, "info", "serverapp")
    info_cache_route = url_path_join(base_url, APP_NAME, "info", "cache")
    info_runway_route = url_path_join(base_url, APP_NAME, "runway", "info")

    runway_user_route = url_path_join(base_url, APP_NAME, "runway", "user")
    runway_user_login_route = url_path_join(base_url, APP_NAME, "runway", "user", "login")
    runway_user_logout_route = url_path_join(base_url, APP_NAME, "runway", "user", "logout")
    runway_project_route = url_path_join(base_url, APP_NAME, "runway", "projects")
    runway_workspace_route = url_path_join(base_url, APP_NAME, "runway", "workspaces")
    runway_model_registry_route = url_path_join(base_url, APP_NAME, "runway", "model_registries")
    runway_dataset_route = url_path_join(base_url, APP_NAME, "runway", "datasets")
    runway_dataset_version_route = url_path_join(base_url, APP_NAME, "runway", "datasets", "versions")
    runway_tabular_code_snippet_route = url_path_join(
        base_url,
        APP_NAME,
        "runway",
        "datasets",
        "tabular",
        "code-snippet",
    )
    runway_import_code_snippet_route = url_path_join(
        base_url,
        APP_NAME,
        "runway",
        "datasets",
        "code-snippet",
    )

    path_check_route = url_path_join(base_url, APP_NAME, "runway", "path_check")
    dataset_diff_route = url_path_join(base_url, APP_NAME, "runway", "dataset", "diff")
    single_dataset_diff_route = url_path_join(base_url, APP_NAME, "runway", "dataset", "single", "diff")
    update_route = url_path_join(base_url, APP_NAME, "runway", "update")

    handlers = [
        (dag_route, DAGHandler),
        (ws_route, MRXLinkWebSocketHandler),
        (kfp_pipeline_export_route, MRXRunwayPipelineExportHandler),
        (link_pipeline_export_route, MRXLinkPipelineExportHandler),
        (py_pipeline_export_route, PyPipelineExportHandler),
        (runway_pipeline_export_route, MRXRunwayPipelineExportHandler),
        (kfp_pipeline_import_route, KfpPipelineImportHandler),
        (link_pipeline_import_route, MRXLinkPipelineImportHandler),
        (cache_export_route, CacheExportHandler),
        (cache_import_route, CacheImportHandler),
        (cache_clear_route, ClearCacheDirHandler),
        (info_extension_route, MRXLinkInfoHandler),
        (info_serverapp_route, ServerAppInfoHandler),
        (info_cache_route, CacheInfoHandler),
        (info_runway_route, MRXRunwayInfoHandler),
        (runway_user_route, MRXRunwayUserInfoHandler),
        (runway_user_login_route, MRXRunwayUserLoginHandler),
        (runway_user_logout_route, MRXRunwayUserLogoutHandler),
        (runway_project_route, MRXRunwayProjectHandler),
        (runway_workspace_route, MRXRunwayWorkspaceHandler),
        (runway_model_registry_route, MRXRunwayModelRegistryHandler),
        (runway_dataset_route, MRXRunwayDatasetHandler),
        (runway_dataset_version_route, MRXRunwayDatasetVersionHandler),
        (runway_tabular_code_snippet_route, MRXRunwayTabularCodeSnippetHandler),
        (runway_import_code_snippet_route, MRXRunwayImportCodeSnippetHandler),
        (path_check_route, PathCheckHandler),
        (dataset_diff_route, DataSetDiffHandler),
        (single_dataset_diff_route, SingleDataSetDiffHandler),
        (update_route, MRXRunwayUpdateHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)


__all__ = ["setup_application"]
