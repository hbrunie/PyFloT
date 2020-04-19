import json
import pdb
import os
import re
from itertools import permutations
import itertools

verbose = 0

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

def createStratFilesMultiSiteSLOC(stratDir, jsonFile, validNameHashKeyList):
    return createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, True)

def createStratFilesMultiSiteBacktrace(stratDir, jsonFile, validNameHashKeyList):
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
