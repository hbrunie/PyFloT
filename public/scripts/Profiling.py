import os
import subprocess
from Strategy import Strategy
import subprocess

class Profiling:
    __binary = "None"
    __dumpJsonProfileFile = "None"
    __directory = "None"

    def __init__(self, binary, directory, profileFile, param,
            outputFile, onlyGenStrat, onlyApplyingStrat):
        self.__directory = directory
        self.__binary = binary
        self.__param = param
        self.__outputFile = outputFile
        self.__dumpJsonProfileFile = directory + "/" + profileFile
        assert self.__dumpJsonProfileFile != "None"
        if not onlyGenStrat and not onlyApplyingStrat:
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
        command.append(self.__binary+" " +self.__param)
        print("PROFILING Command: ",command)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv, shell=True)
        strout = out.decode("utf-8")
        with open(self.__outputFile+"_profile.txt", "w") as ouf:
            ouf.write(strout)
        print(strout)

    def developStrategy(self, onlyApplyingStrat):
        strategies = []
        stop = False
        count = 0
        while (not stop):
            strat = Strategy(self.__binary,self.__param,self.__directory,self.__dumpJsonProfileFile,
                    count, self.__outputFile, onlyApplyingStrat)
            yield strat
            stop = strat.isLast()
            count += 1
