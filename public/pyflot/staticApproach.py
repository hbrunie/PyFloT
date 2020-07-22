#!/usr/bin/env python3
import pdb
from parse import parseAnalyzing

from Common import BFS
from Profile import Profile

def slocBFS(profile, searchSet, args, verbose=1):
    ## Composed constants
    return BFS(profile, searchSet, args, True, verbose)

if __name__ == "__main__":
    ## Parsing arguments
    args           = parseAnalyzing()
    profileFile    = args.readdir + "/" + args.profilefile
    ## get verbose level from generateStrat.py
    profile = Profile(profileFile)
    initSet = profile._doublePrecisionSet
    slocBFS(profile, searchSet, args)
