import json
import os
import re

profile = {}
globalBestName = None
verbose = 0
def getVerbose():
    return verbose

correspondanceDynStatic = []
def getCorrStatList():
    """ return a list giving the corresopndance between
        dynamic ID and static ID.
        This list is filled inside updateProfile.
        It is useful in communities build_graph and generate_clusters functions.
    """
    return correspondanceDynStatic

nbTrials       = 0
ratioDynSP     = 0.
ratioStatSP    = 0.
dynCallsSP     = 0
statCallsSP    = 0
totalDynCalls  = 0
totalStatCalls = 0
fileKey        = 0
## TODO: move it into argument parser
outputFile = "pmfOutputFile-4check"

def display():
    global ratioSP
    ratioStatSP = float(statCallsSP) / float(totalStatCalls)
    ratioDynSP = float(dynCallsSP) / float(totalDynCalls)
    if verbose > 0:
        print(f"nbTrials: {nbTrials}")
        print(f"ratioStatSP: {ratioStatSP}")
        print(f"ratioDynSP: {ratioDynSP}")
        print(f"dynCallsSP: {dynCallsSP}")
        print(f"statCallsSP: {statCallsSP}")
        print(f"totalDynCalls: {totalDynCalls}")
        print(f"totalStatCalls: {totalStatCalls}")

def updateProfileCluster(jsonFile):
    global profile
    print(jsonFile)
    with open(jsonFile, 'r') as json_file:
        profile = json.load(json_file)

    return updateProfile(profile)

def updateProfile(profile, usebtsym = False):
    global totalDynCalls
    global totalStatCalls
    global correspondanceDynStatic
    slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
    btsymbolreg = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
    dynCalls = profile["IndependantCallStacks"]
    staticCalls = []
    staticCallsd = {}
    profile["StaticCalls"] = staticCalls
    profile["StaticCallsd"] = staticCallsd
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
        dynCount += 1
        ## If already in dict update CallsCount
        if staticCallsd.get(statickey):
            scs = staticCallsd[statickey]
            scs["CallsCount"] += cs["CallsCount"]
            totalDynCalls += cs["CallsCount"]
            statCountMinusOne = statCount - 1
            cs["statname"] = f"statCS-{statCountMinusOne}"
            cs["statid"] = statCountMinusOne
            correspondanceDynStatic.append(statCountMinusOne)
        ## If not already in dict
        ## Add to dict and update name/hashKey/CallsCount
        ## Append to staticCalls list
        else:
            ##Copy of Dynamic Call dictionnary into the staticCall one
            cs["statname"] = f"statCS-{statCount}"
            cs["statid"] = statCount
            correspondanceDynStatic.append(statCount)
            staticCallsd[statickey] = cs.copy()
            scs = staticCallsd[statickey]
            scs["StaticHashKey"] = statickey
            ##Change dynCall name for static one, in copy
            ##Update StatCall callsCount with dynamic one, in copy
            totalDynCalls += cs["CallsCount"]
            totalStatCalls += 1
            staticCalls.append(scs)
            statCount += 1
    if verbose > 1:
        print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in staticCalls])
        print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in dynCalls])
    return (staticCalls,dynCalls)


def getHashKeysFromIndex(ind,jsonFile):
    global profile
    with open(jsonFile, 'r') as json_file:
        profile = json.load(json_file)
    staticCalls,dynCalls = updateProfile(profile)
    hashKeys = []
    for i in ind:
        hashKeys.append(dynCalls[i]["HashKey"])
    return hashKeys

from itertools import permutations
import itertools
def getCount(subset, static, computeCalls=True):
    keys = []
    cc = 0
    if static:
        calls = profile["StaticCalls"]
        name = "statname"
    else:
        calls = profile["IndependantCallStacks"]
        name = "dynname"
    for call in calls:
        if call[name] in subset:
            if computeCalls:
                cc += call["CallsCount"]
            else:
                keys.append(call["HashKey"])
    if computeCalls:
        return cc
    else:
        return keys

def getCountCalls(subset, static):
    return getCount(subset, static, True)

def getKeys(subset, static):
    return getCount(subset, static, False)

def createStratFilesMultiSiteStatic(stratDir, jsonFile, validNameHashKeyList):
    return createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, True)

def createStratFilesMultiSiteDynamic(stratDir, jsonFile, validNameHashKeyList):
    return createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, False)

def createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, static):
    """  validNameHashKeyList
        --> COUPLE of 2 lists: (nameList, keyList)
        If static
            create one stratFile per combination. Each combination
            is a subset of the set of individuals
        else (dynamic)
            Take into account strategy found with StaticMultiSite
            create one stratFile per combination. Each combination
            is a subset of the set of individuals
    """
    def generateStratFiles(CsubsetList):
        global fileKey
        rank = 0
        CsubsetListFiles = []
        staticName = "dynamic"
        if static:
            staticName = "static"
        for csub in CsubsetList:
            rank += 1
            name = f"multiSite-{staticName}-r{rank}"
            name += f"-k{fileKey}"
            fileKey += 1
            f = f"strat-{name}.txt"
            ## csub ((name,name,), CallsCount)
            keys = getKeys(csub[0], static)
            CsubsetListFiles.append((name, keys, csub[1],csub[2]))
            if verbose>2:
                print(f"Creation of file: {f}")
            with open(stratDir+f, 'a') as ouf:
                for key in keys:
                    ouf.write(key+"\n")
        return CsubsetListFiles

    def findsubsets(s, n):
        return list(itertools.combinations(s, n))
    ## For possible size of subset composing strategies
    callsName = validNameHashKeyList[0]
    snames = set(callsName)
    os.system(f"mkdir -p {stratDir}")
    lenCallsName = len(callsName)
    for n in range(lenCallsName,0,-1):
        ## List of all subset strategies
        CsubsetList = []
        ## Compute the subsets
        subsets = findsubsets(snames, n)
        lensubsets = len(subsets)
        ## For each subset, create a strategy file
        for subset in subsets:
            ## Build subset name from all component
            #name = "_".join(list(subset))
            ## Compute score: sum of dynCalls count
            Csubset = (subset, getCountCalls(subset, static),n)
            ## Append tuple subset,score to the list
            CsubsetList.append(Csubset)
        ## Sort subsets list with score
        CsubsetList.sort(key=lambda x: x[1], reverse=True)
        ## Remove all list elements after first individual encountered
        ## Idea is to keep best individual in case all multisite don't work
        eltCounter = 0
        for e in CsubsetList:
            ## len of subset
            if len(e[0]) == 1:
                eltCounter += 1
                break
            eltCounter += 1
        CsubsetList = list(CsubsetList[0:eltCounter])
        ## Generating strategy files
        CsubsetListFiles = generateStratFiles(CsubsetList)
        ## Return list of performance ordered subset names
        yield CsubsetListFiles
    return []

def createStratFilesDynamicAfterStatic(stratDir, jsonFile, validNameHashKeyList):
    """ Hierarchical approach.
        Static analysis result are used to create test for remaining dynamic calls.
        if validNameList
         It means that this is level2: We must take into account level 1 pruning
         Thus returns stratList (name,hashkey) all individuals
         which do not contain any of the hashKey in validNameList
        else
         just return stratList of all individuals
    """
    def getStratList(readJsonProfileFile, validNameList):
        """ Returns list of name and HashKey
            name for building strategy fileName
            HashKey for writing into strategy file
        """
        staticCalls = profile["StaticCalls"]
        dynCalls = profile["IndependantCallStacks"]
        ## Return list of couples: (name,hashKey)
        ##Don't return dynamic calls containing any name in validNameList
        ## Coarse grained strat result impact finer grained strat
        validHashKeyList = validNameList[1]
        if len(validHashKeyList) < 1:
            validHashKeyList.extend(getKeys([globalBestName],level=1))
        res = []
        for x in dynCalls:
            add = True
            ## For all static call site HashKeys
            for y in validHashKeyList:
                ## if dynamic Call Site HashKey contains Static One
                if y in x["HashKey"]:
                    ## Don't add it
                    add = False
                    break
            if add:
                res.append(x)
        return [(x["dynname"],x["HashKey"]) for x in res]
    os.system(f"mkdir -p {stratDir}")
    stratList = []
    stratList = getStratList(jsonFile, validNameHashKeyList)
    n = len(stratList)
    ## No dynamic or static calls to do in Reduced Precision
    if n < 1:
        print("Best solution found.")
        exit(0)
    for (name, key) in stratList:
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            ouf.write(key+"\n")
            ##TODO: addr2lineStaticKey
            for statickey in validNameHashKeyList[1]:
                ouf.write(statickey+"\n")
    if verbose>0:
        print(f"{n} files created.")
    ## Return list of names
    return stratList

def checkFile(dynCallsd):
    """ Obsolete
    """
    backtracelistfile = ".pyflot/profile/BacktraceList.txt"
    already = set()
    with open(backtracelistfile, 'r') as inf:
        content = inf.read()
        for l in content.splitlines():
            if not dynCallsd.get(l):
                print("Error Not found",l)
            else:
                if l not in already:
                    already.add(l)

def createStratFilesStatic(stratDir, jsonFile):
    return createStratFiles(stratDir, jsonFile, True)

def createStratFilesDynamic(stratDir, jsonFile):
    return createStratFiles(stratDir, jsonFile, False)

def createStratFiles(stratDir, jsonFile, static):
    """ Static: level1
        Create strategy files, for each individual static call sites
    """
    global profile
    os.system(f"mkdir -p {stratDir}")

    with open(jsonFile, 'r') as json_file:
        profile = json.load(json_file)

    staticCalls,dynCalls = updateProfile(profile)
    if static:
        stratList = [(x["statname"],x["HashKey"],x["CallsCount"], 1) for x in staticCalls]
    else:
        stratList = [(x["dynname"],x["HashKey"],x["CallsCount"], 0) for x in dynCalls]
    n = len(stratList)
    assert n>1## at least two individual dynamic call sites
    for (name, key, dynCallsCount, statCallsCount) in stratList:
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            ouf.write(key+"\n")
    if verbose>0:
        print(f"{n} files created.")
    ## Return list of names
    return stratList

checkCount = 0
def checkTest3Exp():
    global checkCount
    if checkCount%2 == 0:
        checkCount +=1
        return True
    else:
        checkCount +=1
        return False

def checkPMF(f, checkText):
    ## Check PMF result
    res = checkText
    with open(f, "r") as inf:
        for l in inf.readlines():
            if res in l:
                return True
    return False

def runCheckScript(f, checkText):
    #return checkTest3Exp()
    return checkPMF(f, checkText)

def runApp(cmd, stratDir, name, checkText, envStr):
    global nbTrials
    global outputFile
    nbTrials += 1
    outputFileLocal = stratDir + outputFile + f"-{nbTrials}.dat"
    ## File name Should be same as in generateStrat.py
    backtrace = f"{stratDir}/strat-{name}.txt"
    os.environ["BACKTRACE_LIST"] = backtrace
    if verbose>3:
        print(f"BACKTRACE_LIST={backtrace}")
    os.environ["PRECISION_TUNER_DUMPJSON"] = f"./dumpResults-{name}.json"
    if verbose>3:
        print(f"{envStr} PRECISION_TUNER_DUMPJSON="+f"./dumpResults-{name}.json")
        print(cmd)
    os.system(cmd + f" >> {outputFileLocal}")
    valid = runCheckScript(outputFileLocal, checkText)
    if verbose>2:
        print(f"BacktraceListFile ({backtrace}) Valid? {valid}")
    return valid

def updateEnv(dumpDirectory, profileFile, binary):
    resultsDir = dumpDirectory +"./results/"
    procenv = {}
    ##TODO: use script arguments
    procenv["TARGET_FILENAME"] = binary
    procenv["PRECISION_TUNER_READJSON"] = dumpDirectory + profileFile
    procenv["PRECISION_TUNER_DUMPCSV"] = "./whocares.csv"
    procenv["PRECISION_TUNER_OUTPUT_DIRECTORY"] = resultsDir
    procenv["PRECISION_TUNER_MODE"] = "APPLYING_STRAT"
    os.system(f"mkdir -p {resultsDir}")
    envStr = "TARGET_FILENAME="
    envStr += binary
    envStr += " PRECISION_TUNER_READJSON="
    envStr += dumpDirectory
    envStr += profileFile
    envStr += " PRECISION_TUNER_DUMPCSV="
    envStr += "./whocares.csv"
    envStr += " PRECISION_TUNER_OUTPUT_DIRECTORY="
    envStr += resultsDir
    envStr += " PRECISION_TUNER_MODE=APPLYING_STRAT"
    for var,value in procenv.items():
        os.environ[var] = value
    return envStr

def __execApplication(binary, args, stratDir, stratList, checkText, dumpDirectory, profileFile, multiSite):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    global dynCallsSP
    global statCallsSP
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    envStr = updateEnv(dumpDirectory, profileFile, binary)
    _stratList = stratList
    for (name, hashKey, dynCallsCount, statCallsCount) in _stratList:
        valid = runApp(cmd, stratDir, name, checkText,envStr)
        if valid:
            if multiSite:
                dynCallsSP += dynCallsCount
                statCallsSP += statCallsCount
                return ([name],hashKey)
            else:
                validNames.append(name)
                validHashKeys.append(hashKey)
    if multiSite:
        return []
    else:
        return (validNames,validHashKeys)

def execApplication(binary, args, stratDir, stratList, checkText, dumpDirectory, profileFile):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    return __execApplication(binary, args, stratDir, stratList, checkText, dumpDirectory, profileFile, False)

def execApplicationMultiSite(binary, args, stratDir, stratList, checkText, dumpDirectory, profileFile):
    """ stratList is a list of tuple (name,hashKeys)
        GOAL: Returns best multisite solution, if not return best individual solution
    """
    return __execApplication(binary,args,stratDir,stratList, checkText, dumpDirectory, profileFile, True)
