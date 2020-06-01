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

def worker(obj):
    return obj.runApp()

def execute(toTestList, args, verbose):
    pool = mp.Pool(min(1,len(toTestList))) ## haswell
    poolargs = []
    for (name, callSiteList) in toTestList:
        args.name = name
        args.callSiteList = callSiteList
        poolargs.append(Trial(args,verbose))
    #trialsList = [worker(x) for x in poolargs]
    trialsList = pool.map(worker,poolargs)
    pool.close()
    pool.join()
    return trialsList

def clusterBFS(profile, searchSet, args, sloc, verbose):
    """ Compute Breadth First Search with clustering
    """
    Trial._profile = profile
    Trial._verbose = verbose
    tracefile  = args.readdir + "/" + args.mergedtracefile
    threshold  = args.threshold
    windowSize = args.windowSize
    maxdepth   = args.maxdepth
    ssloc          = "sloc"
    if not sloc:
        ssloc      = "backtrace"
    if verbose > 0:
        print(f"Running BFS {ssloc}")
    args.stratDir = args.dumpdir + f"/strats/{ssloc}/"
    args.sloc = sloc
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
    trialsList = execute(toTestList, args, verbose)
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
        trial.display()
    ## E.g. (['depth-0-community-1'], [ ['0x5ead72', '0x5e913e'] ])
    if verbose>2:
        print(f"CLUSTER INDIVIDUAL SLOC?{sloc}. Valid keys:", validDic.keys())
    ## If no valid individual found no need for multisite, return
    if len(validDic.keys())<1:
        return (set(),searchSet)
    ## take Best individual as solution
    onlyCorrectIndividual = list(validDic.values())[0]
    spConvertedSet = set(onlyCorrectIndividual.getCallSiteList())
    if len(validDic.keys()) < 2:
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
        trialsList = execute(toTestList, args, verbose)
        validTrials = []
        for trial in trialsList:
            if trial._valid:
                trial.success(sloc)
                spConvertedSet = set(trial.getCallSiteList())
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                trial.display()
                return (spConvertedSet,searchSet)
            else:
                trial.failure(sloc)
                trial.display()
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
    ## SLOC CallSite identification (1 level CallStack)
    ssloc          = "sloc"
    if not sloc:
        ssloc      = "backtrace"
    if verbose > 0:
        print(f"Running BFS {ssloc}")
    args.stratDir = args.dumpdir + f"/strats/{ssloc}/"
    args.sloc = sloc
    toTestList = createStratFilesIndividuals(profile, args.stratDir, searchSet, sloc)
    if verbose >2:
        print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
    ## Get the successful individual static call sites
    validDic = {}
    trialsList = execute(toTestList, args, verbose)
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
        trial.display()
    if verbose>2:
        print("Level1, Valid name list of individual-site static call sites: ", validDic)
    ## For all remaining Static Calls
    ## Sort all strategies per performance impact,
    ## start trying them from the most to the less impact.
    if len(validTrials)<1:
        return (set(),searchSet)
    onlyCorrectIndividual = validTrials[0]
    spConvertedSet = set(onlyCorrectIndividual.getCallSiteList())
    if len(validTrials) < 2:
        ## take Best individual as solution
        searchSet = searchSet - spConvertedSet
        return (spConvertedSet,searchSet)
    toTestListGen = createStratFilesMultiSite(profile, args.stratDir, validDic, sloc)
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
        trialsList = execute(toTestList, args, verbose)
        validTrials = []
        for trial in trialsList:
            if trial._valid:
                trial.success(sloc)
                spConvertedSet = set(trial.getCallSiteList())
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                trial.display()
                return (spConvertedSet,searchSet)
            else:
                trial.failure(sloc)
                trial.display()
    return (spConvertedSet,searchSet)
