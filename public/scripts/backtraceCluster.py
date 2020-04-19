#!/usr/bin/env python3
from parse import parseWithCluster

from Common import runApp
from Common import runAppMockup
from Common import updateEnv
from Common import getVerbose

from generateStrat import createStratFilesCluster
from generateStrat import createStratFilesMultiSite

from communities import build_graph
from communities import community_algorithm

def backtraceClusterBFS(profile, searchSet, params, binary, dumpdir,
                        checkTest2Find, tracefile, threshold, maxdepth=1,windowSize=2,verbose=1):
    """ Search set contains backtrace based index of call site yet in double precision.
        Returns the new search set and the set of call site successfully converted to single precision.
    """
    ## Composed constants
    stratDir            = dumpdir + "/strats/backtraceWithClustering/"
    resultsDir = dumpdir + "/results/"
    tracefile = dumpdir + "/" + tracefile
    cmd = f"{binary} {params}"
    envStr = updateEnv(resultsDir, profile._profileFile, binary)
    ## Generate clusters
    (ge, gn) = build_graph(searchSet, tracefile, threshold, windowSize)
    com = community_algorithm(ge, gn, threshold, maxdepth)
    if not com:
        return (set(), searchSet)
        ## Individual analysis (BFS inspired from Mike Lam papers)
    toTestList =  createStratFilesCluster(profile, stratDir, com, depth=0, sloc=False)
    if verbose >2:
        print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
        print(toTestList)
    ## Get the successful individual backtrace based call sites
    validDic = {}
    for (name, btCallSiteList) in toTestList:
        #valid = runApp(cmd, stratDir, name, checkTest2Find, envStr, profile._nbTrials, btCallSiteList)
        valid = runAppMockup(btCallSiteList)
        if valid:
            validDic[name] = btCallSiteList
            profile.trialSuccess(btCallSiteList)
            ## Revert success because we testing individual
            profile.display()
            profile.revertSuccess(btCallSiteList)
        else:
            profile.trialFailure()
            profile.display()
    ## E.g. (['depth-0-cluster-1'], [['0x5ead72', '0x5e913e']])
    if verbose>2:
        print("Level1, Valid name list of individual-site static call sites: ", validDic.keys())
        print("validDic",validDic)
    ## If no valid individual found no need for multisite, return
    if len(validDic.keys())<1:
        return (set(),searchSet)
    if len(validDic.keys()) < 2:
        ## take Best individual as solution
        onlyCorrectIndividual = list(validDic.values())[0]
        spConvertedSet = set(onlyCorrectIndividual)
        searchSet = searchSet - spConvertedSet
        return (spConvertedSet,searchSet)
    toTestListGen = createStratFilesMultiSiteStatic(profile, stratDir, validDic)
    assert(toTestListGen)
    ## Execute the application on generated strategy files
    ## Generate strategies choosing k among n.
    ## Analyze k-strategies before generating strategies for the next k.
    toStop = True
    while toStop:
        try:
            toTestList = next(toTestListGen)
        except StopIteration:
            print(f"No more strategy to test for depth {depth}.")
            break
        if verbose>2:
            print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])
    for (name, btCallSiteList) in toTestList:
        #valid = runApp(cmd, stratDir, name,  checkTest2Find, envStr, profile._nbTrials, btCallSiteList)
        valid = runAppMockup(btCallSiteList)
        if valid:
            spConvertedSet = set(btCallSiteList)
            profile.trialSuccess(btCallSiteList)
            ## Revert success because we testing individual
            searchSet = searchSet - spConvertedSet
            profile.display()
            break
        else:
            profile.trialFailure()
            profile.display()
    return (spConvertedSet,searchSet)

if __name__ == "__main__":
    ## Parsing arguments
    args           = parseStaticWithCluster()
    params         = args.param
    binary         = args.binary
    dumpdir        = args.dumpdir
    profileFile    = args.profilefile
    checkText2Find = args.verif_text
    tracefile      = dumpdir + args.mergedtracefile
    threshold      = args.threshold
    windowSize     = args.windowSize
    maxdepth       = args.maxdepth
    profileFile    = dumpdir + profileFile
    ## get verbose level from generateStrat.py
    verbose = getVerbose()
    profile = Profile(profileFile)
    initSet = profile._doublePrecisionSet
    slocClusterBFS(params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)
