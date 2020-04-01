import json
import os
import re

profile = {}
globalBestName = None
verbose = 3

def updateProfile(profile):
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
            scs["CallsCount"] += cs["CallsCount"]
            staticCalls.append(scs)
    return (staticCalls,dynCalls)



from itertools import permutations
import itertools
def getCountCalls(subset, level):
    cc = 0
    if level == 1:
        calls = profile["StaticCalls"]
    else:
        calls = profile["IndependantCallStacks"]
    for dc in calls:
        if dc["name"] in subset:
            cc += dc["CallsCount"]
    return cc

def getKeys(csub, level):
    keys = []
    if level == 1:
        calls = profile["StaticCalls"]
    else:
        calls = profile["IndependantCallStacks"]
    for ics in calls:
        n = ics["name"]
        if n in csub:
            keys.append(ics["HashKey"])
    return keys

def createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, level):
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
    callsName = validNameHashKeyList[0]
    snames = set(callsName)
    def findsubsets(s, n):
        return list(itertools.combinations(s, n))
    ## List of all subset strategies
    CsubsetList = []
    ## For possible size of subset composing strategies
    for n in range(1,len(callsName)+1):
        ## Compute the subsets
        subsets = findsubsets(snames, n)
        ## For each subset, create a strategy file
        for subset in subsets:
            ## Build subset name from all component
            #name = "_".join(list(subset))
            ## Compute score: sum of dynCalls count
            Csubset = (subset, getCountCalls(subset, level))
            ## Append tuple subset,score to the list
            CsubsetList.append(Csubset)
    ## Sort subsets list with score
    CsubsetList.sort(key=lambda x: x[1], reverse=True)
    ## Remove all list elements after first individual encountered
    eltCounter = 0
    for e in CsubsetList:
        ## len of subset
        if len(e[0]) == 1:
            eltCounter += 1
            break
        eltCounter += 1
    CsubsetList = list(CsubsetList[0:eltCounter])
    os.system(f"mkdir -p {stratDir}")
    rank = 0
    CsubsetListFiles = []
    for csub in CsubsetList:
        rank += 1
        name = f"multiSite-{level}-r{rank}"
        for n in csub[0]:
            name += f"-{n}"
        f = f"strat-{name}.txt"
        ## csub ((name,name,), CallsCount)
        keys = getKeys(csub[0],level)
        CsubsetListFiles.append((name, keys))
        print(f)
        with open(stratDir+f, 'a') as ouf:
            for key in keys:
                ouf.write(key+"\n")
    ## Return list of performance ordered subset names
    return CsubsetListFiles

def createStratFilesLvl2(stratDir, jsonFile, validNameHashKeyList):
    """ if validNameList
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
    #print(stratList)
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
                print("Not found")
                print (l)
            else:
                if l in already:
                    print(l)
                else:
                    already.add(l)

def createStratFiles(stratDir, jsonFile, static=True):
    if static:
        createStratFiles

def createStratFilesDynamic(stratDir, jsonFile):
    """ Static: level1
        Create strategy files, for each individual static call sites
    """
    global profile
    os.system(f"mkdir -p {stratDir}")

    with open(jsonFile, 'r') as json_file:
        profile = json.load(json_file)
    staticCalls,dynCalls = updateProfile(profile)
    stratList = [(x["name"],x["HashKey"]) for x in dynCalls]
    n = len(stratList)
    assert n>1## at least two individual dynamic call sites
    for (name, key) in stratList:
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            ouf.write(key+"\n")
    print(f"{n} files created.")
    ## Return list of names
    return stratList

def createStratFilesLvl1(stratDir, jsonFile):
    """ Static: level1
        Create strategy files, for each individual static call sites
    """
    global profile
    os.system(f"mkdir -p {stratDir}")

    with open(jsonFile, 'r') as json_file:
        profile = json.load(json_file)
    staticCalls,dynCalls = updateProfile(profile)
    stratList = [(x["name"],x["HashKey"]) for x in staticCalls]
    n = len(stratList)
    assert n>1## at least two individual static call sites
    for (name, key) in stratList:
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            ouf.write(key+"\n")
    print(f"{n} files created.")
    ## Return list of names
    return stratList

checkCount = 0
def runCheckScript():
    global checkCount
    if checkCount%2 == 0:
        checkCount +=1
        return True
    else:
        checkCount +=1
        return False

def runApp(cmd, stratDir, name):
    ## File name Should be same as in generateStrat.py
    backtrace = f"{stratDir}/strat-{name}.txt"
    os.environ["BACKTRACE_LIST"] = backtrace
    os.environ["PRECISION_TUNER_DUMPJSON"] = f"./dumpResults-{name}.json"
    #print(f"execute {name}",backtrace,cmd)
    os.system(cmd)
    valid = runCheckScript()
    if verbose>2:
        print(f"BacktraceListFile ({backtrace}) Valid? {valid}")
    return valid

def updateEnv():
    resultsDir = "./.pyflot/results/"
    procenv = {}
    procenv["PRECISION_TUNER_READJSON"] = "./.pyflot/profile/profile.json"
    procenv["PRECISION_TUNER_DUMPCSV"] = "./whocares.json"
    procenv["PRECISION_TUNER_OUTPUT_DIRECTORY"] = resultsDir
    procenv["PRECISION_TUNER_MODE"] = "APPLYING_STRAT"
    os.system(f"mkdir -p {resultsDir}")
    for var,value in procenv.items():
        os.environ[var] = value

def execApplication(binary, args, stratDir, stratList, level, multiSite=False):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    updateEnv()
    for (name,hashKey) in stratList:
        valid = runApp(cmd, stratDir, name)
        if valid:
            if multiSite:
                return ([name],hashKey)
            validNames.append(name)
            validHashKeys.append(hashKey)
    return (validNames,validHashKeys)

def execApplicationMultiSiteLvl1(binary, args, stratDir, stratList):
    """ stratList is a list of tuple (name,hashKeys)
        GOAL: Returns best multisite solution, if not return best individual solution
    """
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    updateEnv()
    ## Go through [0:n-1] in list
    ## Because last element is best valid individual
    for (name,hashKey) in stratList[:-1]:
        valid = runApp(cmd, stratDir, name)
        if valid:
            return ([name],hashKey)
    return (validNames,validHashKeys)

def  execApplicationIndividualLvl1(binary, args, stratDir, stratList):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    updateEnv()
    for (name,hashKey) in stratList:
        valid = runApp(cmd, stratDir, name)
        if valid:
            validNames.append(name)
            validHashKeys.append(hashKey)
    bestScore = -1
    print(validNames)
    for name in validNames:
        score = getCountCalls(name, 1)
        if score > bestScore:
            globalBestName = name
            bestScore = score
    print("BEST individidual",globalBestName)
    return (validNames,validHashKeys)

def execApplicationMultiSiteLvl1(binary, args, stratDir, stratList):
    """ stratList is a list of tuple (name,hashKeys)
        GOAL: Returns best multisite solution, if not return best individual solution
    """
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    updateEnv()
    ## Go through [0:n-1] in list
    ## Because last element is best valid individual
    for (name,hashKey) in stratList[:-1]:
        valid = runApp(cmd, stratDir, name)
        if valid:
            return (name,hashKey)
    return stratList[-1]
