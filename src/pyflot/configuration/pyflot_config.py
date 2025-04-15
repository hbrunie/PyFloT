from dataclasses import dataclass, field
from pyflot.configuration.config_base import ConfigBase


@dataclass
class PyflotConfig(ConfigBase):
    connector: str = field(
        default="schweinshaxe",
        metadata={
            "help": "Connector, e.g., 'schweinshaxe'",
            "choices": ["schweinshaxe", "croco", "tpdeshouches", "generic"],
            "required": True,
        },
    )
    verbosity: int = field(default=0, metadata={"help": "Verbosity of Poseidon."})
    _stages: tuple = (
        "variable_scope",
        "control_flow",
        "data_flow_graph",
        "dfg_operations",
        "render_data_flow",
        "generate_code",
    )
    up_to_stage: int = field(
        default=len(_stages), metadata={"help": f"Choose up to which stage to execute Poseidon. The stages are {_stages}"}
    )
    warnings: bool = field(default=True, metadata={"help": "Print warnings"})
    print_output_fortran: bool = field(default=False, metadata={"help": "Print the output Fortran code"})
    view_config: bool = field(default=False, metadata={"help": "View the configuration"})
    dump_config_to_file: str = field(default="", metadata={"help": "Dump the configuration to a JSON file"})
