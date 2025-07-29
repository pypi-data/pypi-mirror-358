#
#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2024] MakinaRocks Co., Ltd.
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
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from mrx_link_core.callbacks import MRXLinkPipelineCallback
from mrx_link_core.common.mixins import LoggingMixin
from mrx_link_core.pipeline import MRXLinkPipeline

from mrx_link.common import get_ipykernel_id

from . import commands


@magics_class
class MRXLinkMagics(LoggingMixin, Magics):
    """A class to manage canvas magic commands"""

    # pylint: disable=too-many-public-methods

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(LoggingMixin, self).__init__(*args, **kwargs)  # pylint: disable=bad-super-call
        super(Magics, self).__init__(**kwargs)

        ipykernel_id: str = get_ipykernel_id(ipython_shell=self.shell)
        if not ipykernel_id:
            raise RuntimeError("MRXLinkMagics is only valid in the InteractiveShell")

        self.link_ipykernel_id: str = ipykernel_id
        self.link_pipeline_callback: Optional[MRXLinkPipelineCallback] = None
        self.link_pipeline: Optional[MRXLinkPipeline] = None

    @magic_arguments()
    @argument("var", default=None, help="Configuration variable")
    @argument("value", default=None, help="Configuration set value")
    @line_magic
    def mrxlink_set_config(self, line: str) -> None:
        """Set configuration variable"""
        args = parse_argstring(self.mrxlink_set_config, line)
        commands.mrxlink_set_config(link_magic=self, args=args)

    @magic_arguments()
    @argument("dag", help="name of the symbol that references the MRXLinkDag object")
    @line_magic
    def mrxlink_reference_dag(self, line: str) -> None:
        """Return the MRXLinkDag object."""
        args = parse_argstring(self.mrxlink_reference_dag, line)
        commands.mrxlink_reference_dag(link_magic=self, args=args)

    @magic_arguments()
    @argument("-b", "--base_url", default="http://localhost:8888", help="Base URL for server REST API")
    @argument("-h", "--header", default="", help="Header value to communicate with Jupyter server")
    @argument("-c", "--cookie", default="", help="Cookie value to communicate with Jupyter server")
    @line_magic
    def mrxlink_init_dag(self, line: str) -> None:
        """Return the MRXLinkDag object."""
        args = parse_argstring(self.mrxlink_init_dag, line)
        commands.mrxlink_init_dag(link_magic=self, args=args)

    @magic_arguments()
    @cell_magic
    def mrxlink_update_dag(self, line: str, cell: str) -> None:
        """Update DAG at once

        Args:
            line (str): magic command and arguments
            cell (str): JSON description of the DAG
        """
        args = parse_argstring(self.mrxlink_update_dag, line)
        args.cell = cell
        commands.mrxlink_update_dag(link_magic=self, args=args)

    @magic_arguments()
    @argument("-i", "--id", required=True, help="The identifier of this cell")
    @argument("-f", "--send-to-front", dest="send_to_front", action="store_true", help="Send captured to front")
    @argument("-o", "--optimize-memory", dest="optimize_memory", action="store_true", help="Optimize in-memory cache")
    @argument("-p", "--parallel", action="store_true", help="Parallel execution")
    @cell_magic
    def mrxlink_execute_component(self, line: str, cell: str) -> Any:
        """Execute component synchronously.

        Args:
            line (str): magic line
            cell (Optional[str], optional): cell contents. Defaults to None.

        Returns:
            Any: returns last evaluated expression if any, otherwise None.
        """
        args = parse_argstring(self.mrxlink_execute_component, line)
        args.cell = cell
        return commands.mrxlink_execute_component(link_magic=self, args=args)

    @magic_arguments()
    @argument("-i", "--ids", type=lambda s: list(s.split(",")), required=True, help="The identifiers of cells")
    @argument("-f", "--send-to-front", dest="send_to_front", action="store_true", help="Send captured to front")
    @argument("-o", "--optimize-memory", dest="optimize_memory", action="store_true", help="Optimize in-memory cache")
    @argument("-p", "--parallel", action="store_true", help="Parallel execution")
    @line_magic
    def mrxlink_execute_components(self, line: str) -> Any:
        """Execute component synchronously.

        Args:
            line (str): magic line
            cell (Optional[str], optional): cell contents. Defaults to None.

        Returns:
            Any: returns last evaluated expression if any, otherwise None.
        """
        args = parse_argstring(self.mrxlink_execute_components, line)
        return commands.mrxlink_execute_components(link_magic=self, args=args)

    @magic_arguments()
    @argument("level", default="INFO", help="root logging handler's logging level")
    @line_magic
    def mrxlink_logging_level(self, line: str) -> None:
        """set root logging handler's logging level

        Args:
            line (str): magic command and argument
        """
        args = parse_argstring(self.mrxlink_logging_level, line)
        commands.mrxlink_logging_level(link_magic=self, args=args)

    @magic_arguments()
    @argument("-s", "--set", nargs="?", const="", default=None, help="Set DAG cache directory")
    @line_magic
    def mrxlink_cache_dir(self, line: str) -> str:
        """Set/get the cache directory for DAG

        Args:
            line (str): magic command and argument
        """
        args = parse_argstring(self.mrxlink_cache_dir, line)
        return commands.mrxlink_cache_dir(link_magic=self, args=args)

    @magic_arguments()
    @argument("-i", "--id", required=True, help="The identifier of selected cell to set diskcache option")
    @argument("-u", "--use", action="store_true", help="The option to use diskcache")
    @line_magic
    def mrxlink_use_diskcache(self, line: str) -> None:
        """Set use_diskcache option for a component. it can affect to the related components

        Args:
            line (str): magic command and argument
        """
        args = parse_argstring(self.mrxlink_use_diskcache, line)
        commands.mrxlink_use_diskcache(link_magic=self, args=args)

    @magic_arguments()
    @argument("-i", "--id", required=True, help="The identifier of selected cell")
    @line_magic
    def mrxlink_clear_cache(self, line: str) -> None:
        """Clear in-memory cache and diskcache of child nodes, including itself."""
        args = parse_argstring(self.mrxlink_clear_cache, line)
        commands.mrxlink_clear_cache(link_magic=self, args=args)

    @magic_arguments()
    @line_magic
    def mrxlink_clear_all_cache(self, line: str) -> None:
        """Clear in-memory cache and diskcache of all nodes."""
        args = parse_argstring(self.mrxlink_clear_all_cache, line)
        commands.mrxlink_clear_all_cache(link_magic=self, args=args)

    @magic_arguments()
    @argument("-n", "--no-reply", action="store_true", help="No reply to Websocket channel")
    @cell_magic
    # pylint: disable=unused-argument
    def mrxlink_set_parameters(self, line: str, cell: str) -> None:
        """Set parameters for Link DAG and send updated parameters info to the clients.

        Args:
            line (str): magic command and argument
            cell (Optional[str], optional): cell contents. Defaults to None. It includes parameter list
        """
        args: SimpleNamespace = parse_argstring(self.mrxlink_set_parameters, line)
        args.cell = cell
        commands.mrxlink_set_parameters(link_magic=self, args=args)

    @magic_arguments()
    @argument("filename", default="", help="file logging handler's logging filename")
    @line_magic
    def mrxlink_logging_filename(self, line: str) -> None:
        """Set file logging handler's logging filename

        Args:
            line (str): magic command and argument
        """
        args = parse_argstring(self.mrxlink_logging_filename, line)
        commands.mrxlink_logging_filename(link_magic=self, args=args)

    @magic_arguments()
    @line_magic
    def mrxlink_import_hpo_dependencies(self, line: str) -> bool:
        """Import dependencies related to Link HPO.

        Args:
            line (str): magic command and argument
        """
        args = parse_argstring(self.mrxlink_import_hpo_dependencies, line)
        return commands.mrxlink_import_hpo_dependencies(link_magic=self, args=args)

    @magic_arguments()
    @argument(
        "-i",
        "--id",
        required=True,
        help="The id of the component whose last output is to be set as the target value to be optimized",
    )
    @argument("-n", "--n_trials", type=int, required=True, help="Number of trial to optimize")
    @argument(
        "-o",
        "--opt_method",
        required=True,
        help="Optimization method to optimize (ex. GridSearch, RandomSearch, TPESearch)",
    )
    @argument(
        "-m",
        "--directions",
        nargs="+",
        type=int,
        required=True,
        help="Optimization directions of each objective value. Manimize when 0",
    )
    @argument("-e", "--early_stopping_rounds", type=int, help="Early stopping rounds in optimizing if it exists")
    @cell_magic
    def mrxlink_optimize_parameters(self, line: str, cell: str) -> None:
        """Tune parameters.

        Args:
            line (str): magic command and argument
            cell (Optional[str], optional): cell contents. Defaults to None. It includes parameter info to optimize
            --------------------------
            cell PROTOCOL
            --------------------------
            {
                "parameter_1": {
                    "type": <str> (ex. "int", "float"),
                    "distribution": <str> (ex. "uniform", "loguniform", "int", ...),
                    "low": <str> (ex. "-5", "3.1415"),
                    "high": <str> (ex. "-5", "3.1415"),
                },
                "parameter_2": {
                    "type": <str> (ex. "int", "float"),
                    "distribution": <str> (ex. "uniform", "loguniform", "int", ...),
                    "low": <str> (ex. "-5", "3.1415"),
                    "high": <str> (ex. "-5", "3.1415"),
                },
            }
            or
            {
                "parameter_1": {
                    "type": <str> (ex. "int", "float"),
                    "interval": <str> (ex. "1", "0.1"),
                    "low": <str> (ex. "-5", "3.1415"),
                    "high": <str> (ex. "-5", "3.1415"),
                },
                "parameter_2": {
                    "type": <str> (ex. "int", "float"),
                    "interval": <str> (ex. "1", "0.1"),
                    "low": <str> (ex. "-5", "3.1415"),
                    "high": <str> (ex. "-5", "3.1415"),
                },
            }

        """
        args: SimpleNamespace = parse_argstring(self.mrxlink_optimize_parameters, line)
        args.cell = cell
        commands.mrxlink_optimize_parameters(link_magic=self, args=args)

    @magic_arguments()
    @line_magic
    @argument("-i", "--id", required=True, help="The identifier of selected cell")
    def mrxlink_get_target_exp_in_last_exp(self, line: str) -> str:
        """Get last expression and target value expressions in the component"""
        args = parse_argstring(self.mrxlink_get_target_exp_in_last_exp, line)
        return commands.mrxlink_get_target_exp_in_last_exp(link_magic=self, args=args)

    @magic_arguments()
    @argument("-d", "--backend", required=True, help="The result store backend URL.")
    @argument("-m", "--broker", required=True, help="URL of the default broker used.")
    @line_magic
    def mrxlink_remote_ping(self, line: str) -> str:
        """Ping the remote server to see if the connection is OK."""
        args = parse_argstring(self.mrxlink_remote_ping, line)
        return commands.mrxlink_remote_ping(link_magic=self, args=args)

    @magic_arguments()
    @line_magic
    def mrxlink_remote_load_config(self, line: str) -> str:
        """Load remote environment config from file."""
        args = parse_argstring(self.mrxlink_remote_load_config, line)
        return commands.mrxlink_remote_load_config(link_magic=self, args=args)

    @magic_arguments()
    @argument("-n", "--name", required=True, help="Alias name")
    @argument("-d", "--backend", required=True, help="The result store backend URL.")
    @argument("-m", "--broker", required=True, help="URL of the default broker used.")
    @line_magic
    def mrxlink_remote_save_config(self, line: str) -> str:
        """Save remote environment config to file."""
        args = parse_argstring(self.mrxlink_remote_save_config, line)
        return commands.mrxlink_remote_save_config(link_magic=self, args=args)

    @magic_arguments()
    @argument("-n", "--name", required=True, help="Alias name")
    @argument("-d", "--backend", required=True, help="The result store backend URL.")
    @argument("-m", "--broker", required=True, help="URL of the default broker used.")
    @argument("-u", "--new_name", default=None, required=False, help="New alias name")
    @line_magic
    def mrxlink_remote_update_config(self, line: str) -> str:
        """Update remote environment config."""
        args = parse_argstring(self.mrxlink_remote_update_config, line)
        return commands.mrxlink_remote_update_config(link_magic=self, args=args)

    @magic_arguments()
    @argument("-n", "--name", required=True, help="Alias name")
    @line_magic
    def mrxlink_remote_remove_config(self, line: str) -> str:
        """Remove remote environment config from file."""
        args = parse_argstring(self.mrxlink_remote_remove_config, line)
        return commands.mrxlink_remote_remove_config(link_magic=self, args=args)

    @magic_arguments()
    @argument("-n", "--name", required=True, help="Alias name")
    @argument("-i", "--component_id", required=True, help="The identifier of selected cell")
    @line_magic
    def mrxlink_remote_add_component(self, line: str) -> str:
        """Add component to remote environment config."""
        args = parse_argstring(self.mrxlink_remote_add_component, line)
        return commands.mrxlink_remote_add_component(link_magic=self, args=args)

    @magic_arguments()
    @argument("-n", "--name", required=True, help="Alias name")
    @argument("-i", "--component_id", required=True, help="The identifier of selected cell")
    @line_magic
    def mrxlink_remote_remove_component(self, line: str) -> str:
        """Remove component from remote environment config."""
        args = parse_argstring(self.mrxlink_remote_remove_component, line)
        return commands.mrxlink_remote_remove_component(link_magic=self, args=args)

    @magic_arguments()
    @argument("-r", "--is_runway", action="store_true", help="Is for runway")
    @line_magic
    def mrxlink_get_python_path(self, line: str) -> List[str]:
        """Return the PTHONPATH list."""
        args = parse_argstring(self.mrxlink_get_python_path, line)
        return commands.mrxlink_get_python_path(args=args)
