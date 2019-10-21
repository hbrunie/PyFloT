import subprocess
import os

class Envvars:
    _ENVVAR_DUMPSTRAT                   = "PRECISION_TUNER_DUMPJSONSTRATSRESULTSFILE"
    _ENVVAR_READSTRAT                   = "PRECISION_TUNER_READJSONPROFILESTRATFILE"
    _ENVVAR_PTUNERMODE                  = "PRECISION_TUNER_MODE"
    _ENVVAR_OMPNUMTHREADS               = "OMP_NUM_THREADS"
    _ENVVAR_PTUNERDEBUG                 = "DEBUG"
    _ENVVAR_PTUNERDUMPPROF ="PRECISION_TUNER_DUMPJSONPROFILINGFILE"
    _MODE_PROF = "APPLYING_PROF"
    _MODE_STRAT = "APPLYING_STRAT"
    def __init__(self):
        return None

    def execute(self, command, outputfile, procenv):
        out = ""
        try:
            output = subprocess.check_output(
                    command, stderr=subprocess.STDOUT, shell=True,
                    universal_newlines=True, env=procenv)
        except subprocess.CalledProcessError as exc:
            out = "Status : FAIL\nCode: {}\n{}".format(exc.returncode, exc.output)
        else:
            out = "Output: \n{}\n".format(output)
        with open(outputfile, "w") as ouf:
            ouf.write(out)
        return out
