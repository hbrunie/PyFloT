import os
import pdb

class Trial:
    _nbTrials              = 0
    _btTypeConfiguration_g = []
    _slocTypeConfiguration_g = []
    _profile               = None
    _verbose = 1

    def __init__(self, args, verbose, initScore=False):
        self._trialId    = Trial._nbTrials
        Trial._nbTrials += 1
        self._resultsDir      = args.dumpdir + "/results/"
        os.system(f"mkdir -p {self._resultsDir}")
        if initScore:
            return None
        self._btTypeConfiguration = Trial._btTypeConfiguration_g.copy()
        self._slocTypeConfiguration = Trial._slocTypeConfiguration_g.copy()
        cmd = f"{args.binary} {args.params}"
        if verbose > 2:
            print("command",cmd)
        self._cmd             = cmd
        self._profileFile     = args.readdir + args.profilefile
        self._stratDir        = args.stratDir
        self._name            = args.name
        self._checkText       = args.verif_text
        self._callSiteList    = args.callSiteList
        self._binary          = args.binary
        self._outputFileLocal = self._stratDir + "output" + f"-{self._trialId}.dat"
        scoreFile = self._resultsDir + "score.txt"
        return None

    def getName(self):
        return self._name

    def getCallSiteList(self):
        return self._callSiteList

    def checkPMF(self, f, checkText):
        ## Check PMF result
        res = checkText
        with open(f, "r") as inf:
            for l in inf.readlines():
                if res in l:
                    return True
        return False

    def runCheckScript(self,f, checkText):
        #return checkTest3Exp()
        return self.checkPMF(f, checkText)

    def runApp(self):
        self.updateEnv()
        outputFile      = "output"
        outputFileLocal = self._stratDir + outputFile + f"-{self._trialId}.dat"
        ## File name Should be same as in generateStrat.py
        cmd = self._cmd + f" >> {self._outputFileLocal}"
        print("Command:",cmd)
        os.system(cmd)
        self._valid = self.runCheckScript(outputFileLocal, self._checkText)
        if Trial._verbose>2:
            print(f"Trial number({self._trialId}) Valid? {self._valid}")
        return self

    def _score(self):
        score = 0
        for i,x in enumerate(Trial._profile._weightPerBtCallSite):
            score += x*self._btTypeConfiguration[i]
        Trial._profile._dynCallsSP = max(score,Trial._profile._dynCallsSP)
        return 100.*float(Trial._profile._dynCallsSP) / float(Trial._profile._totalDynCalls)

    def success(self,sloc):
        if sloc:
            for y in self._callSiteList:
                for x in self._profile._slocListOfBtIdSet[y]:
                    self._btTypeConfiguration[x] = 1
        else:
            for y in self._callSiteList:
                self._btTypeConfiguration[y] = 1

    def failure(self,sloc):
        return None

    def display(self):
        #ratioSlocSP = 100.* float(self._slocCallSitesSP) / float(self._totalSlocCallSites)
        #ratioBtSP   = 100.* float(self._btCallSitesSP) / float(self._totalBtCallSites)
        if self._trialId == 0:
            ratioDynSP = 0
        else:
            ratioDynSP  = self._score()
        #print(f"{self._nbTrials} {ratioSlocSP:.2f} {ratioBtSP:.2f} {ratioDynSP:.2f} {self._dynCallsSP} {self._slocCallSitesSP} {self._btCallSitesSP} {self._totalDynCalls} {self._totalSlocCallSites} {self._totalBtCallSites}")
        print(f"{self._trialId} {ratioDynSP:.2f}")
        print("scorefile: ",self._scorefile)
        with open(self._scorefile, "a") as ouf:
            ouf.write(f"{self._trialId} {ratioDynSP:.2f}\n")
        #self._verbose = 0
        #if self._verbose > 0:
        #    #print(Fore.RED + f"nbTrials: {self._nbTrials}"+Style.RESET_ALL)
        #    if self._verbose > 1:
        #        print(f"ratioSlocSP: {ratioSlocSP*100:2.0f}")
        #        print(f"ratioBtSP: {ratioBtSP*100:2.0f}")
        #        print(f"ratioDynSP: {ratioDynSP*100:2.0f}")
        #        if self._verbose > 2:
        #            print(f"dynCallsSP: {self._dynCallsSP}")
        #            print(f"statCallsSP: {self._slocCallSitesSP}")
        #            print(f"statCallsSP: {self._btCallSitesSP}")
        #            print(f"totalDynCalls: {self._totalDynCalls}")
        #            print(f"totalSlocCallSites: {self._totalSlocCallSites}")
        #            print(f"totalBtCallSites: {self._totalBtCallSites}")

    def updateEnv(self):
        resultsDir = self._resultsDir
        profileFile = self._profileFile
        binary = self._binary
        verbose = self._verbose
        procenv = {}
        ##TODO: use script arguments
        procenv["TARGET_FILENAME"] = binary
        ##TODO: why need profileFile to apply strategy (libC++)?
        procenv["PRECISION_TUNER_READJSON"] = profileFile
        ##TODO change with real csv filename
        procenv["PRECISION_TUNER_DUMPCSV"] = "./whocares.csv"
        procenv["PRECISION_TUNER_OUTPUT_DIRECTORY"] = resultsDir
        procenv["PRECISION_TUNER_MODE"] = "APPLYING_STRAT"
        procenv["PRECISION_TUNER_DUMPJSON"] = resultsDir + f"./results-{self._name}.json"
        backtrace = f"{self._stratDir}/strat-{self._name}.txt"
        procenv["BACKTRACE_LIST"] = backtrace

        envStr = "TARGET_FILENAME="
        envStr += binary
        envStr += " PRECISION_TUNER_READJSON="
        envStr += profileFile
        envStr += " PRECISION_TUNER_DUMPCSV="
        envStr += "./whocares.csv"
        envStr += " PRECISION_TUNER_OUTPUT_DIRECTORY="
        envStr += resultsDir
        envStr += " PRECISION_TUNER_MODE=APPLYING_STRAT"
        for var,value in procenv.items():
            os.environ[var] = value
            if verbose>3:
                print(f"{var}={value}")
        return envStr
