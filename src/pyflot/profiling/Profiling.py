import os

from pyflot.profiling.Strategy import Strategy
from pyflot.profiling.Envvars import Envvars
from pyflot.configuration.config_handler import ConfigHandler

class Profiling(Envvars):
    __binary = "None"
    __dumpJsonProfileFile = "None"
    __directory = "None"

    def __init__(self, config_handler: ConfigHandler):
        super(Profiling, self).__init__()
        self.__directory           = args.ptunerdir
        self.__binary              = args.binary
        self.__param               = args.params
        self.__onlyApplyingStrat   = args.onlyApplyingStrat
        self.__onlyGenStrat        = args.onlyGenStrat
        self.__execAllStrat        = args.execAllStrat
        self.__outputFile          = args.outputfile
        self.__dumpJsonProfileFile = args.profilefile
        assert self.__dumpJsonProfileFile != "None"
        if not doNotExec:
            print("Profiling application ...")
            self.executeApplicationProfiling()
            print("Application profiled")
        return None

    def __repr__(self):
        s = "Profile: binary({}) dumpJsonProfileFile({})".format(Profiling.__binary, Profiling.__dumpJsonProfileFile)
        return s

    def execute(self, command, outputfile, procenv):
        print(command)
        out = super().execute(command,outputfile, procenv)
        return out

    def executeApplicationProfiling(self):
        procenv = os.environ.copy()
        procenv[self._ENVVAR_PTUNERDUMPPROF] = self.__dumpJsonProfileFile
        procenv[self._ENVVAR_OMPNUMTHREADS] = "1"
        procenv[self._ENVVAR_DUMPDIR] = self.__directory
        procenv[self._ENVVAR_BINARY] = self.__binary
        os.system("mkdir -p {}".format(self.__directory))
        print("env: {}={} {}={} {}={} {}={}".format(self._ENVVAR_BINARY,procenv[self._ENVVAR_BINARY],
            self._ENVVAR_DUMPDIR, procenv[self._ENVVAR_DUMPDIR],
            self._ENVVAR_OMPNUMTHREADS, procenv[self._ENVVAR_OMPNUMTHREADS],
            self._ENVVAR_PTUNERDUMPPROF, procenv[self._ENVVAR_PTUNERDUMPPROF]))
        # procenv["PRECISION_TUNER_DEBUG"] = ""
        command = []
        command.append(self.__binary + " " + self.__param)
        print("PROFILING Command: ",command)
        outputfile = self.__outputFile + "_profile.txt"
        out = self.execute(command,outputfile,procenv)

    def _developStrategy(self):
        stratfiles = self.strategy_files
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

    def develop_strategy(self):
        stopSearch = False
        ## Calls Strategy constructor
        stratGen = self._developStrategy()
        while not stopSearch:
            try:
                ## Calls Strategy constructor
                strat = next(stratGen)
            except StopIteration:
                if self.only_gen_strat:
                    print("No more strategy to generate.")
                else:
                    print("No more strategy to test.")
                return None
            if not self.only_gen_strat:
                stopSearch = strat.applyStrategy(self.verif_text)
        return None
