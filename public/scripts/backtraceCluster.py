#!/usr/bin/env python3
from parse import parseWithCluster

from generateStrat import execApplication
from generateStrat import createStratFilesCluster
from generateStrat import createStratFilesMultiSiteDynamic
from generateStrat import execApplication
from generateStrat import execApplicationMultiSite
from generateStrat import getVerbose

from communities import build_graph
from communities import community_algorithm

def backtraceClusterBFS(params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold):
    ## Composed constants
    stratDir            = dumpdir + "/strats/backtraceWithClustering/"
    readJsonProfileFile = dumpdir + profileFile
    ## get verbose level from generateStrat.py
    verbose = getVerbose()
    ## Generate clusters
    updateProfileCluster(readJsonProfileFile)
    (ge, gn) = build_graph(tracefile, None)
    hierarchy = generate_graph(ge, gn, threshold)
    for depth,clusters in enumerate(hierarchy):
        ## Individual analysis (BFS inspired from Mike Lam papers)
        toTestList = createStratFilesDynamicCluster(stratDir, clusters, depth)
        if verbose >2:
            print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
            print(toTestList)
        ## Get the successful individual backtrace based call sites
        validList = execApplication(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
        ## E.g. (['depth-0-cluster-1'], [['0x5ead72', '0x5e913e']])
        if verbose>2:
            print("Level1, Valid name list of individual-site backtrace based call sites: ", validList[0])
            print(validList)
        ## For all remaining Backtrace Based Calls
        ## Sort all strategies per performance impact,
        ## start trying them from the most to the less impact.
        toTestListGen = createStratFilesMultiSiteDynamic(stratDir,readJsonProfileFile,validList)
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
            validList = execApplicationMultiSite(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
            if verbose>2:
                if len(validList)>0:
                    print("Level2, Valid Name list of multi-site backtrace based call sites:", validList[0])
            ## valid type configuration found. Stop the search.
            if len(validList)>0:
                display()
    display()

if __name__ == "__main__":
    ## Parsing arguments
    args           = parseDynamicWithCluster()
    params         = args.param
    binary         = args.binary
    dumpdir        = args.dumpdir
    profileFile    = args.profilefile
    checkText2Find = args.verif_text
    tracefile      = dumpdir + args.mergedtracefile
    threshold      = args.threshold
    slocClusterBFS(params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)
