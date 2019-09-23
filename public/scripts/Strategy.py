import os
import json
import subprocess
import decimal

class Strategy:
    __readJsonProfileFile = "None"
    __readJsonStratFile = "None"
    __dumpJsonStratResultFile = "None"
    __binary = "None"
    __JSON_MAIN_LIST = "IndependantCallStacks"
    __JSON_DYNCALL_STRATEGY_KEY = "Strategy"
    __JSON_DYNCALL_STRATEGY_DETAILED_KEY = "DetailedStrategy"
    __JSON_CALLSCOUNT = "CallsCount"
    __JSON_TOTALCALLSTACKS = "TotalCallStacks"
    __strategy = []
    stratCoupleList = [
            ([[0,1]],[[0,0.9]]),
            ([[0.1,1]],[[0.2,1]]),
            ([[0,0.8]],[[0.3,1]]),
            ([[0,0.7]],[[0.4,1]]),
            ([[0,0.6]],[[0,0.5]]),
            ([[0.5,1]],[[0,0.4]]),
            ([[0.6,1]],[[0,0.3]]),
            ([[0.7,1]],[[0,0.2]]),
            ([[0.,.1]],[[0.9,1]]),
            ([[0,0]],[[0,0]])
            ]
    strategiesForAllCall = []
    __firstCall = True

    ## CallSites, containing many dynamic calls
    ## "Strategies" is a list S[S],
    ## Inside there are one list s[s] for each strategy to test.
    ## Each Strategy list is made of as many lists c[c] as CallSites
    ## S[ s[c1[ multiSet c1],c2[ multiSet c2],...,cn[ multiSet cn]s], s[c1[ multiSet c1],c2[ multiSet c2],...,cn[ multiSet cn]s], ..., s[c1[ multiSet c1],c2[ multiSet c2],...,cn[ multiSet cn]s] S]
    ##--> [ [ [[],[]] [[],[]]... [[],[]] ], ... [[[]] [[]] ... [[]]] ]
    def updateStrategies(self, callSitesCount):
        def updateStrategy(stratList, cond, stratCouple):
            if cond:
                stratList.append(stratCouple[0])
            else:
                stratList.append(stratCouple[1])

        for stratCouple in self.stratCoupleList:
            for strat in [[0,1],[0,0.5],[0.5,1],[0,0]]:
                ## callSites will stratCouple[0]
                ## or stratCouple[1] according to their belonging to strat
                strategyForAllCallSites = []
                for cs in range(callSitesCount):
                    ## Normalize cs ID
                    isIn = float(cs) / float(callSitesCount)
                    sup = strat[0] <= isIn
                    inf = isIn < strat[1]
                    cond = sup and inf
                    updateStrategy(strategyForAllCallSites, cond, stratCouple)
                Strategy.strategiesForAllCall.append(list(strategyForAllCallSites))

    def __init__(self, binary, directory, readJsonProfileFile, count):
        """ def detailedStrategy: strategy multiset
            converted from 0 -- 1 to 0 -- totalDynCall
            basically: bound*totalDynCall
        """
        def readFileName(count):
            return "readJsonStrat_{}.json".format(count)
        def dumpFileName(count):
            return "dumpJsonStratResults_{}.json".format(count)
        def roundUp(x):
            return int(decimal.Decimal(x).quantize(decimal.Decimal('1'),
        rounding=decimal.ROUND_HALF_UP))
        def inf(x,cc):
            """ Compute inf bound detailed strategy:
                from CallsCount and strategy contiguous set """
            return roundUp(cc*x[0])
        def sup(x,cc):
            """ Compute sup bound detailed strategy:
                from CallsCount and strategy contiguous set """
            return roundUp(cc*x[1])-1

        self.__readJsonStratFile       = directory + readFileName(count)
        self.__dumpJsonStratResultFile = directory + dumpFileName(count)
        self.__binary                  = binary

        ##TODO: do it only once (first instanciation) use static class attribute
        ## for profile
        ## BE AWARE: profile variable is local to each instance for filling
        ## strategy read JSON files
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        ## Dev strategy: Only done by first instanciation
        if profile[self.__JSON_TOTALCALLSTACKS] == 0:
            exit(-1)
        if Strategy.__firstCall:
            self.updateStrategies(len(profile[self.__JSON_MAIN_LIST]))
            Strategy.__firstCall = False

        ## Pop from Strategies list the first strategy for all call sites
        strategyForAllCallSites = Strategy.strategiesForAllCall.pop(0)
        ## for each call site: pop corresponding strategy
        ## and convert to detailedStrategy
        self.__strategy = []
        for i,dynCall in enumerate(profile[self.__JSON_MAIN_LIST]):
            callsCount = dynCall[self.__JSON_CALLSCOUNT]
            ## Specific call site strategy
            strategy = strategyForAllCallSites.pop(0)
            ## convert to detailed strategy
            detailedStrategy = [[inf(x,callsCount), sup(x, callsCount)] for x in strategy]
            ## update JSON representation
            dynCall[self.__JSON_DYNCALL_STRATEGY_KEY] = strategy
            dynCall[self.__JSON_DYNCALL_STRATEGY_DETAILED_KEY] = detailedStrategy
            ## Store current strategy for display if WINNER
            self.__strategy.append(list(detailedStrategy))
        print(self.__strategy)
        ## Each time Strategy is instantiate: fill strategy json file
        with open(self.__readJsonStratFile, 'w') as json_file:
            json.dump(profile, json_file, indent=2)
        return None

    def applyStrategy(self, checkString):
        procenv = os.environ.copy()
        ## TODO: No need of profile file for these executions 
        ## by the PrecisionTuner library
        procenv["READJSONPROFILESTRATFILE"]     = self.__readJsonStratFile
        procenv["DUMPJSONSTRATSRESULTSFILE"]   = self.__dumpJsonStratResultFile
        #procenv["DEBUG"] = "fperror"
        #print("PYTHON: ", procenv["READJSONPROFILESTRATFILE"])
        #print("PYTHON: ", procenv["DUMPJSONSTRATSRESULTSFILE"])
 
        command = []
        command.append(self.__binary)
        print("Command: ",command)
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
        return len(Strategy.strategiesForAllCall) == 0
