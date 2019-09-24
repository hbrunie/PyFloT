import os
import subprocess
from Strategy import Strategy
import subprocess

class Profiling:
    __binary = "None"
    __dumpJsonProfileFile = "None"
    __directory = "None"

    def __init__(self, binary, directory, profileFile):
        self.__directory = directory
        self.__binary = binary
        self.__dumpJsonProfileFile = directory + "/" + profileFile
        assert self.__dumpJsonProfileFile != "None"
        self.getCodeProfile()
        return None

    def __repr__(self):
        s = "Profile: binary({}) dumpJsonProfileFile({})".format(
                self.__binary, self.__dumpJsonProfile)
        return s

    def getCodeProfile(self):
        procenv = os.environ.copy()
        procenv["PRECISION_TUNER_DUMPJSONPROFILINGFILE"] = self.__dumpJsonProfileFile
        procenv["OMP_NUM_THREADS"]="1"
        procenv["PRECISION_TUNER_MODE"]="APPLYING_PROF"
        #procenv["PRECISION_TUNER_DEBUG"] = ""
        command = []
        #command = ["./PeleC2d.gnu.haswell.OMP.ex", "./inputs-2d-regt"]
        command.append(self.__binary)
        print("PROFILING Command: ",command)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        #with open(f, "w") as ouf:
        #    ouf.write(strout)
        print(strout)
        ## TODO:check the dumpJsonProfilingFile file has been created
        ## TODO:check its content

    def developStrategy(self):
        strategies = []
        stop = False
        count = 0
        while (not stop):
            strat = Strategy(self.__binary,self.__directory,self.__dumpJsonProfileFile, count)
            yield strat
            stop = strat.isLast()
            count += 1
