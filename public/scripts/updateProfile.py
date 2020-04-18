class Profile:
    """
    """
    __totalDynCalls           = 0
    __totalStatCalls          = 0
    __correspondanceDynStatic = 0
    __typeConfiguration       = []
    __profile                 = {}

    def __init__(self,jsonFile):
        print(jsonFile)
        with open(jsonFile, 'r') as json_file:
            __profile = json.load(json_file)
        updateProfile()
        return None

    def updateProfile(profile, usebtsym = False):
        slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
        btsymbolreg = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
        dynCalls = __profile["IndependantCallStacks"]
        staticCalls = []
        staticCallsd = {}
        __profile["StaticCalls"] = staticCalls
        __profile["StaticCallsd"] = staticCallsd
        staticmaxlvl = 1
        statCount = 0
        dynCount = 0
        for cs in dynCalls:
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
                __totalDynCalls += cs["CallsCount"]
                statCountMinusOne = statCount - 1
                cs["statname"] = f"statCS-{statCountMinusOne}"
                cs["statid"] = statCountMinusOne
                __correspondanceDynStatic.append(statCountMinusOne)
            ## If not already in dict
            ## Add to dict and update name/hashKey/CallsCount
            ## Append to staticCalls list
            else:
                ##Copy of Dynamic Call dictionnary into the staticCall one
                cs["statname"] = f"statCS-{statCount}"
                cs["statid"] = statCount
                __correspondanceDynStatic.append(statCount)
                staticCallsd[statickey] = cs.copy()
                scs = staticCallsd[statickey]
                scs["StaticHashKey"] = statickey
                ##Change dynCall name for static one, in copy
                ##Update StatCall callsCount with dynamic one, in copy
                __totalDynCalls += cs["CallsCount"]
                __totalStatCalls += 1
                staticCalls.append(scs)
                statCount += 1
        if verbose > 1:
            print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in staticCalls])
            print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in dynCalls])
        return typeConfiguration
