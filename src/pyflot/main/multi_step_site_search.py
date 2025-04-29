#!/usr/bin/env python3
import numpy as np
from enum import Enum
from parse import parseAnalyzing

from src.pyflot.profiling.Profile import Profile
from pyflot.profile.staticApproach import slocBFS
from pyflot.profile.slocCluster import slocClusterBFS
from pyflot.profile.dynamicApproach import backtraceBFS
from pyflot.profile.backtraceCluster import backtraceClusterBFS
from pyflot.profile.Common import BFS

from configuration.config_analysis import PyflotConfig

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
    _available_strategies = [
        "BT",
        "BT-C",
        "BT-Cf",
        ("BT-Cf", "BT"),
        ("BT-C", "BT"),
        "SLOC",
        "SLOC-C",
        ("SLOC-C", "SLOC"),
        ("SLOC-C", "SLOC", "BT"),
        ("SLOC-C", "SLOC", "BT-Cf"),
        ("SLOC-C", "SLOC", "BT-Cf", "BT"),
        ("SLOC-C", "SLOC", "BT-C"),
        ("SLOC-C", "SLOC", "BT-C", "BT"),
        "SLOC,BT",
    ]

    def __init__(self, strategy: STRATEGIES):
        ##SLOC BT -C -Cf ->
        assert strategy is STRATEGIES
        self.verbose = False

        ## Fill initial type configuration list indexed by backtrace based call site ID
        profile = Profile()
        slocsuccess, btsuccess, failures_set = self.get_strategy(strategy, profile, self.verbose)
        print("Can be converted to single precision: ")
        print("SLOC")
        print(sorted(slocsuccess))
        print("BT")
        print(sorted(btsuccess))
        print("Must remain in double precision: (BT)")
        print(sorted(failures_set))

    def _slocBFS(profile: Profile, searchSet: set, verbose=1):
        ## Composed constants
        return BFS(profile, searchSet, args, True, verbose)

    def get_strategy(self, strategy: str, profile: Profile, verbose):
        strat_tuple = tuple(strategy.split("->"))
        initSet = profile._doublePrecisionSlocSet
        slocsuccess = []
        btsuccess = []
        ## S:success F:failure
        successes_set = set()
        failures_set = set()
        assert strat_tuple in MultiStepSiteSearch._available_strategies
        if "SLOC-C" in strat_tuple:
            (successes_set, failures_set) = slocClusterBFS(profile, initSet, args, verbose=verbose)
            slocsuccess += successes_set
        else:
            failures_set = initSet
            if "SLOC" in strategy:
                (successes_set, failures_set) = slocBFS(profile, failures_set, args, verbose)
                slocsuccess.extend(successes_set)
            else:
                failures_set = initSet
        if "BT" in strat_tuple or "BT-C" in strat_tuple or "BT-Cf" in strat_tuple:
            failures_set = set(profile.convertSloc2BtId(failures_set))
            args.filtering = False
            if "BT-Cf" in strat_tuple:
                args.filtering = True
            if "BT-C" in strat_tuple or "BT-Cf" in strat_tuple:
                (successes_set, failures_set) = backtraceClusterBFS(profile, failures_set, args, verbose=verbose)
                btsuccess.extend(successes_set)
            if "BT" in strat_tuple:
                (successes_set, failures_set) = backtraceBFS(profile, failures_set, args, verbose=verbose)
                btsuccess.extend(successes_set)
        return slocsuccess, btsuccess, failures_set
