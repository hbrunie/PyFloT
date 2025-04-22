from dataclasses import dataclass, field
from pyflot.configuration.config_base import ConfigBase


@dataclass
class PyflotConfig(ConfigBase):
    strat0 = "BT"
    strat1 = "BT-C"
    strat2 = "BT-Cf"
    strat3 = "BT-Cf->BT"
    strat4 = "BT-C->BT"
    strat5 = "SLOC"
    strat6 = "SLOC-C"
    strat7 = "SLOC-C->SLOC"
    strat8 = "SLOC-C->SLOC->BT"
    strat9 = "SLOC-C->SLOC->BT-Cf"
    strat10 = "SLOC-C->SLOC->BT-Cf->BT"
    strat11 = "SLOC-C->SLOC->BT-C"
    strat12 = "SLOC-C->SLOC->BT-C->BT"
    strat13 = "SLOC->BT"
    _strategies = tuple(
        [strat0, strat1, strat2, strat3, strat4, strat5, strat6, strat7, strat8, strat9, strat10, strat11, strat12, strat13]
    )
    strategy: str = field(
        default="BT",
        metadata={
            "help": "Select the strategy to apply for searching tuning precision tuple",
            "choices": _strategies,
            "required": True,
        },
    )
    verbosity: int = field(default=0, metadata={"help": "Verbosity of Poseidon.", "choices": (0, 1, 2, 3)})
    warnings: bool = field(default=True, metadata={"help": "Print warnings"})
    verif_text: str = field(
        default="Unknown",
        metadata={
            "required": True,
            "help": (
                "Text to be compared to program output to validate the correct floating point execution of the target program."
            ),
        },
    )
    profile_file: str = field(default="profile.json", metadata={})

    verif_text: str = field(default="AMReX (20.01-36-gfee20d598e0a-dirty) finalized", metadata={})
    params: str = field(default="", metadata={})
    dumpdir: str = field(default="./", metadata={})
    mergedtracefile: str = field(default="mergeCSVintoTrace.trace", metadata={})
    filtering: bool = field(default=False, metadata={})
    maxdepth: int = field(default=1, metadata={})
    windowSize: int = field(default=2, metadata={})
    threshold: int = field(default=100000, metadata={})
