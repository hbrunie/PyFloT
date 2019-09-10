import os
import json
import subprocess
class Strategy:
    __count = 0
    __readJsonProfileFile = "None"
    __readJsonStratFile = "None"
    __dumpJsonStratResultFile = "None"
    __binary = "None"
    __JSON_MAIN_LIST = "IndependantCallStacks"
    __JSON_DYNCALL_STRATEGY_KEY = "Strategy"
    strategies = [[[0.4,0.6], [0,0.3]],[[0,1]]]
    def __init__(self, binary, directory, readJsonProfileFile):
        count = self.__count
        self.__readJsonStratFile = directory + "readJsonStrat_{}.json".format(count)
        self.__dumpJsonStratResultFile = directory + "dumpJsonStratResults_{}.json".format(count)
        self.__binary = binary
        self.__count += 1
        ## Dev strategy
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        for dynCall in profile[self.__JSON_MAIN_LIST]:
            dynCall[self.__JSON_DYNCALL_STRATEGY_KEY] = Strategy.strategies.pop(0)
            #dynCall[self.__JSON_DYNCALL_STRATEGY_KEY] = [[0,0.2], [0.4,1]]
        with open(self.__readJsonStratFile, 'w') as json_file:
            json.dump(profile, json_file, indent=2)
        return None

    def applyStrategy(self, checkString):
        procenv = os.environ.copy()
        ## TODO: No need of profile file for these executions 
        ## by the PrecisionTuner library
        procenv["READJSONPROFILESTRATFILE"]     = self.__readJsonStratFile
        procenv["DUMPJSONSTRATSRESULTSFILE"]   = self.__dumpJsonStratResultFile
        procenv["DEBUG"] = "info"
        print("PYTHON: ", procenv["DUMPJSONPROFILINGFILE"])
 
        command = []
        command.append(self.__binary)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        print(strout)
        #get count of lowered from output
        if checkString in strout:
            ## Stop when valid strategy found
            return True
        else:
            return False
    
    def isLast(self):
        return len(Strategy.strategies) == 0
