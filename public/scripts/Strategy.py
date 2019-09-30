import os
import json
import subprocess
import decimal
import datetime
import io

now = datetime.datetime.now()


class Strategy:
    __readJsonStratFile = "None"
    __dumpJsonStratResultFile = "None"
    __binary = "None"
    __JSON_MAIN_LIST = "IndependantCallStacks"
    __JSON_DYNCALL_STRATEGY_KEY = "Strategy"
    __JSON_DYNCALL_STRATEGY_DETAILED_KEY = "DetailedStrategy"
    __JSON_CALLSCOUNT = "CallsCount"
    __JSON_TOTALCALLSTACKS = "TotalCallStacks"
    __strategy = []
    __count = 0
    stratRepartingCoupleList = [[0,1],[0,0.5],[0.5,1],[0,0]] # [[0.5,1],[0,0]]:
    stratCoupleList = [
            ([[0,0.003]],[[0.997,1]]),
            ([[0,0.002]],[[0.998,1]]),
            ([[0,0.0015]],[[0.9985,1]]),
            ([[0,0.001]],[[0.999,1]]),
            ([[0,0.05]],[[0.9995,1]]),
            ([[0,0.01]],[[0.9998,1]]),
            ([[0,0.005]],[[0.9999,1]])
            ]
    strategiesForAllCall = []
    __firstCall = True

    def __init__(self, binary, param, directory, readJsonProfileFile,
            count, outputFile, onlyApplyingStrat, stratgenfiles, readstratfiles,
             genRandomStrat=False):
        """ def detailedStrategy: strategy multiset
            converted from 0 -- 1 to 0 -- totalDynCall
            basically: bound*totalDynCall
        """
        ### Some local lambda functions ###
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

        # CallSiteCount = len(profile[self.__JSON_MAIN_LIST]
        if Strategy.__firstCall:
            if genRandomStrat:
                self.updateStrategies(callSitesCount))
            Strategy.__firstCall = False

        self.updateAttribute2ApplyStrategy()

        if onlyApplyingStrat:
            return None
        ### Generating strategy JSON files from profile JSON file ###
        self.generatesStrategy(readJsonProfileFile)
        return None

    def applyStrategy(self, checkString):
        """
        """
        ### Some local lambda functions ###
        def lastOccurence(s, text):
            res = "NoOccurence"
            for line in io.StringIO(text).readlines():
                if s in line:
                    res = line
            return res

        ### Starting core function code ###
        procenv = os.environ.copy()
        procenv["PRECISION_TUNER_READJSONPROFILESTRATFILE"]     = self.__readJsonStratFile
        procenv["PRECISION_TUNER_DUMPJSONSTRATSRESULTSFILE"]   = self.__dumpJsonStratResultFile
        procenv["PRECISION_TUNER_MODE"]= "APPLYING_STRAT"
        procenv["OMP_NUM_THREADS"]= "1"
        #procenv["DEBUG"] = "fperror,comparison"

        command = []
        command.append(self.__binary+" " +self.__param)
        print("Strategy Command: ",command)
        out = ""
        try:
                output = subprocess.check_output(
                                command, stderr=subprocess.STDOUT, shell=True,
                                        universal_newlines=True, env=procenv)
        except subprocess.CalledProcessError as exc:
                out = "Status : FAIL\nCode: {}\n{}".format(exc.returncode, exc.output)
        else:
                out = "Output: \n{}\n".format(output)
        laststep = lastOccurence("STEP", out)
        #out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        #strout = out.decode("utf-8")
        print("Strategy: {}, STEP reached: {}".format(self.__count, laststep))
        with open(self.__outputFile, "w") as ouf:
            ouf.write(out)
        #get count of lowered from output
        if checkString in out:
            print("Valid strategy found: ", self.__readJsonStratFile)
            print(self.__strategy)
            print("Results in: ", self.__dumpJsonStratResultFile)
            return True
        else:
            return False
    
    def isLast(self):
        return len(Strategy.strategiesForAllCall) == 0

    def updateAttribute2ApplyStrategy(self):
        self.__readJsonStratFile       = directory + readFileName(count)
        self.__dumpJsonStratResultFile = directory + dumpFileName(count)
        self.__binary                  = binary
        self.__param                  = param
        self.__count = count
        date = f"{now.month}-{now.day}-{now.year}_{now.hour}-{now.minute}"
        self.__outputFile             = "ptuner_strat{}_{}_{}.txt".format(count,date,outputFile)

    def generatesStrategy(self, readJsonProfileFile):
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        ## Dev strategy: Only done by first instanciation
        if profile[Strategy.__JSON_TOTALCALLSTACKS] == 0:
            exit(-1)

        ## Pop from Strategies list the first strategy for all call sites
        strategyForAllCallSites = Strategy.strategiesForAllCall.pop(0)
        ## for each call site: pop corresponding strategy
        ## and convert to detailedStrategy
        self.__strategy = []
        for i,dynCall in enumerate(profile[Strategy.__JSON_MAIN_LIST]):
            callsCount = dynCall[Strategy.__JSON_CALLSCOUNT]
            ## Specific call site strategy
            strategy = strategyForAllCallSites.pop(0)
            ## convert to detailed strategy
            detailedStrategy = [[inf(x,callsCount), sup(x, callsCount)] for x in strategy]
            ## update JSON representation
            dynCall[self.__JSON_DYNCALL_STRATEGY_KEY] = strategy
            dynCall[self.__JSON_DYNCALL_STRATEGY_DETAILED_KEY] = detailedStrategy
            ## Store current strategy for display if WINNER
            self.__strategy.append(list(detailedStrategy))
        #print(self.__strategy)
        ## Each time Strategy is instantiate: fill strategy json file
        with open(self.__readJsonStratFile, 'w') as json_file:
            json.dump(profile, json_file, indent=2)

    ## Looking for a better strategy
    ## We stop when the strategy has not been increase in the last X steps
    ## start with some random lower, then lower around this call
    ## Lower more and more aggressively when it works
    ## Lower less and less when it does not (factor of the loss)
    ## See algorithm pseudo code

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
            for strat in self.stratRepartingCoupleList:
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
