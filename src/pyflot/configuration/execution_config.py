
from dataclasses import dataclass, field
from pyflot.configuration.config_base import ConfigBase


@dataclass
class ConfigExecution(ConfigBase):
    _ENVVAR_DUMPSTRAT                   = "PRECISION_TUNER_DUMPJSONSTRATSRESULTSFILE"
    _ENVVAR_DUMPDIR                     = "PRECISION_TUNER_OUTPUT_DIRECTORY"
    _ENVVAR_READSTRAT                   = "PRECISION_TUNER_READJSONPROFILESTRATFILE"
    _ENVVAR_PTUNERMODE                  = "PRECISION_TUNER_MODE"
    _ENVVAR_OMPNUMTHREADS               = "OMP_NUM_THREADS"
    _ENVVAR_PTUNERDEBUG                 = "DEBUG"
    _ENVVAR_BINARY                      = "TARGET_FILENAME"
    _ENVVAR_PTUNERDUMPPROF              = "PRECISION_TUNER_DUMPJSON"
    #_ENVVAR_PTUNERDUMPPROFCSV           = "PRECISION_TUNER_DUMPCSV"
    _MODE_STRAT = "APPLYING_STRAT"