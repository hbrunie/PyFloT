import os
import json
import subprocess
class Strategy:
    __readJsonProfileFile = "None"
    __readJsonStratFile = "None"
    __dumpJsonStratResultFile = "None"
    __binary = "None"
    __JSON_MAIN_LIST = "IndependantCallStacks"
    __JSON_DYNCALL_STRATEGY_KEY = "Strategy"
    strategies = [[[0,1]],[[0,1]],[[0,1]],[[0,0]],[[0,0]],[[0,1]],[[0,0]],[[0,0]]]
    def __init__(self, binary, directory, readJsonProfileFile, count):
        self.__readJsonStratFile = directory + "readJsonStrat_{}.json".format(count)
        self.__dumpJsonStratResultFile = directory + "dumpJsonStratResults_{}.json".format(count)
        self.__binary = binary
        ## Dev strategy
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        for dynCall in profile[self.__JSON_MAIN_LIST]:
            strategy = Strategy.strategies.pop(0)
            dynCall[self.__JSON_DYNCALL_STRATEGY_KEY] = strategy
        with open(self.__readJsonStratFile, 'w') as json_file:
            json.dump(profile, json_file, indent=2)
        return None

    def applyStrategy(self, checkString):
        procenv = os.environ.copy()
        ## TODO: No need of profile file for these executions 
        ## by the PrecisionTuner library
        procenv["READJSONPROFILESTRATFILE"]     = self.__readJsonStratFile
        procenv["DUMPJSONSTRATSRESULTSFILE"]   = self.__dumpJsonStratResultFile
        procenv["DEBUG"] = "fperror"
        #print("PYTHON: ", procenv["READJSONPROFILESTRATFILE"])
        #print("PYTHON: ", procenv["DUMPJSONSTRATSRESULTSFILE"])
 
        command = []
        command.append(self.__binary)
        print(command)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        print(strout)
        #get count of lowered from output
        if checkString in strout:
            print("Valid strategy found: ", self.__readJsonStratFile)
            print("Results in: ", self.__dumpJsonStratResultFile)
            return True
        else:
            return False
    
    def isLast(self):
        return len(Strategy.strategies) == 0
