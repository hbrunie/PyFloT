from __future__ import annotations
from typing import TYPE_CHECKING

import termcolor

from pyflot.configuration import ConfigHandler


if TYPE_CHECKING:
    from warnings import WarningMessage

class PyflotMain:
    """This class is the entry point for running the DSL on a solver."""

    def __init__(self):
        self.config_handler = ConfigHandler()
        self._view_config: bool = False
        self._dump_config_to_file: str = ""

    def _update_from_args(self, args: list[str]):
        # Print help if requested, don't use argparse here as it includes a default help
        if "--help" in args or "-h" in args:
            self.help(args)
        self.config_handler.update_from_args(args, self._view_config, self._dump_config_to_file)

    def run_from_args(self, args: list[str]):
        """Run Poseidon from Command Line.
        Either user provides a config path to a json config file.
        Or it does not.

        :param args: _description_
        """
        self._update_from_args(args)
        self.help(args)
        # self.run()

    def dump_warnings(self, all_warnings: list[WarningMessage]):
        """Dump all warnings that were emitted during the run.

        :param all_warnings: List of all warnings that were emitted during the run.
        """
        print("*" * 80)
        print("The following warnings were emitted during the run:")
        print("*" * 80)

        if len(all_warnings) == 0:
            print("[No warnings]")
        else:
            for w in all_warnings:
                w: WarningMessage
                filename = w.filename
                lineno = w.lineno

                termcolor.cprint(f"{filename}:{lineno}: {termcolor.colored(w.message, 'yellow')}")

        print("*" * 80)

    def help(self, prog_args: list[str]):
        """Print help, including all configuration options.

        :param prog_args: List of arguments that were passed to the program.
        """
        self.config_handler.print_help(prog_args)
