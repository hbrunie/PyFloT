#!/usr/bin/env python3
from parse import parseStaticWithCluster

from generateStrat import execApplication
from generateStrat import createStratFilesStaticCluster
from generateStrat import createStratFilesMultiSiteStatic
from generateStrat import execApplication
from generateStrat import execApplicationMultiSite
from generateStrat import display
from generateStrat import getVerbose
from generateStrat import updateProfileCluster
from generateStrat import getCorrStatList

from communities import build_graph
from communities import generate_graph

def slocClusterBasedBFS(searchSet, params, binary, dumpdir, profileFile,
                        checkTest2Find, tracefile, threshold, maxdepth,windowSize):
    """ Search set contains backtrace based index of call site yet in double precision.
        Returns the new search set and the set of call site successfully converted to single precision.
    """
    spConvertedSet = set()
    resultsDir = dumpdir + "/results/"
    stratDir   = dumpdir + "/strats/staticWithClustering/"
    ## get verbose level from generateStrat.py
    verbose = getVerbose()
    ## Generate clusters
    corr = getCorrStatList()
    (ge, gn) = build_graph(searchSet, tracefile, threshold, windowSize, corr)
    hierarchy = clustering_algorithm(ge, gn, threshold, maxdepth)
    for depth,clusters in enumerate(hierarchy):
        if depth>maxdepth:
            break
        ## Individual analysis (BFS inspired from Mike Lam papers)
        toTestList = createStratFilesStaticCluster(stratDir, clusters, depth)
        if verbose >2:
            print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
            print(toTestList)
        ## Get the successful individual static call sites
        validList = execApplication(binary, params, stratDir, toTestList, checkText2Find, resultsDir, profileFile)
        ## E.g. (['depth-0-cluster-1'], [['0x5ead72', '0x5e913e']])
        if verbose>2:
            print("Level1, Valid name list of individual-site static call sites: ", validList[0])
            print(validList)
        ## For all remaining Static Calls
        ## Sort all strategies per performance impact,
        ## start trying them from the most to the less impact.
        toTestListGen = createStratFilesMultiSiteStatic(stratDir,profileFile,validList)
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
            validList = execApplicationMultiSite(binary, params, stratDir, toTestList, checkText2Find, resultsDir, profileFile)
            if verbose>2:
                if len(validList)>0:
                    print("Level2, Valid Name list of multi-site static call sites:", validList[0])
            ## valid type configuration found. Stop the search.
            if len(validList)>0:
                display()
    display()
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
    profile = Profile(profileFile)
    initSet = profile.__doublePrecisionSet
    slocClusterBasedBFS(initSet, params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold,maxdepth,windowSize)
