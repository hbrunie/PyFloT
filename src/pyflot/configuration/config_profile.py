from dataclasses import dataclass, field
from pyflot.configuration.config_base import ConfigBase


@dataclass
class ConfigProfile(ConfigBase):

    binary: str = field(
        default="./",
        metadata={"required": True, "help": "binary file absolute or relative path: DONT FORGET ./ if in same directory!"},
    )
    params: str = field(default="", metadata={})
    ptunerdir: str = field(default="./", metadata={})
    stratfile: list[str] = field(
        default_factory=list,
        metadata={"help": "List of json files containing either generated strategies and/or strategies to apply."},
    )
    outputfile: str = field(
        default="stdoutAndstderr",
        metadata={"help": """Stdout and stderr are dumped into:
    /path/to/outputdirectory/outputfile_profile.txt or ./ptuner_stratCOUNT_DATE_outputfile.txt"""},
    )
    profilefile: str = field(
        default="profile.json",
        metadata={"help": """Profile phase dumps the JSON into profilefile into outputdir,
    Applying strat phase read into to create strat files."""},
    )
    onlyProfile: bool = field(
        default=False,
        metadata={
            "help": """Choose to do only profiling no strategy generation,
    no applying strategy. One execution.""",
        },
    )
    onlyGenStrat: bool = field(
        default=False,
        metadata={
            "help": """Choose to do only strategies generation based on existing profiling.
    No application execution here.""",
        },
    )
    onlyApplyingStrat: bool = field(
        default=False,
        metadata={
            "help": "Choose to do only applying strategy. These MUST already have been generated.",
        },
    )
    movePLTdir: bool = field(
        default=False,
        metadata={
            "help": "Choose to move plt directories according to strategy number.",
        },
    )
    execAllStrat: bool = field(
        default=False,
        metadata={
            "help": "Exec all strategies even when a valid one is found",
        },
    )
    verif_text: str = field(
        default="VERIFICATION SUCCESSFUL",
        metadata={
            "required": True,
            "help": "Text searched in output to verify the code executed without accuracy error",
        },
    )
