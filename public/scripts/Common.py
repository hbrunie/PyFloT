import os
import pdb
from generateStrat import createStratFilesCluster
from generateStrat import createStratFilesMultiSite
from generateStrat import createStratFilesIndividuals
from communities import build_graph
from communities import community_algorithm
from communities import community_algorithm_mockup

verbose = 0
def getVerbose():
    return verbose

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

def runAppMockup(btCallSiteIdList, sloc=False):
    """ CallSiteId are BT or SLOC?
    """
    ## MOCKUP:TODO
    if sloc:
        for i in btCallSiteIdList:
            if i in [5]:
                return False
    else:
        for i in btCallSiteIdList:
            if i in [ 37, 38, 39, 40, 41, 42, 43, 44, 45]:
                return False
    return True

def runApp(cmd, stratDir, name, checkText, envStr, nbTrials):
    outputFile = "output"
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

def clusterBFS(profile, searchSet, params, binary, dumpdir, stratDir, sloc,
                        checkTest2Find, tracefile, threshold, maxdepth=1,windowSize=2,verbose=1):
    verbose = 3
    profile.trialNewStep()
    resultsDir = dumpdir + "/results/"
    tracefile = dumpdir + "/" + tracefile
    cmd = f"{binary} {params}"
    envStr = updateEnv(resultsDir, profile._profileFile, binary)
    ## Generate communities
    corr = None
    if sloc:
        corr = profile._correspondanceBt2SLOC
    (ge, gn) = build_graph(searchSet, tracefile, threshold, windowSize, corr)
    #com = community_algorithm(ge, gn, threshold, maxdepth)
    com = community_algorithm_mockup(gn)
    if not com:
        return (set(), searchSet)
    ## Individual analysis for BFS
    toTestList =  createStratFilesCluster(profile, stratDir, com, 0, sloc)
    if verbose>2:
        print(f"CLUSTER INDIVIDUAL SLOC?{sloc}. ToTest:", toTestList)
    ## Get the successful individual sloc/backtrace based call sites
    validDic = {}
    for (name, btCallSiteList) in toTestList:
        valid = runAppMockup(btCallSiteList, sloc)
        #valid = runApp(cmd, stratDir, name, checkTest2Find, envStr, profile._nbTrials)
        if valid:
            validDic[name] = btCallSiteList
            profile.trialSuccessIndivCluster(btCallSiteList, sloc)
            ## Revert success because we testing individual
            profile.display()
        else:
            profile.trialFailure()
            profile.display()
    ## E.g. (['depth-0-community-1'], [ ['0x5ead72', '0x5e913e'] ])
    if verbose>2:
        print(f"CLUSTER INDIVIDUAL SLOC?{sloc}. Valid keys:", validDic.keys())
    ## If no valid individual found no need for multisite, return
    if len(validDic.keys())<1:
        return (set(),searchSet)
    if len(validDic.keys()) < 2:
        ## take Best individual as solution
        onlyCorrectIndividual = list(validDic.values())[0]
        spConvertedSet = set(onlyCorrectIndividual)
        searchSet = searchSet - spConvertedSet
        return (spConvertedSet,searchSet)
    toTestListGen = createStratFilesMultiSite(profile, stratDir, validDic, sloc)
    assert(toTestListGen)
    ## Execute the application on generated strategy files
    ## Generate strategies choosing k among n.
    ## Analyze k-strategies before generating strategies for the next k.
    toStop = True
    while toStop:
        try:
            toTestList = next(toTestListGen)
        except StopIteration:
            print(f"No more strategy to test.")
            break
        if verbose>2:
            print(f"CLUSTER MULTI SET SLOC?{sloc}. To Test List:", toTestList)
        for (name, btCallSiteList) in toTestList:
            #valid = runApp(cmd, stratDir, name,  checkTest2Find, envStr, profile._nbTrials, btCallSiteList)
            valid = runAppMockup(btCallSiteList, sloc)
            if valid:
                spConvertedSet = set(btCallSiteList)
                profile.trialSuccessMultiSiteCluster(btCallSiteList,sloc)
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                profile.display()
                return (spConvertedSet,searchSet)
            else:
                profile.trialFailure()
                profile.display()
    return (spConvertedSet,searchSet)

def BFS(profile, searchSet, params, binary, dumpdir, stratDir, checkText2Find, verbose, sloc):
    """
    """
    profile.trialNewStep()
    resultsDir          = dumpdir + "/results/"
    readJsonProfileFile = dumpdir + profile._profileFile
    cmd = f"{binary} {params}"
    envStr = updateEnv(resultsDir, profile._profileFile, binary)
    ## SLOC CallSite identification (1 level CallStack)
    toTestList = createStratFilesIndividuals(profile, stratDir, searchSet, sloc)
    if verbose >2:
        print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
    ## Get the successful individual static call sites
    validDic = {}
    for (name, CallSiteList) in toTestList:
        valid = runAppMockup(CallSiteList, sloc)
        #valid = runApp(cmd, stratDir, name, checkText2Find, envStr, profile._nbTrials, btCallSiteList)
        if valid:
            validDic[name] = CallSiteList
            profile.trialSuccessIndivBFS(CallSiteList, sloc)
            ## Revert success because we testing individual
            profile.display()
        else:
            profile.trialFailure()
            profile.display()
    if verbose>2:
        print("Level1, Valid name list of individual-site static call sites: ", validDic)
    ## For all remaining Static Calls
    ## Sort all strategies per performance impact,
    ## start trying them from the most to the less impact.
    if len(validDic.keys())<1:
        return (set(),searchSet)
    if len(validDic.keys()) < 2:
        ## take Best individual as solution
        onlyCorrectIndividual = list(validDic.values())[0]
        spConvertedSet = set(onlyCorrectIndividual)
        searchSet = searchSet - spConvertedSet
        return (spConvertedSet,searchSet)
    toTestListGen = createStratFilesMultiSite(profile, stratDir, validDic, sloc)
    assert(toTestListGen)
    ## Execute the application on generated strategy files
    ## Generate strategies choosing k among n.
    ## Analyze k-strategies before generating strategies for the next k.
    toStop = True
    while toStop:
        try:
            toTestList = next(toTestListGen)
        except StopIteration:
            print("No more strategy to test.")
            break
        if verbose>2:
            print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])
        for (name, btCallSiteList) in toTestList:
            #valid = runApp(cmd, stratDir, name,  checkText2Find, envStr, profile._nbTrials, btCallSiteList)
            valid = runAppMockup(btCallSiteList,sloc)
            if valid:
                spConvertedSet = set(btCallSiteList)
                profile.trialSuccessMultiSiteBFS(btCallSiteList, sloc)
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                profile.display()
                return (spConvertedSet,searchSet)
            else:
                profile.trialFailure()
                profile.display()
    return (spConvertedSet,searchSet)
