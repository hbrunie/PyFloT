from __future__ import annotations

import sys
import warnings
import argparse
import termcolor

from typing import TYPE_CHECKING

from pyflot.configuration import ConfigHandler


if TYPE_CHECKING:
    pass

class PyflotMain:
    """This class is the entry point for running the DSL on a solver."""

    def __init__(self):
        self.config_handler = ConfigHandler()
        self.arg_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    def _extract_remaining_args_and_config_files(self, args: list[str]) -> tuple[list[str], list[str]]:
        """TODO: refactor this, cleanup the list splitting awfulness
        Returns the args updated, and the list of config_files
        """
        for i, arg in enumerate(args):
            if not arg.startswith("--config"):
                continue
            # Setup a temporary, limited argparser for the --config file.json [other_file.json] part
            tmp_arg_parser = argparse.ArgumentParser()
            tmp_arg_parser.add_argument(
                "--config", type=str, nargs="+", action="append", help="JSON configuration file to load"
            )
            tmp_arg_parser.add_argument("-v", "--verbose", help="View each configuration file")

            # Split the cmd line arguments between the config part and the other options
            config_args: list[str] = [arg]
            for j, other_arg in enumerate(args[i + 1 :]):
                if other_arg.startswith("-"):
                    break
                config_args.append(other_arg)

            # Drop the config arguments
            non_config_args = args[:i]
            if len(args) > i + len(config_args) - 1:
                non_config_args += args[i + len(config_args) :]

            args = non_config_args
            # Add the required --connector arg and value
            args.extend(["--connector", self.config_handler.poseidon_config.connector])

            # Parse the config part and update all Poseidon configurations using the JSON config file
            options = tmp_arg_parser.parse_args(config_args)
            config_arg_values = options.config
            config_files = []
            for sublist in config_arg_values:
                config_files.extend(sublist)
            return args, config_files
        assert False, "Must not get here"

    def _update_from_args(self, args: list[str]):
        # Print help if requested, don't use argparse here as it includes a default help
        if "--help" in args or "-h" in args:
            self.help(args)

        use_defaults: bool = "--config" not in " ".join(args)
        # Either parse the cmd line arguments
        if use_defaults:
            # First setup the connector and its config
            connector_name = self.config_handler.get_connector_name(args)
            assert isinstance(connector_name, str)
            self.config_handler.connector_config: ConnectorConfig_Generic = (
                self.config_handler.setup_config_from_prog_args(args, self.arg_parser, connector_name)
            )
            self.config_handler.update_all_configs(args, self.arg_parser)
            self.connector = self.config_handler.build_connector_from_name_and_config(
                self.config_handler.connector_config, connector_name
            )
        # or load the config from a file
        else:
            args, config_files = self._extract_remaining_args_and_config_files(args)
            self.connector = self.config_handler.build_connector_from_json_files(config_files, self.arg_parser, args)

        if self.config.view_config:
            print(self.config_handler.view_options())

        if self.config.dump_config_to_file != "":
            print(f"Dumping configuration to file: {self.config.dump_config_to_file}")
            # Avoid dumping the config file name, so that it does not get overwritten when loading it
            config_file = self.config.dump_config_to_file
            self.config.dump_config_to_file = ""
            self.config_handler.to_json_file(config_file)

    def run_from_args(self, args: list[str]):
        """Run Poseidon from Command Line.
        Either user provides a config path to a json config file.
        Or it does not.

        :param args: _description_
        """
        self._update_from_args(args)
        self.run()

    def dump_warnings(self, all_warnings: list[Warning]):
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
                w: Warning
                filename = w.filename
                lineno = w.lineno

                termcolor.cprint(f"{filename}:{lineno}: {termcolor.colored(w.message, 'yellow')}")

        print("*" * 80)

    def help(self, prog_args: list[str]):
        """Print help, including all configuration options.

        :param prog_args: List of arguments that were passed to the program.
        """
        self.config_handler.print_help(prog_args)

