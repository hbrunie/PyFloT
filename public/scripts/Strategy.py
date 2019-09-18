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
    __JSON_DYNCALL_STRATEGY_DETAILED_KEY = "DetailedStrategy"
    __JSON_CALLSCOUNT = "CallsCount"
    __strategy = []
    ## 2 call sites
    #strategies = [[[0,1]],[[0,1]],[[0,1]],[[0,0]],[[0,0]],[[0,1]],[[0,0]],[[0,0]]]
    ## 1 call sites
    strategies = [[[0,1]],[[0,0.5]],[[0.5,1]],[[0,0.4]],[[0,0.3]],[[0,0.2]],[[0,0.1]],[[0,0]]]
    strategiesPerCall = [[[0,1]],[[0,0.5]]]#,[[0.5,1]],[[0,0.4]],[[0,0.3]],[[0,0.2]],[[0,0.1]],[[0.6,1]],[[0.7,1]],[[0.8,1]],[[0.9,1]],[[0,0]]]
    strategiesForAllCall = []
    __firstCall = True

    def __init__(self, binary, directory, readJsonProfileFile, count):
        self.__readJsonStratFile = directory + "readJsonStrat_{}.json".format(count)
        self.__dumpJsonStratResultFile = directory + "dumpJsonStratResults_{}.json".format(count)
        self.__binary = binary
        ## Dev strategy
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        if Strategy.__firstCall:
            self.updateStrategies(len(profile[self.__JSON_MAIN_LIST]))
            Strategy.__firstCall = False
        i=0
        #print(len(profile[self.__JSON_MAIN_LIST]))
        for dynCall in profile[self.__JSON_MAIN_LIST]:
            #print(Strategy.strategiesForAllCall)
            print(Strategy.strategiesForAllCall[i])
            strategy = Strategy.strategiesForAllCall[i].pop(0)
            callsCount = dynCall[self.__JSON_CALLSCOUNT]
            detailedStrategy = [[int(callsCount*x[0]), int(callsCount*x[1])] for x in strategy]
            self.__strategy = strategy
            dynCall[self.__JSON_DYNCALL_STRATEGY_KEY] = strategy
            #print(strategy,detailedStrategy,callsCount)
            dynCall[self.__JSON_DYNCALL_STRATEGY_DETAILED_KEY] = detailedStrategy #[strategy[0]*callsCount, strategy[1]*callsCount]
            i += 1
        print(Strategy.strategiesForAllCall)
        with open(self.__readJsonStratFile, 'w') as json_file:
            json.dump(profile, json_file, indent=2)
        return None

    def updateStrategies(self, l):
        for i in range(l):
            Strategy.strategiesForAllCall.append(list(Strategy.strategiesPerCall))


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
            print(self.__strategy)
            print("Results in: ", self.__dumpJsonStratResultFile)
            return True
        else:
            return False
    
    def isLast(self):
        return len(Strategy.strategiesForAllCall[0]) == 0
