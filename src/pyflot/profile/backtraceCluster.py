#!/usr/bin/env python3
from parse import parseAnalyzing
from Common import clusterBFS

def backtraceClusterBFS(profile, searchSet, args, verbose=1):
    """ Search set contains backtrace based index of call site yet in double precision.
        Returns the new search set and the set of call site successfully converted to single precision.
    """
    ## Composed constants
    return clusterBFS(profile, searchSet, args, False, verbose=verbose)


if __name__ == "__main__":
    ## Parsing arguments
    args           = parseAnalyzing()
    profileFile    = args.readdir +"/" + profileFile
    ## get verbose level from generateStrat.py
    profile = Profile(profileFile)
    initSet = profile._doublePrecisionSet
    initSet = set(profile.convertSloc2BtId(initSet))
    slocClusterBFS(profile, initSet, args)
