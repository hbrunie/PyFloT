import os
import pdb
from generateStrat import createStratFilesCluster
from generateStrat import createStratFilesMultiSite
from generateStrat import createStratFilesIndividuals
from communities import build_graph
from communities import community_algorithm

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

def runAppMockup(btCallSiteIdList, sloc=False, dim=1):
    """ CallSiteId are BT or SLOC?
    """
    ## MOCKUP:TODO
    if sloc:
        for i in btCallSiteIdList:
            if i in [3]:
                return False
    else:
        for i in btCallSiteIdList:
            if dim ==2:
                if i in [64, 65, 66, 67, 68, 69, 70, 71, 76, 77, 78, 79]:
                    return False
            if dim == 1:
                if i in [21,22,23]:
                    return False
    return True

def runApp(cmd, stratDir, name, checkText, envStr, nbTrials):
    outputFile = "output"
    outputFileLocal = stratDir + outputFile + f"-{nbTrials}"
    ## File name Should be same as in generateStrat.py
    backtrace = f"{stratDir}/strat-{name}.txt"
    os.environ["BACKTRACE_LIST"] = backtrace
    if verbose>3:
        print(f"BACKTRACE_LIST={backtrace} " + f"{envStr} PRECISION_TUNER_DUMPJSON="+f"./dumpResults-{name}.json")
    os.environ["PRECISION_TUNER_DUMPJSON"] = f"./dumpResults-{name}.json"
    if verbose>3:
        print(f"{envStr} PRECISION_TUNER_DUMPJSON="+f"./dumpResults-{name}.json")
        print(cmd)
    os.system(cmd + f" 1>> {outputFileLocal}.out 2>> {outputFileLocal}.err")
    valid = runCheckScript(outputFileLocal+".out", checkText)
    if verbose>2:
        print(f"BacktraceListFile ({backtrace}) Valid? {valid}")
    return valid

def updateEnv(resultsDir, profileFile, binary, verbose):
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
        if verbose>3:
            print(f"{var}={value}")
    return envStr

def clusterBFS(profile, searchSet, args, sloc, verbose):
    profile.trialNewStep()
    ssloc = "sloc"
    if not sloc:
        ssloc      = "backtrace"
    if verbose > 0:
        print(f"Running Cluster BFS {ssloc} filtered?",args.filtering)
    stratDir   = args.dumpdir + f"/strats/{ssloc}WithClustering/"
    resultsDir = args.dumpdir + "/results/"
    tracefile  = args.readdir + "/" + args.mergedtracefile
    threshold  = args.threshold
    windowSize = args.windowSize
    maxdepth   = args.maxdepth
    cmd = f"{args.binary} {args.params}"
    envStr = updateEnv(resultsDir, profile._profileFile, args.binary, verbose)
    ## Generate communities
    corr = None
    if not sloc and args.filtering:#BT cluster + filtering with SLOC cluster
        ## Convert bt call sites into sloc call sites from search set
        slocSearchSet = profile.convertBt2SlocSearchSet(searchSet)
        ## apply community algorithm to searchSet
        corr = profile._correspondanceBt2SLOC
        (ge, gn) = build_graph(slocSearchSet, tracefile, threshold, windowSize, corr)
        slocCom = community_algorithm(ge, gn, threshold, maxdepth,verbose)
        ## Convert back communities to backtrace CallSites
        if not slocCom:
            return (set(), searchSet)
        com = profile.convertSloc2BtCommunity(slocCom)
        comList = []
        for localSearchSet in com:
            localSearchSet = set(localSearchSet)
            #pdb.set_trace()
            (ge, gn) = build_graph(localSearchSet, tracefile, threshold, windowSize, corr)
            com = community_algorithm(ge, gn, threshold, maxdepth,verbose)
            comList.extend(list(com))
        com = comList
        com=tuple(comList)
    else:
        if sloc:
            corr = profile._correspondanceBt2SLOC
        (ge, gn) = build_graph(searchSet, tracefile, threshold, windowSize, corr)
        com = community_algorithm(ge, gn, threshold, maxdepth,verbose)
    if not com:
        return (set(), searchSet)
    ## Individual analysis for BFS
    toTestList =  createStratFilesCluster(profile, stratDir, com, 0, sloc)
    if verbose>2:
        print(f"CLUSTER INDIVIDUAL SLOC?{sloc}. ToTest:", toTestList)
    ## Get the successful individual sloc/backtrace based call sites
    validDic = {}
    for (name, btCallSiteList) in toTestList:
        valid = runApp(cmd, stratDir, name, args.verif_text, envStr, profile._nbTrials)
        if valid:
            validDic[name] = btCallSiteList
            profile.trialReverse(sloc)
            profile.trialSuccess(btCallSiteList, sloc,True)
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
            valid = runApp(cmd, stratDir, name,  args.verif_text, envStr, profile._nbTrials)
            if valid:
                spConvertedSet = set(btCallSiteList)
                profile.trialReverse(sloc)
                profile.trialSuccess(btCallSiteList,sloc)
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                profile.display()
                return (spConvertedSet,searchSet)
            else:
                profile.trialFailure()
                profile.display()
    return (spConvertedSet,searchSet)

def BFS(profile, searchSet, args, sloc, verbose):
    """
    """
    dumpdir        = args.dumpdir
    ssloc          = "sloc"
    if not sloc:
        ssloc      = "backtrace"
    stratDir       = args.dumpdir + f"/strats/{ssloc}/"
    resultsDir     = args.dumpdir + "/results/"
    if verbose > 0:
        print(f"Running BFS {ssloc}")
    profile.trialNewStep()
    readJsonProfileFile = dumpdir + profile._profileFile
    cmd = f"{args.binary} {args.params}"
    if verbose > 2:
        print("command",cmd)
    envStr = updateEnv(resultsDir, profile._profileFile, args.binary, verbose)
    ## SLOC CallSite identification (1 level CallStack)
    toTestList = createStratFilesIndividuals(profile, stratDir, searchSet, sloc)
    if verbose >2:
        print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
    ## Get the successful individual static call sites
    validDic = {}
    for (name, CallSiteList) in toTestList:
        valid = runApp(cmd, stratDir, name, args.verif_text, envStr, profile._nbTrials)
        if valid:
            validDic[name] = CallSiteList
            profile.trialReverse(sloc)
            profile.trialSuccess(CallSiteList, sloc, True)
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
            valid = runApp(cmd, stratDir, name,  args.verif_text, envStr, profile._nbTrials)
            if valid:
                spConvertedSet = set(btCallSiteList)
                profile.trialSuccess(btCallSiteList, sloc)
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                profile.display()
                return (spConvertedSet,searchSet)
            else:
                profile.trialFailure()
                profile.display()
    return (spConvertedSet,searchSet)
