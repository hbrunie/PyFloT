class Trial:
    _nbTrials              = 0
    _btTypeConfiguration_g = []
    _slocTypeConfiguration_g = []
    _profile               = None
    _verbose = 1

    def __init__(self, cmd, stratDir, name, verif_text, envStr, callSiteList):
        self._btTypeConfiguration = Trial._btTypeConfiguration_g.copy()
        self._slocTypeConfiguration = Trial._slocTypeConfiguration_g.copy()
        self._cmd             = cmd
        self._stratDir        = stratDir
        self._name            = name
        self._checkText       = verif_text
        self._envStr          = envStr
        self._callSiteList    = callSiteList
        self._trialId         = Trial._nbTrials
        self._outputFileLocal = self._stratDir + "output" + f"-{self._trialId}.dat"
        Trial._nbTrials += 1
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
        outputFile      = "output"
        outputFileLocal = self._stratDir + outputFile + f"-{self._trialId}.dat"
        ## File name Should be same as in generateStrat.py
        backtrace = f"{self._stratDir}/strat-{self._name}.txt"
        os.environ["BACKTRACE_LIST"] = backtrace
        if Trial._verbose>3:
            print(f"BACKTRACE_LIST={backtrace}")
        os.environ["PRECISION_TUNER_DUMPJSON"] = f"./dumpResults-{self._name}.json"
        if Trial._verbose>3:
            print(f"{envStr} PRECISION_TUNER_DUMPJSON="+f"./dumpResults-{self._name}.json")
            print(self._cmd)
        os.system(self._cmd + f" >> {self._outputFileLocal}")
        self._valid = self.runCheckScript(outputFileLocal, self._checkText)
        if Trial._verbose>2:
            print(f"BacktraceListFile ({backtrace}) Valid? {valid}")
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

    def display(self,scoreFile):
        #ratioSlocSP = 100.* float(self._slocCallSitesSP) / float(self._totalSlocCallSites)
        #ratioBtSP   = 100.* float(self._btCallSitesSP) / float(self._totalBtCallSites)
        ratioDynSP  = self._score()
        #print(f"{self._nbTrials} {ratioSlocSP:.2f} {ratioBtSP:.2f} {ratioDynSP:.2f} {self._dynCallsSP} {self._slocCallSitesSP} {self._btCallSitesSP} {self._totalDynCalls} {self._totalSlocCallSites} {self._totalBtCallSites}")
        print(f"{self._trialId} {ratioDynSP:.2f}")
        with open(scoreFile, "a") as ouf:
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
