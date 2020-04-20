from colorama import Fore, Back, Style
import json
import pdb
import re
class Profile:
    """ Rename it metada? (profile + score)
    """
    _totalDynCalls         = 0
    _totalSlocCallSites    = 0
    _totalBtCallSites    = 0

    _slocCallSitesSP           = 0
    _btCallSitesSP           = 0
    _dynCallsSP            = 0

    _nbTrials              = 0
    _verbose = 1
    _doublePrecisionBtSet     = set()
    _doublePrecisionSlocSet     = set()
    _profile               = {}
    _correspondanceBt2SLOC  = []
    ## double precision 0, single precision 1
    _btTypeConfiguration = []
    _slocTypeConfiguration = []
    ## List indexed by SLOC id,
    ## each element is a set of backtrace ID corresponding to
    ## same SLOC id
    _slocListOfBtIdSet = []
    ##trialGlobalVar
    ## SlocCallSiteCount
    ## BetaP
    _prevDynCallsSP = 0
    ## Gammap
    _prevBtCallSitesSP = 0
    _firstTrial = True

    def __init__(self,jsonFile,verbose):
        self._profileFile = jsonFile
        self._verbose = verbose
        with open(jsonFile, 'r') as json_file:
            self._profile = json.load(json_file)
        self.updateProfile()
        self._doublePrecisionSlocSet = set(range(self._totalSlocCallSites))
        self._btTypeConfiguration = [0] *self._totalBtCallSites
        self._slocTypeConfiguration = [0] *self._totalSlocCallSites
        self._onlyOnce = True
        print("List indexed by CLOC id, containing corresponding set BtId: ",self._slocListOfBtIdSet)
        return None

    def trialFailure(self):
        self._nbTrials += 1

    def getInfoByBtId(self,x):
        return [x]

    def trialSuccessMultiSite(self,spConvertedSet, sloc):
        self._nbTrials += 1

    def trialNewStep(self):
        self._firstTrial = True

    def clusternbBtInSLOC(self, sloc):
        n = 0
        for s in sloc:
            n+=len(self._slocListOfBtIdSet[s])
        return n

    def nbBtInSLOC(self, sloc):
        return len(self._slocListOfBtIdSet[sloc])

    def updateSlocCallSite(self,callSitesList, sloc, cluster, indiv):
        if sloc:
            if cluster:
                self._slocCallSitesSP = max(self._slocCallSitesSP, len(callSitesList))
            else:
                if indiv and self._onlyOnce:
                    self._onlyOnce = False
                    self._slocCallSitesSP = self._slocCallSitesSP + 1
                else:
                    self._slocCallSitesSP = self._slocCallSitesSP + len(callSitesList) - 1

    def trialSuccessMultiSiteBFS(self, slocCallSite, sloc):
        self.trialSuccessMultiSite(slocCallSite, sloc)
        self.updateSlocCallSite(slocCallSite,sloc,False,False)

    def trialSuccessMultiSiteCluster(self, slocCallSite, sloc):
        self.trialSuccessMultiSite(slocCallSite, sloc)
        self.updateSlocCallSite(slocCallSite,sloc,True,False)

    def trialSuccessMultiSite(self, CallSites, sloc):
        self._nbTrials += 1
        if sloc:
            ## Beta <- Betap + w(Delta)
            self._dynCallsSP = self._prevDynCallsSP + self.clusterslocweight(CallSites)
            ## Gamma <- Gammap + f(Delta)
            self._btCallSitesSP = self._prevBtCallSitesSP + self.clusternbBtInSLOC(CallSites)
        else:
            self._dynCallsSP = self._prevDynCallsSP + self.clusterbtweight(CallSites)
            self._btCallSitesSP = self._prevBtCallSitesSP + len(CallSites)

    def trialSuccessIndivBFS(self, slocCallSite, sloc):
        self.trialSuccessIndiv(slocCallSite,sloc)
        self.updateSlocCallSite(slocCallSite,sloc,False,True)

    def trialSuccessIndivCluster(self, slocCallSite, sloc):
        self.trialSuccessIndiv(slocCallSite,sloc)
        self.updateSlocCallSite(slocCallSite,sloc,True,True)

    def trialSuccessIndiv(self, CallSites, sloc):
        """ slocCallSite is a single integer
        """
        self._nbTrials += 1
        if self._firstTrial:
            self._firstTrial = False
            ## Betap <- Beta
            self._prevDynCallsSP = self._dynCallsSP
            ## Gammap <- Gamma
            self._prevBtCallSitesSP = self._btCallSitesSP
        if sloc:
            ## Beta
            self._dynCallsSP = max(self._dynCallsSP, self._prevDynCallsSP + self.clusterslocweight(CallSites))
            ## Gamma
            self._btCallSitesSP = max(self._btCallSitesSP, self._prevBtCallSitesSP + self.clusternbBtInSLOC(CallSites))
        else:
            self._dynCallsSP = max(self._dynCallsSP, self._prevDynCallsSP + self.clusterbtweight(CallSites))
            self._btCallSitesSP = max(self._btCallSitesSP, self._prevBtCallSitesSP + len(CallSites))

    def clusterbtweight(self, s):
        weights = []
        for x in s:
            weights.append(self._weightPerBtCallSite[x])
        return sum(weights)

    def btweight(self, x):
        return self._weightPerBtCallSite[x]

    def slocweight(self, x):
        btIdSetList = self._slocListOfBtIdSet[x]
        return self.clusterbtweight(btIdSetList)

    def clusterslocweight(self, s):
        weights = []
        for x in s:
            btIdSetList = self._slocListOfBtIdSet[x]
            weights.append(self.clusterbtweight(btIdSetList))
        return sum(weights)

    def convertSloc2BtId(self, l):
        """ in params: list of sloc call sites id [0,1,2]
            use _slocListOfBtIdSet[i] --> set of Bt Id corresponding to SLOC call sites ID i
        """
        r = []
        for i in l:
            r.extend(list(self._slocListOfBtIdSet[i]))
        r.sort()
        return r

    def getHashKeyList(self,l,sloc):
        r = []
        for e in l:
            hk = None
            if sloc:
                for x in self._slocCallSitesList:
                    if x["SlocId"] == e:
                        hk = x["SlocSymbolsHashKey"]
                        break
            else:#BT
                for x in self._btCallSitesList:
                    if x["BtId"] == e:
                        hk = x["HashKey"]
                        break
            assert hk != None
            r.append(hk)
        return r

    def display(self):
        ratioSlocSP = float(self._slocCallSitesSP) / float(self._totalSlocCallSites)
        ratioBtSP = float(self._btCallSitesSP) / float(self._totalBtCallSites)
        ratioDynSP = float(self._dynCallsSP) / float(self._totalDynCalls)
        if ratioSlocSP >1.0:
            pdb.set_trace()
        if self._verbose > 0:
            print(Fore.RED + f"nbTrials: {self._nbTrials}"+Style.RESET_ALL)
            if self._verbose > 1:
                print(f"ratioSlocSP: {ratioSlocSP*100:2.0f}")
                print(f"ratioBtSP: {ratioBtSP*100:2.0f}")
                print(f"ratioDynSP: {ratioDynSP*100:2.0f}")
                if self._verbose > 2:
                    print(f"dynCallsSP: {self._dynCallsSP}")
                    print(f"statCallsSP: {self._slocCallSitesSP}")
                    print(f"statCallsSP: {self._btCallSitesSP}")
                    print(f"totalDynCalls: {self._totalDynCalls}")
                    print(f"totalSlocCallSites: {self._totalSlocCallSites}")
                    print(f"totalBtCallSites: {self._totalBtCallSites}")

    def updateProfile(self):
        slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
        btsymbolreg = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
        self._btCallSitesList = self._profile["IndependantCallStacks"]
        self._slocCallSitesList = []
        self._totalBtCallSites = len(self._btCallSitesList)
        self._doublePrecisionBtSet = set(range(self._totalBtCallSites))
        self._weightPerBtCallSite = []
        slocDict = {}
        currentSlocId = 0
        for currentBtId,btCallSite in enumerate(self._btCallSitesList):
            self._totalDynCalls += btCallSite["CallsCount"]
            self._weightPerBtCallSite.append(btCallSite["CallsCount"])
            ## Building SLOC HashKeys: addr2line
            m = re.search(slocreg, btCallSite["Addr2lineCallStack"][0])
            assert(m)
            slocHKey = m.group(0)
            m = re.search(btsymbolreg, btCallSite["CallStack"][0])
            assert(m)
            slocSymbolsHKey = m.group(1)
            ## Building Backtrace HashKeys: addr2line
            btHKey = ""
            for callstack in  btCallSite["Addr2lineCallStack"]:
                ##addr2line identification
                m = re.search(slocreg, callstack)
                ## don't treat callstack after main
                if callstack == "??:0":
                    break
                assert(m)
                btHKey += m.group(0)
            ## identification
            btCallSite["BtId"] = currentBtId
            ## HashKey already exist in btCallSite: it is the BtHashKey without addr2line
            btCallSite["BtAddrHashKey"] = btHKey
            btCallSite["SlocAddrHashKey"] = slocHKey
            btCallSite["SlocSymbolsHashKey"] = slocSymbolsHKey
            ## If already in dict update CallsCount
            if slocDict.get(slocHKey):
                ## Retrieve slocCallSite from dictionnary
                slocCallSite                    = slocDict[slocHKey]
                ## Update number of dynamic calls done through this SLOC call site
                slocCallSite["SlocCallsCount"] += btCallSite["CallsCount"]
                ## update list indexed by SLOC id, containing backtrace Callsite id set
                self._slocListOfBtIdSet[slocCallSite["SlocId"]].add(currentBtId)
                self._correspondanceBt2SLOC.append(slocCallSite["SlocId"])
            ## If not already in dict
            else:
                btCallSite["SlocId"] = self._totalSlocCallSites
                self._correspondanceBt2SLOC.append(self._totalSlocCallSites)
                self._totalSlocCallSites += 1
                ## update list of backtrace ID corresponding to same SLOC id
                self._slocListOfBtIdSet.append(set([currentBtId]))
                ##Copy of Backtrace Call Site into SLOC Call site
                slocCallSite = btCallSite.copy()
                slocCallSite["SlocAddrHashKey"] = slocHKey
                slocCallSite["SlocCallsCount"] = slocCallSite["CallsCount"]
                slocDict[slocHKey] = slocCallSite
                self._slocCallSitesList.append(slocCallSite)
