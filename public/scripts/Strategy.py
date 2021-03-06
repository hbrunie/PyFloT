import os
import json
import subprocess
import decimal
import datetime
import io

from Envvars import Envvars
from DataStrategy import DataStrategy

now = datetime.datetime.now()
date = f"{now.month}-{now.day}-{now.year}_{now.hour}-{now.minute}"

class Strategy(Envvars):
    __readJsonStratFile                  = "None"
    __dumpJsonStratResultFile            = "None"
    __binary                             = "None"
    #__strategy                           = []
    __JSON_MAIN_LIST                     = "IndependantCallStacks"
    __JSON_DYNCALL_STRATEGY_KEY          = "Strategy"
    __JSON_DYNCALL_STRATEGY_DETAILED_KEY = "DetailedStrategy"
    __JSON_CALLSCOUNT                    = "CallsCount"
    __JSON_TOTALCALLSTACKS               = "TotalCallStacks"
    __firstCall                          = True

    def __init__(self, binary, param, directory, readJsonProfileFile,
            outputFile, onlyApplyingStrat, onlyGenStrat, stratfiles, count,
            executeAllStrat):
        """ Instantiate Strategy. 
            Either:
                (1) Generate and apply 
                (2) just Generate
                (3) just Apply
            (1) or (2): Generation is made only on first instantiation (CLASS Static list)
                        Then, at each new instantiation, the corresponding JSON file
                        is generated, poping element of the static list.
            (1) Application is run using generated JSON file.
            (3) Application is run reading stratfiles.
        """
        ### Core code ###
        super(Strategy, self).__init__()
        self.__onlyApplyingStrat = onlyApplyingStrat
        self.__executeAllStrategies = executeAllStrat
        if Strategy.__firstCall:
            Strategy.__count = 0
            Strategy.__decount = self.countStratFiles(directory)## number of strat files
            Strategy.__stratfiles = stratfiles
            if not onlyApplyingStrat:
                self.updateStrategiesStaticList(readJsonProfileFile)
            Strategy.__firstCall = False
        readJsonStratFile = directory + "/readJsonStrat_{}.json".format(Strategy.__count)
        if not onlyApplyingStrat:
            self.generatesStrategyJSONfile(readJsonProfileFile, readJsonStratFile)
        if not onlyGenStrat:
            self.updateAttribute2ApplyStrategy(readJsonStratFile, param, binary, directory)
        Strategy.__count += 1
        Strategy.__decount -= 1
        return None

    def execute(self, command, outputfile, procenv, count):
        out = super().execute(command,outputfile, procenv)
        os.system("mv plt00000 plt00000_strat{}".format(count))
        os.system("mv plt00030 plt00030_strat{}".format(count))
        os.system("mv chk00000 chk00000_strat{}".format(count))
        os.system("mv chk00030 chk00030_strat{}".format(count))
        #laststep = lastOccurence("STEP", out)
        #print("Strategy: {}, STEP reached: {}".format(self.__count, laststep))
        return out

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
        procenv                             = os.environ.copy()
        procenv[self._ENVVAR_READSTRAT]     = self.__readJsonStratFile
        procenv[self._ENVVAR_DUMPSTRAT]     = self.__dumpJsonStratResultFile
        procenv[self._ENVVAR_PTUNERMODE]    = self._MODE_STRAT
        procenv[self._ENVVAR_OMPNUMTHREADS] = "1"
        #procenv[Strategy.__ENVVAR_PTUNERDEBUG]  = "fperror,comparison"
        command = []
        command.append(self.__binary+" " +self.__param)
        print("Strategy Command: ",command)
        out = self.execute(command, self.__outputFile, procenv, Strategy.__count)
        #get count of lowered from output
        if checkString in out:
            print("Valid strategy found: ", self.__readJsonStratFile)
            print("Results in: ", self.__dumpJsonStratResultFile)
            if (self.__executeAllStrategies):
                return False ## Execute all strategies
            else:
                return True
        else:
            return False
    
    def isLast(self):
        if self.__onlyApplyingStrat:
            return self.__decount == 0
        else:
            return len(Strategy.strategiesForAllCall) == 0

    def countStratFiles(self, directory):
        return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) and "readJsonStrat" in name])

    def updateAttribute2ApplyStrategy(self, readStratFile, param, binary, directory):
        self.__readJsonStratFile       = readStratFile
        self.__binary                  = binary
        self.__param                   = param
        self.__outputFile              = directory + "/ptuner_applystrat{}_{}.txt".format(Strategy.__count, date)
        self.__dumpJsonStratResultFile = directory + "dumpStratResults_{}.json".format(Strategy.__count)

    def generatesStrategyJSONfile(self, readJsonProfileFile, readJsonStratFile):
        ### Some local lambda functions ###
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
        ### Core Code ###
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        if profile[Strategy.__JSON_TOTALCALLSTACKS] == 0:
            exit(-1)
        ## Pop from Strategies list the first strategy for all call sites
        strategyForAllCallSites = Strategy.strategiesForAllCall.pop(0)
        ## for each call site: pop corresponding strategy
        ## and convert to detailedStrategy
        #Strategy.__strategy = []
        for i,dynCall in enumerate(profile[Strategy.__JSON_MAIN_LIST]):
            callsCount = dynCall[Strategy.__JSON_CALLSCOUNT]
            ## Specific call site strategy
            strategy = strategyForAllCallSites.pop(0)
            ## convert to detailed strategy
            detailedStrategy = [[inf(x,callsCount), sup(x, callsCount)] for x in strategy]
            ## update JSON representation
            dynCall[Strategy.__JSON_DYNCALL_STRATEGY_KEY] = strategy
            dynCall[Strategy.__JSON_DYNCALL_STRATEGY_DETAILED_KEY] = detailedStrategy
            ## Store current strategy for display if WINNER
            #Strategy.__strategy.append(list(detailedStrategy))
        ## Each time Strategy is instantiate: fill strategy json file
        with open(readJsonStratFile, 'w') as json_file:
            json.dump(profile, json_file, indent=2)

    ## Looking for a better strategy
    ## We stop when the strategy has not been increase in the last X steps
    ## start with some random lower, then lower around this call
    ## Lower more and more aggressively when it works
    ## Lower less and less when it does not (factor of the loss)
    ## See algorithm pseudo code

    strategiesForAllCall = []

    ## CallSites, containing many dynamic calls
    ## "Strategies" is a list S[S],
    ## Inside there are one list s[s] for each strategy to test.
    ## Each Strategy list is made of as many lists c[c] as CallSites
    ## S[ s[c1[ multiSet c1],c2[ multiSet c2],...,cn[ multiSet cn]s], s[c1[ multiSet c1],c2[ multiSet c2],...,cn[ multiSet cn]s], ..., s[c1[ multiSet c1],c2[ multiSet c2],...,cn[ multiSet cn]s] S]
    ##--> [ [ [[],[]] [[],[]]... [[],[]] ], ... [[[]] [[]] ... [[]]] ]
    def updateStrategiesStaticList(self,readJsonProfileFile):
        """ Updates the STATIC strategiesForAllCall
            list containing strategies for all call sites,
            all dynamic calls.
        """
        ### Lambda function ###
        def updateStrategy(stratList, cond, stratCouple):
            if cond:
                stratList.append(stratCouple[0])
            else:
                stratList.append(stratCouple[1])
        ### Core code ###
        with open(readJsonProfileFile, 'r') as json_file:
            profile = json.load(json_file)
        if profile[Strategy.__JSON_TOTALCALLSTACKS] == 0:
            print("Error no callstacks")
            exit(-1)
        callSitesCount = len(profile[Strategy.__JSON_MAIN_LIST])
        ds = DataStrategy()
        for stratCouple in ds.stratCoupleList:
            for strat in ds.stratRepartingCoupleList:
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
