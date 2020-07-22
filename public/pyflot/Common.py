import os
import pdb
from generateStrat import createStratFilesCluster
from generateStrat import createStratFilesMultiSite
from generateStrat import createStratFilesIndividuals
from communities import build_graph
from communities import community_algorithm
from Trial import Trial

import multiprocessing as mp

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

def worker(self, obj):
    return obj.runApp()

def clusterBFS(profile, searchSet, args, sloc, verbose):
    """ Compute Breadth First Search with clustering
    """
    Trial._profile = profile
    Trial._verbose = verbose
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
    """ Compute the Breadth First Search without clustering.
        2 steps:
                (*) Individual evaluation, done in parallel,
                each application execution is assumed to be done on one core.
                (*) MultiSite evaluation, merging all individual with success,
                sorting the list of k among n elt (for k from 2 to n) in decreasing
                impact on performance.
        Note:
            - impact on performance is assumed to be equivalent to number of calls done in
        reduced precision
            - the list is generated on the fly, each k among n at a time. We assume
            all solution or k+1 among n are better than those with k among n.
    """
    Trial._profile = profile
    Trial._verbose = verbose
    dumpdir        = args.dumpdir
    ssloc          = "sloc"
    if not sloc:
        ssloc      = "backtrace"
    stratDir       = args.dumpdir + f"/strats/{ssloc}/"
    resultsDir     = args.dumpdir + "/results/"
    scoreFile = resultsDir + "score.txt"
    if verbose > 0:
        print(f"Running BFS {ssloc}")
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
    pool = mp.Pool(min(32,len(toTestList))) ## haswell
    poolargs = []
    for (name, callSiteList) in toTestList:
        poolargs.append(Trial(cmd, stratDir, name, args.verif_text, envStr, callSiteList))
    trialsList = pool.map(worker,poolargs)
    pool.close()
    pool.join()
    ## Displaying
    validTrials = []
    for trial in trialsList:
        if trial._valid:
            trial.success(sloc)
            ## validTrials is sorted by impact on performance (because trials is)
            validTrials.append(trial)
            validDic[trial.getName()] = trial.getCallSiteList()
        else:
            trial.failure(sloc)
        trial.display(scoreFile)
    if verbose>2:
        print("Level1, Valid name list of individual-site static call sites: ", validDic)
    ## For all remaining Static Calls
    ## Sort all strategies per performance impact,
    ## start trying them from the most to the less impact.
    if len(validTrials)<1:
        return (set(),searchSet)
    if len(validTrials) < 2:
        ## take Best individual as solution
        onlyCorrectIndividual = validTrials[0]
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
            trial = runApp(cmd, stratDir, name,  args.verif_text, envStr, btCallSiteList)
            if trial._valid:
                spConvertedSet = set(btCallSiteList)
                trial.success(sloc)
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                trial.display(scoreFile)
                return (spConvertedSet,searchSet)
            else:
                trial.failure(sloc)
                trial.display(scoreFile)
    return (spConvertedSet,searchSet)
