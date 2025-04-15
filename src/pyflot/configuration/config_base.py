"""Abstract base class for configuration objects. Developed by Julien Remy"""

from typing import Callable, Dict, List, Union, get_args, get_origin
from enum import Enum
from dataclasses import dataclass, _MISSING_TYPE, Field
from abc import ABCMeta
from argparse import _ArgumentGroup, ArgumentParser, ArgumentTypeError
import termcolor


@dataclass
class ConfigBase(metaclass=ABCMeta):
    """Abstract base DATAclass for configuration objects.
    Inherit using @dataclass!
    The fields of the dataclass specify the type, default value, help messages, choices, etc of the options.
    fields starting with '_' are ignored, can be used to specify choices, etc.

    Automatically generates argparse options and Python attributes/fields updates.

    syntax:
    my_field: type = field(default=default_value,
                           metadata={"help": "help message",
                                    ?"choices": ["choice1", "choice2"],
                                    ?"required": True,
                                    ?"nargs": "+",
                                    ?"action": "append",
                                    ?...})
    """

    def dataclass_field_name_to_cmd_line_arg_name(self, field_name: str) -> str:
        """Convert a dataclass field name to a command line argument name.

        :param field_name: the name of the dataclass field.

        :return: the name of the command line argument.
        """
        return f"--{field_name.replace('_', '-')}"

    def resolve_field_type(self, field_type: Union[str, type]) -> type:
        """Resolve the type of a field, which can be a type or a string.

        :param field: the dataclass field.

        :return: the type of the field.
        """
        if isinstance(field_type, str):
            field_type = eval(field_type)

        return field_type

    def dataclass_field_type_to_cmd_line_arg_type(self, field_type: type) -> Union[type, Callable]:
        """Convert a dataclass field type to a command line argument type for argparse.

        :param field_type: the type of the dataclass field.

        :return: the type of the command line argument.
        """

        arg_type = self.resolve_field_type(field_type)
        # Bools args use a special function mapping strings to bools
        if arg_type is bool:
            arg_type = self.bool_arg
        elif get_origin(arg_type) in (list, tuple):
            arg_type = str
        elif issubclass(arg_type, Enum):
            arg_type = str

        if arg_type is _MISSING_TYPE:
            raise Exception("Missing type for field.")

        return arg_type

    def cmd_line_arg_name_to_dataclass_field_name(self, arg_name: str) -> str:
        """Convert a command line argument name to a dataclass field name.

        :param arg_name: the name of the command line argument.

        :return: the name of the dataclass field.
        """
        assert arg_name.startswith("--")
        return arg_name[2:].replace("-", "_")

    def cmd_line_arg_name_to_dataclass_field(self, arg_name: str) -> Field:
        """Convert a command line argument name to a dataclass field.

        :param arg_name: the name of the command line argument.

        :return: the dataclass field.
        """
        field_name = self.cmd_line_arg_name_to_dataclass_field_name(arg_name)
        return self.__dataclass_fields__[field_name]

    def cmd_line_arg_value_to_dataclass_field_value(self, cmd_line_arg_value, field: Field):
        """Convert a command line argument value to a dataclass field value.

        :param cmd_line_arg_value: the value of the command line argument.
        :param field: the dataclass field.

        :return: the value of the dataclass field.
        """
        field_type = self.resolve_field_type(field.type)

        # Special case for list and tuple types, splitting at ',' and dealing with nargs
        if get_origin(field_type) in (list, tuple):
            field_type = get_origin(field_type)
            if isinstance(cmd_line_arg_value, str):
                return field_type(cmd_line_arg_value.replace(" ", "").split(","))
            elif isinstance(cmd_line_arg_value, (tuple, list)):
                modified_list = []
                if field.metadata.get("nargs", None) == "+":
                    for val in cmd_line_arg_value:
                        modified_list.append(" ".join(val))
                    return field_type(modified_list)
                else:
                    return field_type(cmd_line_arg_value)
            else:
                raise Exception(f"Invalid type for list/tuple: {type(cmd_line_arg_value)} on {field.name}")
        elif issubclass(field_type, Enum):
            assert isinstance(cmd_line_arg_value, str)
            return field_type[cmd_line_arg_value]
        else:
            return cmd_line_arg_value

    def get_field_default_value(self, field: Field):
        """Get the default value of a field, dealing with _MISSING_TYPE, None and default factories for mutable fields.

        :param field: the dataclass field.

        :return: the default value of the field.
        """
        arg_default = field.default

        if isinstance(arg_default, Enum):
            arg_default = arg_default.name

        if isinstance(arg_default, (_MISSING_TYPE)) or arg_default is None:
            arg_default = field.default_factory()

        assert arg_default is not _MISSING_TYPE
        assert arg_default is not None

        return arg_default

    def setup_arg_parser(self, arg_parser: ArgumentParser, use_defaults: bool = True) -> _ArgumentGroup:
        """Setup the argument parser for the configuration object.
        Creates an argument group for the configuration object and adds the fields as arguments.

        :param arg_parser: the argument parser.
        :param use_defaults: whether to use the default values for the arguments. Useful for overwriting only certain arguments.

        :return: the argument group for the configuration object.
        """
        # Recurse up the inheritance tree to setup the argument parser for the parent class
        if issubclass(type(super()), Config_Base):
            super().setup_arg_parser(arg_parser)

        # Create a specific argument group for this class
        self.group: _ArgumentGroup = arg_parser.add_argument_group(type(self).__name__)

        # Go through all the fields of the dataclass
        for field in self.__dataclass_fields__.values():
            # Skip fields starting with '_'
            if field.name.startswith("_"):
                continue

            # Create the argument name
            arg_name = self.dataclass_field_name_to_cmd_line_arg_name(field.name)

            # Create the argument dictionary, used in setting group.add_argument
            argument_dict = dict()

            # Set the type of the argument
            arg_type = self.dataclass_field_type_to_cmd_line_arg_type(field.type)
            argument_dict["type"] = arg_type

            # Set the default value of the argument, _MISSING_TYPE is the 'None' default value for fields
            ## if adding required type could be necessary again
            # if use_defaults:
            #    arg_default = self.get_field_default_value(field)
            #    argument_dict["default"] = arg_default

            # Set the choices of the argument
            if issubclass(self.resolve_field_type(field.type), Enum):
                choices = [e.name for e in self.resolve_field_type(field.type)]
            else:
                choices = field.metadata.get("choices", None)
            if choices is not None:
                assert isinstance(choices, (list, tuple))
                argument_dict["choices"] = choices

            # Set the help message of the argument, adding the choices if they exist
            # FIXME: do this or not?
            help_str = field.metadata.get("help", "")
            if choices is not None:
                help_str += f" Choices: {', '.join(choices)}"
            argument_dict["help"] = help_str

            # Set the required flag of the argument
            required = field.metadata.get("required", False)
            if required:
                argument_dict["required"] = required

            # Set the nargs of the argument, used to deal with whitespaces
            nargs = field.metadata.get("nargs", None)
            if nargs is not None:
                argument_dict["nargs"] = nargs

            # Set the action of the argument, used e.g. with dfg-op to specify them one by one
            action = field.metadata.get("action", None)
            if action is not None:
                argument_dict["action"] = action

            # Add the argument to the argparse group
            self.group.add_argument(arg_name, **argument_dict)

        return self.group

    def update_config(self, options: Dict[str, str]):
        """Update the configuration from a dictionary of options.

        :param options: the dictionary of options.

        :raises Exception: if a required argument is not found in the options dictionary.

        :return: None
        """
        # Recurse up the inheritance tree to update the configuration for the parent class
        if isinstance(super(), Config_Base):
            super().update_config(options)
        # Go through all the fields of the dataclass
        for field in self.__dataclass_fields__.values():
            # Skip fields starting with '_'
            if field.name.startswith("_"):
                continue

            # Only update the field if it is in the options dictionary
            if field.name in options:
                value = options[field.name]
                if value is None:
                    continue
                # TODO: Append for nargs/append actions?
                setattr(self, field.name, self.cmd_line_arg_value_to_dataclass_field_value(value, field))
            else:
                if field.metadata.get("required", False):
                    raise Exception(f"Required argument '{field.name}' not found in options dict.")

    def get_list_of_options_values(self, tag_defaults: bool = False) -> list[str]:
        """Get a list of strings with the options and their values.

        :param tag_defaults: whether to tag the default values. Used for viewing a configuration.

        :return: the list of strings with the options and their values.
        """
        retstr_list: list[str] = []
        if isinstance(super(), Config_Base):
            retstr_list = super().get_list_of_options_values()
        else:
            retstr_list: list[str] = []

        for field in self.__dataclass_fields__.values():
            if field.name.startswith("_"):
                continue

            value = getattr(self, field.name)

            # if field.name == "input_files":
            #     raise Exception(value[0])

            # Used for --dfg-operations and other append actions
            values = []
            if value is None:
                continue
            if value == "":
                continue
            if isinstance(value, str):
                values.append(self.escape_string(value))
            elif isinstance(value, (list, tuple)):
                if len(value) == 0:
                    continue
                if field.metadata.get("nargs", None) == "+":
                    values = value
                else:
                    values.append(self.join_list(value))
            elif isinstance(value, Enum):
                values.append(value.name)

            for value in values:
                if tag_defaults and value == self.get_field_default_value(field):
                    color_str = "grey"
                    option_str = self.color(
                        f"{self.dataclass_field_name_to_cmd_line_arg_name(field.name)} {value} (default)", color_str
                    )
                else:
                    option_str = f"{self.dataclass_field_name_to_cmd_line_arg_name(field.name)} {value}"

                retstr_list.append(option_str)

        return retstr_list

    @staticmethod
    def color(text: str, color: str) -> str:
        """Color a string for output in a terminal using termcolor (if available).

        :param text: the string to color.
        :param color: the color to use.

        :return: the colored string.
        """

        return termcolor.colored(text, color)

    def get_list_of_help_strings(self) -> list[list[str]]:
        """Get a list of strings with the options and their help messages.

        :return: the list of strings with the options and their help messages.
        """

        retstr_columns: list[list[str]] = []
        if isinstance(super(), Config_Base):
            retstr_columns = super().get_list_of_help_strings()

        for field in self.__dataclass_fields__.values():
            if field.name.startswith("_"):
                continue

            left_str = ""
            left_str += self.color(f"{self.dataclass_field_name_to_cmd_line_arg_name(field.name)}", "light_blue")

            # FIXME: should display the argparser type?
            python_type = self.resolve_field_type(field.type)
            left_str += f": {self.color(python_type.__name__, 'green')} "

            default = self.get_field_default_value(field)
            if default is not _MISSING_TYPE:
                if python_type is str:
                    default = f"'{default}'"
                left_str += f"= {default} "

            required = field.metadata.get("required", False)
            if required:
                left_str += self.color("Required ", "red")

            right_str = ""

            right_str += f"{field.metadata.get('help', '')} "

            if issubclass(python_type, Enum):
                choices = [e.name for e in python_type]
            else:
                choices = field.metadata.get("choices", None)
            if choices is not None:
                right_str += self.color(f"Choices: {choices} ", "yellow")

            retstr_columns.append([left_str, right_str])

        return retstr_columns

    def get_command_line_args(self) -> str:
        """Generates the exact command line arguments that would be used to run the program.

        :return: the command line arguments.
        """
        return " ".join(self.get_list_of_options_values())

    def view_help(self, output_prefix: str = "", output_header: bool = True, prog_args: list[str] = None) -> list[list[str]]:
        """Generates a human-readable string with the options and their help messages.

        :param output_prefix: the prefix to add to each line.
        :param output_header: whether to add a header to the output (the name of the configuration class).
        :param prog_args: the program arguments to include in the output.

        :return: the human-readable string with the options and their help messages.
        """
        if prog_args is None:
            prog_args = []

        columns_of_strings: list[list[str]] = []

        if output_header:
            name = termcolor.colored(type(self).__name__, "grey", attrs=["bold"])
            columns_of_strings.append([f"{output_prefix}- {name}", " "])
            output_prefix = f"{output_prefix}  "

        sub_columns_of_strings = self.get_list_of_help_strings()
        for left, right in sub_columns_of_strings:
            columns_of_strings.append([f"{output_prefix}{left}", f"{right}"])

        return columns_of_strings

    def view_options(self, output_prefix: str = "", output_header: bool = True) -> str:
        """Generates a human-readable string with the options and their values.

        :param output_prefix: the prefix to add to each line.
        :param output_header: whether to add a header to the output (the name of the configuration class).

        :return: the human-readable string with the options and their values.
        """
        retstr_list: list[str] = []

        if output_header:
            retstr_list.append(f"{output_prefix}- {type(self).__name__}:")
            output_prefix = f"{output_prefix}  "

        list_of_options_values = self.get_list_of_options_values(tag_defaults=True)
        for option_value in list_of_options_values:
            retstr_list.append(f"{output_prefix}{option_value}")

        return "\n".join(retstr_list) + "\n"

    def to_dict(self, include_default_values: bool = True) -> dict[str, str]:
        """Convert the configuration to a dictionary.

        :param include_default_values: whether to include default values in the dictionary. Default is True.

        :return: the dictionary with the configuration.
        """
        ret_dict: dict[str, str] = {}

        for field in self.__dataclass_fields__.values():
            if field.name.startswith("_"):
                continue

            value = getattr(self, field.name)
            if value is None:
                continue
            if value == "":
                continue
            if not include_default_values and value == self.get_field_default_value(field):
                continue
            if isinstance(value, str):
                value = self.escape_string(value)
            # elif isinstance(value, (list, tuple)):
            #     value = self.join_list(value)
            elif isinstance(value, Enum):
                raise NotImplementedError("Enum not supported yet, needs an encoder.")

            ret_dict[field.name] = value

        return ret_dict

    def update_from_dict(self, config_dict: dict[str, str], error_if_required_option_missing: bool = True) -> None:
        """Update the configuration from a dictionary.

        :param config_dict: the dictionary with the configuration.
        :param error_if_required_option_missing: whether to raise an exception if a required argument is not found in the options dictionary.

        :raises Exception: if a required argument is not found in the options dictionary.
        """
        for field in self.__dataclass_fields__.values():
            if field.name in config_dict:
                value = config_dict[field.name]
                setattr(self, field.name, value)
            else:
                if error_if_required_option_missing and field.metadata.get("required", False):
                    raise Exception(f"Required argument '{field.name}' not found in options dict.")

    def escape_string(self, str_to_escape: str) -> str:
        """Escape a string for use in a command line argument, avoiding problems with quotes and backslashes.

        :param str_to_escape: the string to escape.

        :return: the escaped string.
        """
        retstr: str = str_to_escape

        retstr = retstr.replace("'", r"\\'")
        retstr = retstr.replace('"', r'\\"')
        retstr = retstr.replace(r"\\", r"\\\\")

        return retstr

    def join_list(self, list_str: List[str]) -> str:
        """Join a list of strings into a single string, escaping each string.

        :param list_str: the list of strings to join.

        :return: the joined string.
        """
        if list_str is None:
            return "[None]"

        return ",".join(self.escape_string(str(_)) for _ in list_str)

    @staticmethod
    def bool_arg(v: Union[bool, str]) -> bool:
        """Convert a string to a boolean value.
        Accepts the following string values, case-insensitive:
        - "True", "Y", "Yes", "1" for True.
        - "False", "N", "No", "0" for False.

        :param v: the string to convert to a boolean value.

        :raises ArgumentTypeError: if the string is not a valid boolean value.

        :return: the boolean value.
        """
        if isinstance(v, bool):
            return v
        if v.lower() in ("true", "y", "yes", "1"):
            return True
        elif v.lower() in ("false", "f", "n", "no", "0"):
            return False
        else:
            raise ArgumentTypeError("Boolean value expected.")
