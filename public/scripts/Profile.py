import json
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
    _typeConfiguration = []
    ## List indexed by SLOC id,
    ## each element is a set of backtrace ID corresponding to
    ## same SLOC id
    _slocListOfBtIdSet = []

    def __init__(self,jsonFile):
        self._profileFile = jsonFile
        print(jsonFile)
        with open(jsonFile, 'r') as json_file:
            self._profile = json.load(json_file)
        self.updateProfile()
        self._typeConfiguration = [0] *self._totalDynCalls
        return None

    def trialFailure(self):
        self._nbTrial += 1

    def mergeBt2SLOC(self, btSet):
        sloc = set([map(x,self._correspondanceBt2SLOC) for x in btSet])
        return sorted(list(sloc))

    def revertSuccess(self, spConvertedSet):
        for i in spConvertedSet:
            self._typeConfiguration[i] = 0
        self._dynCallsSP = self._typeConfiguration.count(1)
        self._statCallsSP = mergeBt2SLOC.count(0)

    def trialSuccess(self,spConvertedSet):
        for i in spConvertedSet:
            self._typeConfiguration[i] = 1
        self._dynCallsSP = self._typeConfiguration.count(1)
        self._statCallsSP = mergeBt2SLOC.count(0)

    def weight(self, s):
        return sum(map(s, lambda i: self._weightPerBtCallSite[i]))


    def display(self):
        ratioStatSP = float(self._statCallsSP) / float(self._totalSlocCallSites)
        ratioDynSP = float(self._dynCallsSP) / float(self._totalDynCalls)
        if verbose > 0:
            print(f"nbTrials: {self._nbTrials}")
            print(f"ratioStatSP: {ratioStatSP*100:2.0f}")
            print(f"ratioDynSP: {ratioDynSP*100:2.0f}")
            print(f"dynCallsSP: {self._dynCallsSP}")
            print(f"statCallsSP: {self._statCallsSP}")
            print(f"totalDynCalls: {self._totalDynCalls}")
            print(f"totalStatCalls: {self._totalSlocCallSites}")

    def updateProfile(self):
        slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
        btCallSitesList = self._profile["IndependantCallStacks"]
        self._doublePrecisionSet = set(range(len(btCallSitesList)))
        self._weightPerBtCallSite = []
        slocDict = {}
        currentSlocId = 0
        for currentBtId,btCallSite in enumerate(btCallSitesList):
            self._totalDynCalls += btCallSite["CallsCount"]
            self._weightPerBtCallSite.append(btCallSite["CallsCount"])
            ## Building SLOC HashKeys: addr2line
            m = re.search(slocreg, btCallSite["Addr2lineCallStack"][0])
            assert(m)
            slocHKey = m.group(0)
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
            btCallSite["BtHashKey"] = btHKey
            btCallSite["SlocHashKey"] = slocHKey
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
                slocCallSite["StaticHashKey"] = slocHKey
                slocCallSite["SlocCallsCount"] = slocCallSite["CallsCount"]
                slocDict[slocHKey] = slocCallSite
