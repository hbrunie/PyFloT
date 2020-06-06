#!/usr/bin/env python3
import pdb
from parse import parseAnalyzing

from Common import BFS

def backtraceBFS(profile, searchSet, args, verbose):
    ## Composed constants
    return BFS(profile, searchSet, args, False, verbose)

if __name__ == "__main__":
    ## Parsing arguments
    args           = parseAnalyzing()
    profileFile    = args.readdir + "/" + args.profilefile
    ## get verbose level from generateStrat.py
    profile = Profile(profileFile)
    initSet = profile._doublePrecisionSet
    backtraceBFS(profile, searchSet, args)
