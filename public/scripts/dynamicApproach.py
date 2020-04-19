#!/usr/bin/env python3
import pdb
from parse import parseBt

from Common import BFS

def backtraceBFS(profile, searchSet, params, binary, dumpdir, checkText2Find, verbose):
    ## Composed constants
    stratDir            = dumpdir + "/strats/backtrace/"
    return BFS(profile, searchSet, params, binary, dumpdir, stratDir, checkText2Find, verbose, False)

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
    backtraceBFS(profile, searchSet, params,binary,dumpdir,checkText2Find,verbose)
