import json
import pdb
import re
class Profile:
    """ Rename it metada? (profile + score)
    """
    _totalDynCalls         = 0
    _totalSlocCallSites    = 0
    _statCallsSP           = 0
    _dynCallsSP            = 0
    _nbTrials              = 0
    _doublePrecisionSet     = set()
    _profile               = {}
    _correspondanceBt2SLOC  = []
    ## double precision 0, single precision 1
    _btTypeConfiguration = []
    _slocTypeConfiguration = []
    ## List indexed by SLOC id,
    ## each element is a set of backtrace ID corresponding to
    ## same SLOC id
    _slocListOfBtIdSet = []

    def __init__(self,jsonFile,verbose):
        self._profileFile = jsonFile
        self._verbose = verbose
        with open(jsonFile, 'r') as json_file:
            self._profile = json.load(json_file)
        self.updateProfile()
        self._btTypeConfiguration = [0] *self._totalBtCallSites
        self._slocTypeConfiguration = [0] *self._totalSlocCallSites
        return None

    def trialFailure(self):
        self._nbTrials += 1

    def getInfoByBtId(self,x):
        return [x]

    def revertSuccess(self, spConvertedSet):
        for i in spConvertedSet:
            self._btTypeConfiguration[i] = 0
        for i in range(self._totalSlocCallSites):
            self._slocTypeConfiguration[i] = 1
            for j in self._slocListOfBtIdSet[i]:
                if self._btTypeConfiguration[j] == 0:
                    break
        self._dynCallsSP = self._btTypeConfiguration.count(1)
        self._statCallsSP = self._slocTypeConfiguration.count(0)

    def trialSuccess(self,spConvertedSet):
        self._nbTrials += 1
        for i in spConvertedSet:
            self._btTypeConfiguration[i] = 1
        for i in range(self._totalSlocCallSites):
            self._slocTypeConfiguration[i] = 1
            for j in self._slocListOfBtIdSet[i]:
                if self._btTypeConfiguration[j] == 0:
                    break
        self._dynCallsSP = self._btTypeConfiguration.count(1)
        self._statCallsSP = self._slocTypeConfiguration.count(0)

    def weight(self, s):
        weights = []
        for x in s:
            weights.append(self._weightPerBtCallSite[x])
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
        ratioStatSP = float(self._statCallsSP) / float(self._totalSlocCallSites)
        ratioDynSP = float(self._dynCallsSP) / float(self._totalDynCalls)
        if self._verbose > 0:
            print(f"nbTrials: {self._nbTrials}")
            print(f"ratioStatSP: {ratioStatSP*100:2.0f}")
            print(f"ratioDynSP: {ratioDynSP*100:2.0f}")
            print(f"dynCallsSP: {self._dynCallsSP}")
            print(f"statCallsSP: {self._statCallsSP}")
            print(f"totalDynCalls: {self._totalDynCalls}")
            print(f"totalSlocCallSites: {self._totalSlocCallSites}")
            print(f"totalBtCallSites: {self._totalBtCallSites}")

    def updateProfile(self):
        slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
        btsymbolreg = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
        self._btCallSitesList = self._profile["IndependantCallStacks"]
        self._slocCallSitesList = []
        self._totalBtCallSites = len(self._btCallSitesList)
        self._doublePrecisionSet = set(range(self._totalBtCallSites))
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
