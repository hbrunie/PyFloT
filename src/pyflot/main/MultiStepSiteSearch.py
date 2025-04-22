#!/usr/bin/env python3
import numpy as np
from parse import parseAnalyzing

from src.pyflot.profiling.Profile import Profile
from staticApproach import slocBFS
from slocCluster import slocClusterBFS
from dynamicApproach import backtraceBFS
from backtraceCluster import backtraceClusterBFS
from pyflot.configuration.pyflot_config import PyflotConfig


def main():
    config = PyflotConfig()
    ## Different strat
    ## Parsing arguments
    verbose = config.verbosity
    strategy config.strategy
    args = parseAnalyzing(verbose)
    ##SLOC BT -C -Cf ->
    strategy = args.strategy
    ## Composed constants
    profileFile = args.readdir + "/" + args.profilefile

    ## Fill initial type configuration list indexed by backtrace based call site ID
    profile = Profile(profileFile, 0)
    initSet = profile._doublePrecisionSlocSet
    slocsuccess = []
    btsuccess = []
    ## S:success F:failure
    S = set()
    F = set()
    ##TODO: why need profileFile to apply strategy (libC++)?
    print(
        "nbTrials ratioSlocSP ratioBtSP ratioDynSP dynCallsSP slocCallSiteSP btCallSiteSP totalDynCalls totalSlocCallSites"
        " totalBtCallSites"
    )
    print("0 0 0 0 0 0 0 0 0 0")
    print("strategy", strategy)
    if strategy not in strategies:
        print("Error Strategy unknown.")
        exit(-1)
    if strategy in strategies[6:13]:  ##SLOC-C
        (S, F) = slocClusterBFS(profile, initSet, args, verbose=verbose)
        slocsuccess += S
    if strategy in strategies[np.r_[0:6, 13]]:  ##NO SLOC-C
        F = initSet
    if strategy in strategies[np.r_[5, 7:14]]:  ##SLOC
        (S, F) = slocBFS(profile, F, args, verbose)
        slocsuccess.extend(S)
    if strategy in strategies[0:5]:  ##NO SLOC-C NOR SLOC
        F = initSet
    if strategy in strategies[np.r_[0:5, 8:14]]:  ##BT or BT-C or BT-Cf
        F = set(profile.convertSloc2BtId(F))
        args.filtering = False
        if strategy in strategies[np.r_[2:4, 9:11]]:  ##BT-Cf
            args.filtering = True
        if strategy in strategies[np.r_[1:5, 9:13]]:  ##BT-C or BT-Cf
            (S, F) = backtraceClusterBFS(profile, F, args, verbose=verbose)
            btsuccess.extend(S)
        if strategy in strategies[np.r_[0, 3:5, 8, 10, 12, 13]]:  ##BT
            (S, F) = backtraceBFS(profile, F, args, verbose=verbose)
            btsuccess.extend(S)

    print("Can be converted to single precision: ")
    print("SLOC")
    print(sorted(slocsuccess))
    print("BT")
    print(sorted(btsuccess))
    print("Must remain in double precision: (BT)")
    print(sorted(F))
