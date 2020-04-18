class Profile:
    """ Rename it metada? (profile + score)
    """
    __totalDynCalls           = 0
    __totalStatCalls          = 0
    __correspondanceBt2SLOC = 0
    __statCallsSP = 0
    __dynCallsSP = 0
    __doublePrecisionSet       = set()
    __profile                 = {}
    __nbTrials = 0
    ## double precision 0, single precision 1
    __typeConfiguration = []

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
        ratioStatSP = float(self.__statCallsSP) / float(self.__totalStatCalls)
        ratioDynSP = float(self.__dynCallsSP) / float(self.__totalDynCalls)
        if verbose > 0:
            print(f"nbTrials: {self.__nbTrials}")
            print(f"ratioStatSP: {ratioStatSP*100:2.0f}")
            print(f"ratioDynSP: {ratioDynSP*100:2.0f}")
            print(f"dynCallsSP: {self.__dynCallsSP}")
            print(f"statCallsSP: {self.__statCallsSP}")
            print(f"totalDynCalls: {self.__totalDynCalls}")
            print(f"totalStatCalls: {self.__totalStatCalls}")

    def updateProfile(self, profile, usebtsym = False):
        slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
        btsymbolreg = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
        dynCalls = self.__profile["IndependantCallStacks"]
        self.__weightPerBtCallSite = []
        staticCalls = []
        staticCallsd = {}
        self.__profile["StaticCalls"] = staticCalls
        self.__profile["StaticCallsd"] = staticCallsd
        staticmaxlvl = 1
        statCount = 0
        dynCount = 0
        for cs in dynCalls:
            self.__weightPerBtCallSite.append(cs["CallsCount"])
            ##Update search set
            self.__doublePrecisionSet.add(dynCount)
            ##Building HashKeys: btsymbol and addr2line
            ## Static
            ## addr2line identification
            m = re.search(slocreg, cs["Addr2lineCallStack"][0])
            assert(m)
            addr2lineStaticKey = m.group(0)
            ## btsymbol identification
            m = re.search(btsymbolreg, cs["CallStack"][0])
            assert(m)
            statickey = m.group(1)
            btSymStaticKey = statickey
            if not usebtsym:
                statickey = addr2lineStaticKey
            ## Dynamic addr2line identification
            ##TODO: Unused HashKey
            addr2lineDynamicKey = ""
            for callstack in  cs["Addr2lineCallStack"]:
                ##addr2line identification
                m = re.search(slocreg, callstack)
                ## don't treat callstack after main
                if callstack == "??:0":
                    break
                assert(m)
                addr2lineDynamicKey += m.group(0)
            ##dynamic identification
            cs["dynname"] = f"D-{dynCount}"
            cs["dynid"] = dynCount
            cs["BtSymStaticKey"] = btSymStaticKey
            dynCount += 1
            ## If already in dict update CallsCount
            if staticCallsd.get(statickey):
                scs = staticCallsd[statickey]
                scs["CallsCount"] += cs["CallsCount"]
                self.__totalDynCalls += cs["CallsCount"]
                statCountMinusOne = statCount - 1
                cs["statname"] = f"statCS-{statCountMinusOne}"
                cs["statid"] = statCountMinusOne
                self.__correspondanceBt2SLOC.append(statCountMinusOne)
            ## If not already in dict
            ## Add to dict and update name/hashKey/CallsCount
            ## Append to staticCalls list
            else:
                ##Copy of Dynamic Call dictionnary into the staticCall one
                cs["statname"] = f"statCS-{statCount}"
                cs["statid"] = statCount
                self.__correspondanceBt2SLOC.append(statCount)
                staticCallsd[statickey] = cs.copy()
                scs = staticCallsd[statickey]
                scs["StaticHashKey"] = statickey
                ##Change dynCall name for static one, in copy
                ##Update StatCall callsCount with dynamic one, in copy
                self.__totalDynCalls += cs["CallsCount"]
                self.__totalStatCalls += 1
                staticCalls.append(scs)
                statCount += 1
        if verbose > 1:
            print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in staticCalls])
            print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in dynCalls])
