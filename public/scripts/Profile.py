class Profile:
    """ Rename it metada? (profile + score)
    """
    __totalDynCalls           = 0
    __totalSlocCallSites          = 0
    __correspondanceBt2SLOC = 0
    __statCallsSP = 0
    __dynCallsSP = 0
    __doublePrecisionSet       = set()
    __profile                 = {}
    __nbTrials = 0
    ## double precision 0, single precision 1
    __typeConfiguration = []
    ## List indexed by SLOC id,
    ## each element is a set of backtrace ID corresponding to
    ## same SLOC id
    __slocListOfBtIdSet = []

    def __init__(self,jsonFile):
        self.__profileFile = jsonFile
        print(jsonFile)
        with open(jsonFile, 'r') as json_file:
            self.__profile = json.load(json_file)
        updateProfile()
        self.__typeConfiguration = [0] * len(self.__totalDynCalls)
        return None

    def trialFailure(self):
        self.__nbTrial += 1

    def mergeBt2SLOC(self, btSet):
        sloc = set([map(x,self.__correspondanceBt2SLOC) for x in btSet])
        return sorted(list(sloc))

    def revertSuccess(spConvertedSet):
        for i in spConvertedSet:
            self.__typeConfiguration[i] = 0
        self.__dynCallsSP = self.__typeConfiguration.count(1)
        self.__statCallsSP = mergeBt2SLOC.count(0)

    def trialSuccess(spConvertedSet):
        for i in spConvertedSet:
            self.__typeConfiguration[i] = 1
        self.__dynCallsSP = self.__typeConfiguration.count(1)
        self.__statCallsSP = mergeBt2SLOC.count(0)

    def weight(self, s):
        return sum(map(s, lambda i: self.__weightPerBtCallSite[i]))


    def display(self):
        ratioStatSP = float(self.__statCallsSP) / float(self.__totalSlocCallSites)
        ratioDynSP = float(self.__dynCallsSP) / float(self.__totalDynCalls)
        if verbose > 0:
            print(f"nbTrials: {self.__nbTrials}")
            print(f"ratioStatSP: {ratioStatSP*100:2.0f}")
            print(f"ratioDynSP: {ratioDynSP*100:2.0f}")
            print(f"dynCallsSP: {self.__dynCallsSP}")
            print(f"statCallsSP: {self.__statCallsSP}")
            print(f"totalDynCalls: {self.__totalDynCalls}")
            print(f"totalStatCalls: {self.__totalSlocCallSites}")

    def updateProfile(self, profile):
        slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
        btCallSitesList = self.__profile["IndependantCallStacks"]
        self.__doublePrecisionSet = set(range(len(btCallSitesList)))
        self.__weightPerBtCallSite = []
        slocDict = {}
        currentSlocId = 0
        for currentBtId,btCallSite in enumerate(btCallSitesList):
            self.__totalDynCalls += btCallSite["CallsCount"]
            self.__weightPerBtCallSite.append(btCallSite["CallsCount"])
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
                __slocListOfBtIdSet[slocCallSite["SlocId"]].add(currentBtId)
                self.__correspondanceBt2SLOC.append(slocCallSite["SlocId"])
            ## If not already in dict
            else:
                btCallSite["SlocId"] = self.__totalSlocCallSites
                self.__correspondanceBt2SLOC.append(self.__totalSlocCallSites)
                self.__totalSlocCallSites += 1
                ## update list of backtrace ID corresponding to same SLOC id
                __slocListOfBtIdSet.append(set(currentBtId))
                ##Copy of Backtrace Call Site into SLOC Call site
                slocCallSite = btCallSite.copy()
                slocCallSite["StaticHashKey"] = slocHKey
                slocDict[slocHKey] = slocCallSite
