#!/usr/bin/env python3
from parse import parseWithCluster

from Common import clusterBFS

def slocClusterBFS(profile, searchSet, params, binary, dumpdir,
                   checkTest2Find, tracefile, threshold, maxdepth=1,windowSize=2,verbose=1):
    """ Search set contains backtrace based index of call site yet in double precision.
        Returns the new search set and the set of call site successfully converted to single precision.
    """
    ## Composed constants
    stratDir   = dumpdir + "/strats/staticWithClustering/"
    return clusterBFS(profile, searchSet, params, binary, dumpdir, stratDir, True,
                        checkTest2Find, tracefile, threshold, maxdepth=1,windowSize=2,verbose=1)

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
    slocClusterBasedBFS(initSet, params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold,maxdepth,windowSize)
