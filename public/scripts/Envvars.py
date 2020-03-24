import subprocess
from subprocess import *
import os

class Envvars:
    _ENVVAR_DUMPSTRAT                   = "PRECISION_TUNER_DUMPJSONSTRATSRESULTSFILE"
    _ENVVAR_DUMPDIR                     = "PRECISION_TUNER_OUTPUT_DIRECTORY"
    _ENVVAR_READSTRAT                   = "PRECISION_TUNER_READJSONPROFILESTRATFILE"
    _ENVVAR_PTUNERMODE                  = "PRECISION_TUNER_MODE"
    _ENVVAR_OMPNUMTHREADS               = "OMP_NUM_THREADS"
    _ENVVAR_PTUNERDEBUG                 = "DEBUG"
    _ENVVAR_PTUNERDUMPPROF              = "PRECISION_TUNER_DUMPJSON"
    #_ENVVAR_PTUNERDUMPPROFCSV           = "PRECISION_TUNER_DUMPCSV"
    _MODE_STRAT = "APPLYING_STRAT"
    def __init__(self):
        return None

    def execute(self, command, outputfile, procenv):
        #out = ""
        #TODO: subprocess communicate, hang out on maybe
        # what could be a not properly closed stderr or stdout...
        # IN PeleC PMF 1D
        #try:
        #    output = subprocess.check_output(
        #            command, stderr=subprocess.STDOUT, shell=True,
        #            universal_newlines=True, timeout=10, env=procenv)
        #except subprocess.CalledProcessError as exc:
        #    out = "Status : FAIL\nCode: {}\n{}".format(exc.returncode, exc.output)
        #else:
        #    out = "Output: \n{}\n".format(output)
        for var,value in procenv.items():
            os.environ[var] = value
        print(" ".join(command))
        os.system(" ".join(command))
        #with open(outputfile, "w") as ouf:
        #    ouf.write(out)
        return ""
