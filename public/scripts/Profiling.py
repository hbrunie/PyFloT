import os
import subprocess
from Strategy import Strategy
class Profiling:
    __binary = "None"
    __dumpJsonProfileFile = "None"
    __directory = "None"

    def __init__(self, binary, directory):
        self.__directory = directory
        self.__binary = binary
        self.__dumpJsonProfileFile = directory + "/profile.json"
        assert self.__dumpJsonProfileFile != "None"
        self.getCodeProfile()
        return None

    def __repr__(self):
        s = "Profile: binary({}) dumpJsonProfileFile({})".format(
                self.__binary, self.__dumpJsonProfile)
        return s

    def getCodeProfile(self):
        procenv = os.environ.copy()
        procenv["DUMPJSONPROFILINGFILE"] = self.__dumpJsonProfileFile
        procenv["DEBUG"] = "info,infoplus"
        command = []
        command.append(self.__binary)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        ## TODO:check the dumpJsonProfilingFile file has been created
        ## TODO:check its content

    def developStrategy(self):
        strategies = []
        stop = False
        count = 0
        while (not stop):
            strat = Strategy(self.__binary,self.__directory,self.__dumpJsonProfileFile)
            yield strat
            stop = strat.isLast()
            count += 1
