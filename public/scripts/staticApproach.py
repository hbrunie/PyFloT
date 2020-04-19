#!/usr/bin/env python3
import pdb
from parse import parseStatic

from Common import BFS
from Profile import Profile

def slocBFS(profile, searchSet, params, binary, dumpdir, checkText2Find, verbose):
    ## Composed constants
    stratDir            = dumpdir + "/strats/sloc/"
    return BFS(profile, searchSet, params, binary, dumpdir, stratDir, checkText2Find, verbose, True)

if __name__ == "__main__":
    ## Parsing arguments
    args           = parseStatic()
    params         = args.param
    binary         = args.binary
    dumpdir        = args.dumpdir
    profileFile    = args.profilefile
    checkText2Find = args.verif_text
    ## get verbose level from generateStrat.py
    verbose = getVerbose()
    profile = Profile(profileFile)
    initSet = profile._doublePrecisionSet
    slocBFS(profile, searchSet, params,binary,dumpdir,checkText2Find,verbose)
