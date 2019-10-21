import os

from Strategy import Strategy
from Envvars import Envvars

class Profiling(Envvars):
    __binary = "None"
    __dumpJsonProfileFile = "None"
    __directory = "None"

    def __init__(self, args, doNotExec):
        super(Profiling, self).__init__()
        self.__directory           = args.ptunerdir
        self.__binary              = args.binary
        self.__param               = args.param
        self.__onlyApplyingStrat   = args.onlyApplyingStrat
        self.__onlyGenStrat        = args.onlyGenStrat
        self.__execAllStrat        = args.execAllStrat
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

    def execute(self, command, outputfile, procenv):
        out = super().execute(command,outputfile, procenv)
        os.system("mv plt00000 plt00000_profile")
        os.system("mv plt00030 plt00030_profile")
        os.system("mv chk00000 chk00000_profile")
        os.system("mv chk00030 chk00030_profile")
        return out

    def executeApplicationProfiling(self):
        procenv = os.environ.copy()
        procenv[self._ENVVAR_PTUNERDUMPPROF] = self.__dumpJsonProfileFile
        procenv[self._ENVVAR_OMPNUMTHREADS] = "1"
        procenv[self._ENVVAR_PTUNERMODE] = self._MODE_PROF
        #procenv["PRECISION_TUNER_DEBUG"] = ""
        command = []
        command.append(self.__binary+" " +self.__param)
        print("PROFILING Command: ",command)
        outputfile = self.__directory + self.__outputFile+"_profile.txt"
        out = self.execute(command,outputfile,procenv)

    def developStrategy(self, stratfiles):
        stop = False
        count = 0
        while (not stop):
            strat = Strategy(self.__binary, self.__param, self.__directory,
                             self.__dumpJsonProfileFile, self.__outputFile,
                             self.__onlyApplyingStrat, self.__onlyGenStrat,
                             stratfiles, count, self.__execAllStrat)
            yield strat
            stop = strat.isLast()
            count += 1
