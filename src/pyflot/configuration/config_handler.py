import os
import sys
import argparse
import json
import re
import termcolor
from typing import Optional
from configuration import ConfigProfile, ConfigAnalysis

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pyflot.configuration.config_base import ConfigBase

class ConfigHandler:
    """Class to hold all configurations for Poseidon."""

    def __init__(
        self,
        config_analysis: Optional[ConfigAnalysis] = None,
        config_profile: Optional[ConfigProfile] = None,
        # csv_config: Optional[PyflotConfigMergeCsvIntoTrace] = None,
        only_profile: bool = True,
    ) -> None:
        self.analysis_config = config_analysis or ConfigAnalysis()
        self.profile_config = config_profile or ConfigProfile()
        # self.csv_config = csv_config or PyflotConfigMergeCsvIntoTrace()
        self._all_configurations: list[ConfigBase] = [self.profile_config, self.analysis_config]  # , self.csv_config]
        self.only_profile = only_profile

        # Autodetect path to Poseidon based on this file name
        binary_abspath = os.path.dirname(__file__)
        binary_abspath = os.path.join(binary_abspath, "../../run_pyflot.py")
        binary_abspath = os.path.abspath(binary_abspath)
        # Path to executable of Poseidon
        self.pyflot_binary= binary_abspath

    def update_from_args(
        self,
        args: str,
        view_config: bool = False,
        dump_config_to_file: str = "",
    ):
        use_config_file: bool = "--config" in " ".join(args)
        arg_parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        if use_config_file:
            args, config_file = self._extract_remaining_args_and_config_files(args)
            self.update_all_configs_from_json_and_args(config_file, arg_parser, args)
        else:
            self.update_all_configs_from_args(args, arg_parser)
            self.update_all_configs_from_args(args, arg_parser)

        if view_config:
            print(self.view_options())

        if dump_config_to_file != "":
            print(f"Dumping configuration to file: {dump_config_to_file}")
            self.to_json_file(dump_config_to_file)

    def update_all_configs_from_json_and_args(self, file_path: str, arg_parser: argparse.ArgumentParser, prog_args) -> None:
        """
        From a given config file (JSON)
        * update all the configs from the JSON file extracted dict

        """

        options_dict = self._get_options_dict(file_path)
        self._setup_config_from_argparser_and_dict(options_dict, arg_parser)
        self.update_all_configs_from_args(prog_args, arg_parser)

    def get_connector_name(self, args: list[str]):
        """FIXME: make it robust

        :param args: _description_
        :return: _description_
        """
        ## find --connector
        list_with_connector: list[str] = [c for c in args if "--connector" in c]
        assert len(list_with_connector) == 1
        connector_string: str = list_with_connector[0]
        if "=" in connector_string:
            list_with_connector_and_name: list[str] = connector_string.split("=")
            assert len(list_with_connector_and_name) == 2
            return list_with_connector_and_name[1]
        else:
            assert connector_string == "--connector"
            return args[args.index("--connector") + 1]

    def _setup_argparser_for_all_configs(
        self, arg_parser: argparse.ArgumentParser, use_defaults: bool
    ) -> None:
        for config in self._all_configurations:
            config.setup_arg_parser(arg_parser, use_defaults=use_defaults)

    def _setup_config_from_argparser_and_dict(
        self, args_dict: dict, arg_parser: argparse.ArgumentParser
    ) ->None:
        """Setup the connector configuration.

        :param arg_parser: argparse.ArgumentParser object
        """
        self._setup_argparser_for_all_configs(
            arg_parser, use_defaults=True
        )
        for config in self._all_configurations:
            config.update_from_dict(args_dict)

    def setup_config_from_prog_args(
        self, prog_args: list[str], arg_parser: argparse.ArgumentParser
    ) ->None:
        """Setup the connector configuration.

        :param arg_parser: argparse.ArgumentParser object
        """
        self._setup_argparser_for_all_configs(
            arg_parser, use_defaults=False
        )
        args_namespace = arg_parser.parse_args(prog_args)
        args_dict = vars(args_namespace)
        for config in self._all_configurations:
            config.update_config(args_dict)

    def _wrap_strings_list(self, columns_of_strs: list[list[str]], line_length: int):
        """Wrap columns of list of strings into list of strings.

        :param columns_of_strs: _description_
        :param line_length: _description_
        """
        def no_color(line):
            ansi_regex = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
            return ansi_regex.sub("", line)
        max_left_len = max([len(no_color(row[0])) for row in columns_of_strs if len(row) == 2])
        wrap_right_len = line_length - max_left_len - 2

        strs: list[str] = []
        for row in columns_of_strs:
            if len(row) == 0:
                strs.append("")
                continue
            elif len(row) == 1:
                operations_offset = "      "
                for i in range(0, len(no_color(row[0])), line_length - len(operations_offset)):
                    strs.append(operations_offset + row[0][i : i + line_length])
                continue
            elif len(row) == 2:
                left, right = row
                for i in range(0, len(right), wrap_right_len):
                    right_slice = right[i : i + wrap_right_len]
                    if i == 0:
                        strs.append(left + " " * (max_left_len - len(no_color(left))) + "  " + right_slice)
                    else:
                        strs.append(" " * max_left_len + "  " + right_slice)
            else:
                raise ValueError("Invalid row length")
        return strs

    def print_help(self, prog_args: list[str], line_length: int = 127) -> None:
        """Print help for all configurations."""

        columns_of_strs: list[list[str]] = []
        for config in self._all_configurations:
            columns_of_strs.extend(config.view_help(prog_args=prog_args))
        strs = self._wrap_strings_list(columns_of_strs, line_length)

        print(termcolor.colored("Pyflot: Floating-Point precision Tuner", attrs=["bold"]))
        print("Usage: ./run_pyflot.py --options")
        print("\n".join(strs))
        sys.exit(0)

    def update_all_configs_from_args(self, prog_args: list[str], arg_parser: argparse.ArgumentParser) -> None:
        """Update all configurations other than the Connector_Config using program arguments.
        NOTE: this must be done before the Connector is instantiated because it will
        creates DataFlowGraph based on the data_flow_graph_config updated here.

        :param prog_args: program arguments
        :param arg_parser: argparse.ArgumentParser object
        """
        # Final processing of program arguments
        args_namespace = arg_parser.parse_args(prog_args)
        args_dict = vars(args_namespace)
        # Update configs
        for config in self._all_configurations:
            config.update_config(args_dict)

    def get_command_line_args(self) -> str:
        """Used to generate the CMake PYFLOT_COMMAND environment variable.
        :return: whitespace separated string of command line arguments
        """
        retstr_list = []
        for config in self._all_configurations:
            retstr_list.append(config.get_command_line_args())

        retstr = ""
        retstr += self.pyflot_binary
        retstr += " "
        retstr += " ".join(retstr_list)

        return retstr

    def view_options(self, output_prefix: str = "") -> str:
        """View all options.
        :param output_prefix: prefix to prepend to each line
        :return: string representation of all options
        """
        retstr: str = ""

        retstr += f"{output_prefix}- Config options are:\n"

        output_prefix += "  "
        # Path to executable of Poseidon
        for config in self._all_configurations:
            retstr += config.view_options(output_prefix)

        return retstr

    def to_dict(self, include_default_values: bool = True) -> dict[str, str]:
        """Convert all configurations to a dictionary.

        :param include_default_values: include default values

        :return: dictionary of all configurations
        """
        ret_dict: dict[str, str] = {}
        for config in self._all_configurations:
            ret_dict.update(config.to_dict(include_default_values))
        return ret_dict

    def to_json(self, include_default_values: bool = True) -> str:
        """Convert all configurations to a JSON string.

        :param include_default_values: include default values

        :return: JSON string of all configurations
        """
        return json.dumps(self.to_dict(include_default_values), indent=4)

    def to_json_file(self, file_path: str, include_default_values: bool = True) -> None:
        """Write all configurations to a JSON file.

        :param file_path: path to JSON file
        :param include_default_values: include default values
        """
        with open(file_path, "w") as f:
            f.write(self.to_json(include_default_values))

    def _get_options_dict(self, file_path) -> dict:
        with open(file_path, mode="r", encoding="utf-8") as f:
            options_dict = json.loads(f.read())
        return options_dict

    def update_config_from_dict(self, input_dict: dict[str, str], error_if_required_option_missing: bool = True) -> None:
        """Update all configurations from a dictionary.

        :param input_dict: dictionary of configurations
        :param error_if_required_option_missing: error if required option is missing

        raises ValueError: if 'connector' is missing from input_dict
        """
        for config in self._all_configurations:
            config.update_from_dict(input_dict, error_if_required_option_missing)

    def update_from_json(self, input_json: str, error_if_required_option_missing: bool = True) -> None:
        """Update all configurations from a JSON string.

        :param input_json: JSON string of configurations
        :param error_if_required_option_missing: error if required option is missing
        """
        self.update_config_from_dict(json.loads(input_json), error_if_required_option_missing)

    def update_from_json_file(self, file_path: str, error_if_required_option_missing: bool = True) -> None:
        """Update all configurations from a JSON file.

        :param file_path: path to JSON file
        :param error_if_required_option_missing: error if required option is missing
        """
        with open(file_path, "r") as f:
            self.update_from_json(f.read(), error_if_required_option_missing)

    def _extract_remaining_args_and_config_files(self, args: list[str]) -> tuple[list[str], str]:
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

            # Parse the config part and update all Poseidon configurations using the JSON config file
            options = tmp_arg_parser.parse_args(config_args)
            config_arg_values = options.config
            config_files = []
            for sublist in config_arg_values:
                config_files.extend(sublist)
            assert len(config_files) == 1
            return args, config_files[0]
        assert False, "Must not get here"
