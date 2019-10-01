import os
import subprocess
from Strategy import Strategy
import subprocess

class Profiling:
    __binary = "None"
    __dumpJsonProfileFile = "None"
    __directory = "None"

    def __init__(self, args, doNotExec):
        self.__directory           = args.ptunerdir
        self.__binary              = args.binary
        self.__param               = args.param
        self.__onlyApplyingStrat   = args.onlyApplyingStrat
        self.__onlyGenStrat        = args.onlyGenStrat
        self.__outputFile          = args.outputfile
        self.__dumpJsonProfileFile = args.ptunerdir + "/" + args.profilefile
        assert self.__dumpJsonProfileFile != "None"
        if not doNotExec:
            self.executeApplicationProfiling()
        return None

    def __repr__(self):
        s = "Profile: binary({}) dumpJsonProfileFile({})".format(
                self.__binary, self.__dumpJsonProfile)
        return s

    def executeApplicationProfiling(self):
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
        outputfile = self.__directory + self.__outputFile+"_profile.txt"
        with open(outputfile, "w") as ouf:
            ouf.write(strout)
        print(strout)

    def developStrategy(self, stratfiles):
        stop = False
        count = 0
        while (not stop):
            strat = Strategy(self.__binary, self.__param, self.__directory,
                             self.__dumpJsonProfileFile, self.__outputFile,
                             self.__onlyApplyingStrat, self.__onlyGenStrat, stratfiles, count)
            yield strat
            stop = strat.isLast()
            count += 1
