import json
import pdb
import os
import re

profile = {}
globalBestName = None
verbose = 3
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
        print(f"ratioStatSP: {ratioStatSP*100:2.0f}")
        print(f"ratioDynSP: {ratioDynSP*100:2.0f}")
        print(f"dynCallsSP: {dynCallsSP}")
        print(f"statCallsSP: {statCallsSP}")
        print(f"totalDynCalls: {totalDynCalls}")
        print(f"totalStatCalls: {totalStatCalls}")

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
    """ subset is a set of names ...
        #TODO USE id ! integer.
    """
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

def createStratFilesCluster(profile, stratDir, communities, depth, sloc):
    """ Always return under form of BtId
        community is a set of btCallSite ID
        communities: ({0, 1, 2, 3, 4}, {5, 6})
    """
    stratList = []
    os.system(f"mkdir -p {stratDir}")
    for counter,community in enumerate(communities):
        ##build community name
        name = f"depth-{depth}-community-{counter}"
        stratList.append((name, community))
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            hashKeyList = profile.getHashKeyList(community, sloc)
            for key in hashKeyList:
                ouf.write(key+"\n")
                #TODO: check this is the right keys ...
    ##Sort the strategy to test by performance weight: x: (name, community)
    if sloc:
        stratList.sort(key=lambda x: profile.clusterslocweight(x[1]), reverse=True)
    else:
        stratList.sort(key=lambda x: profile.clusterbtweight(x[1]), reverse=True)
    if verbose>0:
        n=len(communities)
        print(f"{n} files created.")
    ## Return list of tuples (names, community)
    return stratList

def createStratFilesMultiSite(profile, stratDir, validDic, sloc):
    """ validDic: {'depth-0-community-0': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
    """
    os.system(f"mkdir -p {stratDir}")
    nameList = validDic.keys()
    nameSet = set(nameList)
    approachName = "backtrace"
    if sloc:
        approachName = "SLOC"
    N = len(nameList)
    for n in range(N,1,-1):
        ## List of all subset strategies
        ## Compute the subsets
        namesubsets = list(itertools.combinations(nameSet, n))
        couplesubsets = []
        ##sort subsets according to weight
        for namesubset in namesubsets:
            btIdList = []
            for name in namesubset:
                btIdList.extend(validDic[name])
            couplesubsets.append((list(namesubset), btIdList))
        if sloc:
            couplesubsets.sort(key= lambda x: profile.clusterslocweight(x[1]), reverse=True)
        else:
            couplesubsets.sort(key= lambda x: profile.clusterbtweight(x[1]), reverse=True)
        for key,couplesubset in enumerate(couplesubsets):
            name = f"multiSite-{approachName}-i{key}-k{n}-among{N}"
            f = f"strat-{name}.txt"
            with open(stratDir+f, 'a') as ouf:
                ##If sloc: need to convert btCallSite ID into slocCallSite ID for getHashKeyList
                ##TODO not needed anymore
                CallSiteIdSet = couplesubset[1]
                if sloc:
                    CallSiteIdSet = set()
                    for x in couplesubset[1]:
                        CallSiteIdSet.add(profile._correspondanceBt2SLOC[x])
                keys = profile.getHashKeyList(CallSiteIdSet, sloc)
                for key in keys:
                    ouf.write(key+"\n")
        ## Return list of performance ordered subset names
        yield couplesubsets
    ## Generating strategy files: do not generate best individual
    print("No MultiStrategy found. Back to best individual strategy.")
    return []

def createStratFilesMultiSiteStatic(stratDir, jsonFile, validNameHashKeyList):
    return createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, True)

def createStratFilesMultiSiteDynamic(stratDir, jsonFile, validNameHashKeyList):
    return createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, False)

def createStratFilesIndividuals(profile, stratDir, searchSet, sloc):
    """ Static: level1
        Create strategy files, for each individual SLOC or BT call sites
    """
    stratList = []
    os.system(f"mkdir -p {stratDir}")
    ## CallSiteId represents slocCallSiteId if sloc, else btCallSiteId
    if sloc:
        searchList = list(searchSet)
        searchList.sort(key= lambda x: profile.slocweight(x), reverse=True)
    else:
        searchList = list(searchSet)
        searchList.sort(key= lambda x: profile.btweight(x), reverse=True)
    for CallSiteId in searchList:
        ## CallSiteId represents slocCallSiteId if sloc, else btCallSiteId
        if sloc:
            name = f"sloc-{CallSiteId}"
        else:
            name = f"bt-{CallSiteId}"
        stratList.append((name, [CallSiteId]))
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            ##TODO: be  sure CallSiteId is btCallSite ID and not slocCallSite ID
            hashKeyList = profile.getHashKeyList([CallSiteId], sloc)
            for key in hashKeyList:
                ouf.write(key+"\n")
    if verbose>0:
        n = len(stratList)
        print(f"{n} files created.")
    ## Return list of tuples (names, community)
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

def updateEnv(resultsDir, profileFile, binary):
    procenv = {}
    ##TODO: use script arguments
    procenv["TARGET_FILENAME"] = binary
    ##TODO: why need profileFile to apply strategy (libC++)?
    procenv["PRECISION_TUNER_READJSON"] = profileFile
    ##TODO change with real csv filename
    procenv["PRECISION_TUNER_DUMPCSV"] = "./whocares.csv"
    procenv["PRECISION_TUNER_OUTPUT_DIRECTORY"] = resultsDir
    procenv["PRECISION_TUNER_MODE"] = "APPLYING_STRAT"
    os.system(f"mkdir -p {resultsDir}")
    envStr = "TARGET_FILENAME="
    envStr += binary
    envStr += " PRECISION_TUNER_READJSON="
    envStr += profileFile
    envStr += " PRECISION_TUNER_DUMPCSV="
    envStr += "./whocares.csv"
    envStr += " PRECISION_TUNER_OUTPUT_DIRECTORY="
    envStr += resultsDir
    envStr += " PRECISION_TUNER_MODE=APPLYING_STRAT"
    for var,value in procenv.items():
        os.environ[var] = value
    return envStr

def __execApplication(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile, multiSite):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    global dynCallsSP
    global statCallsSP
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    envStr = updateEnv(resultsDirectory, profileFile, binary)
    _stratList = stratList
    ##TODO: here we need dynCallsCount and statCallsCount from stratList
    ## Only because we compute the SCORE of solution.
    ## SCORE should be computed in separated function elsewhere.
    for (name, hashKey, dynCallsCount, statCallsCount) in _stratList:
        valid = runApp(cmd, stratDir, name, checkText,envStr)
        if valid:
            if multiSite:
                ##TODO: why making sum?
                ## Will it sum over several multisite strat tested, and count the invalid one too?
                #dynCallsSP += dynCallsCount
                #statCallsSP += statCallsCount
                dynCallsSP = max(dynCallsSP,dynCallsCount)
                statCallsSP = max(statCallsSP,statCallsCount)
                display()
                return ([name],hashKey)
            else:
                dynCallsSP = max(dynCallsSP,dynCallsCount)
                statCallsSP = max(statCallsSP,statCallsCount)
                validNames.append(name)
                validHashKeys.append(hashKey)
            display()
    if multiSite:
        return []
    else:
        return (validNames,validHashKeys)

def execApplication(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    return __execApplication(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile, False)

def execApplicationMultiSite(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile):
    """ stratList is a list of tuple (name,hashKeys)
        GOAL: Returns best multisite solution, if not return best individual solution
    """
    return __execApplication(binary,args,stratDir,stratList, checkText, resultsDirectory, profileFile, True)
