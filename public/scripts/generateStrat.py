import json
import os
import re

profile = {}
globalBestName = None
verbose = 3
def getVerbose():
    return verbose

nbTrials = 0
ratioDynSP = 0.
ratioStatSP = 0.
dynCallsSP = 0
statCallsSP = 0
totalDynCalls = 0
totalStatCalls = 0

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

def getDynCalls(k):
    return 0

def updateProfile(profile):
    global totalDynCalls
    global totalStatCalls
    #regex = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
    regex = "([a-zA-Z_0-9]+)\\+([a-f0-9x]+)"
    dynCalls = profile["IndependantCallStacks"]
    staticCalls = []
    staticCallsd = {}
    profile["StaticCalls"] = staticCalls
    profile["StaticCallsd"] = staticCallsd
    maxlvl = 4 #16
    count = 0
    for cs in dynCalls:
        count += 1
        cs["name"] = f"dynCS-{count}"
        key = ""
        ## Build Static Key with 4 backtrace lvl
        for callstack in  cs["CallStack"][:maxlvl]:
            m = re.search(regex, callstack)
            if not m:
                break
            key += m.group(1) + m.group(2)
        ## If already in dict update CallsCount
        if staticCallsd.get(key):
            scs = staticCallsd[key]
            scs["CallsCount"] += cs["CallsCount"]
            totalDynCalls += cs["CallsCount"]
        ## If not already in dict
        ## Add to dict and update name/hashKey/CallsCount
        ## Append to staticCalls list
        else:
            ##Copy of Dynamic Call dictionnary into the staticCall one
            staticCallsd[key] = cs.copy()
            scs = staticCallsd[key]
            scs["HashKey"] = key
            ##Change dynCall name for static one, in copy
            scs["name"] = f"statCS-{count}"
            ##Update StatCall callsCount with dynamic one, in copy
            totalDynCalls += cs["CallsCount"]
            totalStatCalls += 1
            staticCalls.append(scs)
    if verbose > 1:
        print("Profile: ",[(x["name"],x["CallsCount"]) for x in staticCalls])
        print("Profile: ",[(x["name"],x["CallsCount"]) for x in dynCalls])
    return (staticCalls,dynCalls)



from itertools import permutations
import itertools
def getCountCalls(subset, static):
    cc = 0
    if static:
        calls = profile["StaticCalls"]
    else:
        calls = profile["IndependantCallStacks"]
    for dc in calls:
        if dc["name"] in subset:
            cc += dc["CallsCount"]
    return cc

def getKeys(csub, static):
    keys = []
    if static:
        calls = profile["StaticCalls"]
    else:
        calls = profile["IndependantCallStacks"]
    for ics in calls:
        n = ics["name"]
        if n in csub:
            keys.append(ics["HashKey"])
    return keys

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
    def findsubsets(s, n):
        return list(itertools.combinations(s, n))
    ## List of all subset strategies
    CsubsetList = []
    ## For possible size of subset composing strategies
    callsName = validNameHashKeyList[0]
    snames = set(callsName)
    os.system(f"mkdir -p {stratDir}")
    lenCallsName = len(callsName)
    print(f"Do createStratFilesMultiSiteDynamic {lenCallsName}")
    for n in range(1,lenCallsName+1):
        ## Compute the subsets
        print(f"n: {n}, do findsubsets")
        subsets = findsubsets(snames, n)
        print(f"n: {n}, findsubsets done")
        lensubsets = len(subsets)
        ## For each subset, create a strategy file
        print(f"do For each subsets({lensubsets})")
        for subset in subsets:
            ## Build subset name from all component
            #name = "_".join(list(subset))
            ## Compute score: sum of dynCalls count
            Csubset = (subset, getCountCalls(subset, static),n)
            ## Append tuple subset,score to the list
            CsubsetList.append(Csubset)
        print(f"For each subsets({lensubsets}) DONE")
    print(f"createStratFilesMultiSiteDynamic {lenCallsName} DONE")
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
    rank = 0
    CsubsetListFiles = []
    staticName = "dynamic"
    if static:
        staticName = "static"
    for csub in CsubsetList:
        rank += 1
        name = f"multiSite-{staticName}-r{rank}"
        for n in csub[0]:
            name += f"-{n}"
        f = f"strat-{name}.txt"
        ## csub ((name,name,), CallsCount)
        keys = getKeys(csub[0], static)
        CsubsetListFiles.append((name, keys, csub[1],csub[2]))
        if verbose>2:
            print(f"Creation of file: {f}")
        with open(stratDir+f, 'a') as ouf:
            for key in keys:
                ouf.write(key+"\n")
    ## Return list of performance ordered subset names
    return CsubsetListFiles

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
        return [(x["name"],x["HashKey"]) for x in res]
    global bestIndividual
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
            for statickey in validNameHashKeyList[1]:
                ouf.write(statickey+"\n")
    if verbose>0:
        print(f"{n} files created.")
    ## Return list of names
    return stratList

def checkFile(dynCallsd):
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
        stratList = [(x["name"],x["HashKey"],x["CallsCount"], 1) for x in staticCalls]
    else:
        stratList = [(x["name"],x["HashKey"],x["CallsCount"], 0) for x in dynCalls]
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

def checkPMF(f):
    ## Check PMF result
    res = "AMReX (20.01-36-gfee20d598e0a-dirty) finalized"
    with open(f, "r") as inf:
        for l in inf.readlines():
            if res in l:
                return True
    return False

def runCheckScript(f):
    return checkPMF(f)

def runApp(cmd, stratDir, name):
    global nbTrials
    global outputFile
    nbTrials += 1
    outputFileLocal = outputFile + f"-{nbTrials}.dat"
    ## File name Should be same as in generateStrat.py
    backtrace = f"{stratDir}/strat-{name}.txt"
    os.environ["BACKTRACE_LIST"] = backtrace
    os.environ["PRECISION_TUNER_DUMPJSON"] = f"./dumpResults-{name}.json"
    os.system(cmd + f" >> {outputFileLocal}")
    valid = runCheckScript(outputFileLocal)
    if verbose>2:
        print(f"BacktraceListFile ({backtrace}) Valid? {valid}")
    return valid

def updateEnv():
    resultsDir = "./.pyflot/results/"
    procenv = {}
    ##TODO: use script arguments
    procenv["PRECISION_TUNER_READJSON"] = "./.pyflot-1ite/profile.json"
    procenv["PRECISION_TUNER_DUMPCSV"] = "./whocares.csv"
    procenv["PRECISION_TUNER_OUTPUT_DIRECTORY"] = resultsDir
    procenv["PRECISION_TUNER_MODE"] = "APPLYING_STRAT"
    os.system(f"mkdir -p {resultsDir}")
    for var,value in procenv.items():
        os.environ[var] = value

def __execApplication(binary, args, stratDir, stratList, multiSite=False):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    global dynCallsSP
    global statCallsSP
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    updateEnv()
    if multiSite:
        ## Go through [0:n-1] in list
        ## Because last element is best valid individual
        _stratList = stratList[:-1]
    else:
        _stratList = stratList
    for (name, hashKey, dynCallsCount, statCallsCount) in _stratList:
        valid = runApp(cmd, stratDir, name)
        if valid:
            if multiSite:
                dynCallsSP += dynCallsCount
                statCallsSP += statCallsCount
                return ([name],hashKey)
            else:
                validNames.append(name)
                validHashKeys.append(hashKey)
    ## Choose best individual
    if multiSite:
        elt = stratList[-1]
        dynCallsSP += elt[2]
        ## Only one because it is not multi site: best individual
        statCallsSP += 1
        return ([elt[0]],elt[1])
    else:
        return (validNames,validHashKeys)

def execApplication(binary, args, stratDir, stratList):#, multiSite=False):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    return __execApplication(binary,args,stratDir,stratList,False)

def execApplicationMultiSite(binary, args, stratDir, stratList):
    """ stratList is a list of tuple (name,hashKeys)
        GOAL: Returns best multisite solution, if not return best individual solution
    """
    return __execApplication(binary,args,stratDir,stratList,True)
