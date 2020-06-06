#!/usr/bin/env python3
from parse import parseAnalyzing

from Common import clusterBFS

def slocClusterBFS(profile, searchSet, args, verbose=1):
    """ Search set contains backtrace based index of call site yet in double precision.
        Returns the new search set and the set of call site successfully converted to single precision.
    """
    ## Composed constants
    return clusterBFS(profile, searchSet, args, True, verbose)

if __name__ == "__main__":
    ## Parsing arguments
    args           = parseAnalyzing()
    ## get verbose level from generateStrat.py
    profileFile = args.readdir + "/" + args.profileFile
    profile = Profile(profileFile)
    initSet = profile._doublePrecisionSet
    slocClusterBasedBFS(profile, initSet, args)
