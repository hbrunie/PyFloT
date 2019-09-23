import os
import subprocess
from Strategy import Strategy
class Profiling:
    __binary = "None"
    __dumpJsonProfileFile = "None"
    __directory = "None"

    def __init__(self, binary, directory, profileFile):
        self.__directory = directory
        self.__binary = binary
        self.__dumpJsonProfileFile = directory + "/" + profileFile
        assert self.__dumpJsonProfileFile != "None"
        #self.getCodeProfile()
        return None

    def __repr__(self):
        s = "Profile: binary({}) dumpJsonProfileFile({})".format(
                self.__binary, self.__dumpJsonProfile)
        return s

    def getCodeProfile(self):
        procenv = os.environ.copy()
        procenv["DUMPJSONPROFILINGFILE"] = self.__dumpJsonProfileFile
        #procenv["DEBUG"] = "fperror"
        command = []
        command.append(self.__binary)
        #print("PYTHON: DUMPJSONPROFILINGFILE-->",procenv["DUMPJSONPROFILINGFILE"])
        print("Command: ",command)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
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
