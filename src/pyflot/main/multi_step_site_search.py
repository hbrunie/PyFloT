#!/usr/bin/env python3
import numpy as np
from enum import Enum
from parse import parseAnalyzing

from src.pyflot.profiling.Profile import Profile
from staticApproach import slocBFS
from slocCluster import slocClusterBFS
from dynamicApproach import backtraceBFS
from backtraceCluster import backtraceClusterBFS
from pyflot.configuration.pyflot_config import PyflotConfig

class STRATEGIES(Enum):
    STRAT0 = "BT"
    STRAT1 = "BT-C"
    STRAT2 = "BT-Cf"
    STRAT3 = "BT-Cf->BT"
    STRAT4 = "BT-C->BT"
    STRAT5 = "SLOC"
    STRAT6 = "SLOC-C"
    STRAT7 = "SLOC-C->SLOC"
    STRAT8 = "SLOC-C->SLOC->BT"
    STRAT9 = "SLOC-C->SLOC->BT-Cf"
    STRAT10 = "SLOC-C->SLOC->BT-Cf->BT"
    STRAT11 = "SLOC-C->SLOC->BT-C"
    STRAT12 = "SLOC-C->SLOC->BT-C->BT"
    STRAT13 = "SLOC->BT"


class MultiStepSiteSearch:

    def __init__(self, strategy: STRATEGIES):
        ##SLOC BT -C -Cf ->
        assert strategy is STRATEGIES

        ## Fill initial type configuration list indexed by backtrace based call site ID
        profile = Profile()
        initSet = profile._doublePrecisionSlocSet
        slocsuccess = []
        btsuccess = []
        ## S:success F:failure
        successes_set = set()
        failures_set = set()
        print(
            "nbTrials ratioSlocSP ratioBtSP ratioDynSP dynCallsSP slocCallSiteSP btCallSiteSP totalDynCalls totalSlocCallSites"
            " totalBtCallSites"
        )
        print("0 0 0 0 0 0 0 0 0 0")
        print("strategy", strategy)
        if "SLOC-C" in strategy.value:
            (successes_set, failures_set) = slocClusterBFS(profile, initSet, args, verbose=verbose)
            slocsuccess += successes_set
        if strategy in strategies[np.r_[0:6, 13]]:  ##NO SLOC-C
            failures_set = initSet
        if strategy in strategies[np.r_[5, 7:14]]:  ##SLOC
            (successes_set, failures_set) = slocBFS(profile, failures_set, args, verbose)
            slocsuccess.extend(successes_set)
        if strategy in strategies[0:5]:  ##NO SLOC-C NOR SLOC
            failures_set = initSet
        if strategy in strategies[np.r_[0:5, 8:14]]:  ##BT or BT-C or BT-Cf
            failures_set = set(profile.convertSloc2BtId(failures_set))
            args.filtering = False
            if strategy in strategies[np.r_[2:4, 9:11]]:  ##BT-Cf
                args.filtering = True
            if strategy in strategies[np.r_[1:5, 9:13]]:  ##BT-C or BT-Cf
                (successes_set, failures_set) = backtraceClusterBFS(profile, failures_set, args, verbose=verbose)
                btsuccess.extend(successes_set)
            if strategy in strategies[np.r_[0, 3:5, 8, 10, 12, 13]]:  ##BT
                (successes_set, failures_set) = backtraceBFS(profile, failures_set, args, verbose=verbose)
                btsuccess.extend(successes_set)

        print("Can be converted to single precision: ")
        print("SLOC")
        print(sorted(slocsuccess))
        print("BT")
        print(sorted(btsuccess))
        print("Must remain in double precision: (BT)")
        print(sorted(failures_set))

    def get_strategy(self, strategy: str):
        if strategy not in STRATEGIES:
            print("Error Strategy unknown.")
            exit(-1)
        if strategy in strategies[6:13]:  ##SLOC-C
            (successes_set, failures_set) = slocClusterBFS(profile, initSet, args, verbose=verbose)
            slocsuccess += successes_set
        if strategy in strategies[np.r_[0:6, 13]]:  ##NO SLOC-C
            failures_set = initSet
        if strategy in strategies[np.r_[5, 7:14]]:  ##SLOC
            (successes_set, failures_set) = slocBFS(profile, failures_set, args, verbose)
            slocsuccess.extend(successes_set)
        if strategy in strategies[0:5]:  ##NO SLOC-C NOR SLOC
            failures_set = initSet
        if strategy in strategies[np.r_[0:5, 8:14]]:  ##BT or BT-C or BT-Cf
            failures_set = set(profile.convertSloc2BtId(failures_set))
            args.filtering = False
            if strategy in strategies[np.r_[2:4, 9:11]]:  ##BT-Cf
                args.filtering = True
            if strategy in strategies[np.r_[1:5, 9:13]]:  ##BT-C or BT-Cf
                (successes_set, failures_set) = backtraceClusterBFS(profile, failures_set, args, verbose=verbose)
                btsuccess.extend(successes_set)
            if strategy in strategies[np.r_[0, 3:5, 8, 10, 12, 13]]:  ##BT
                (successes_set, failures_set) = backtraceBFS(profile, failures_set, args, verbose=verbose)
                btsuccess.extend(successes_set)