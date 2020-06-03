#!/usr/bin/env python3
import numpy as np
from parse import parseAnalyzing
import pdb

from Profile import Profile
from staticApproach import slocBFS
from slocCluster import slocClusterBFS
from dynamicApproach import backtraceBFS
from backtraceCluster import backtraceClusterBFS
## Different strat
strat0 = "BT"
strat1 = "BT-C"
strat2 = "BT-Cf"
strat3 = "BT-Cf->BT"
strat4 = "BT-C->BT"
strat5 = "SLOC"
strat6 = "SLOC->BT"
strat7 = "SLOC-C"
strat8 = "SLOC-C->SLOC"
strat9 = "SLOC-C->SLOC->BT"
strat10 = "SLOC-C->SLOC->BT-Cf"
strat11 = "SLOC-C->SLOC->BT-Cf->BT"
strat12 = "SLOC-C->SLOC->BT-C"
strat13 = "SLOC-C->SLOC->BT-C->BT"
strategies = np.array([strat0,strat1,strat2,strat3,strat4,strat5,strat6,strat7,strat8,strat9,strat10,strat11,strat12,strat13])
## Parsing arguments
verbose = 1
args    = parseAnalyzing(verbose)
print(args)
##SLOC BT -C -Cf ->
strategy = args.strategy
## Composed constants
profileFile = args.readdir + "/" + args.profilefile

## Fill initial type configuration list indexed by backtrace based call site ID
profile = Profile(profileFile,args=args)
initSet = profile._doublePrecisionSlocSet
slocsuccess = []
btsuccess = []
## S:success F:failure
S = set()
F = set()
##TODO: why need profileFile to apply strategy (libC++)?
print("strategy",strategy)
print("nbTrials ratioSlocSP ratioBtSP ratioDynSP dynCallsSP slocCallSiteSP btCallSiteSP totalDynCalls totalSlocCallSites totalBtCallSites")
print("0 0 0 0 0 0 0 0 0 0")
profile.initScore(args)
if strategy not in strategies:
    print("Error Strategy unknown.")
    exit(-1)
if strategy in strategies[7:14]:##SLOC-C
    (S,F) = slocClusterBFS(profile, initSet, args, verbose=verbose)
    slocsuccess += S
if strategy in strategies[0:7]:##NO SLOC-C
    F = initSet
if strategy in strategies[np.r_[5,6,8:14]]:##SLOC
    (S,F) = slocBFS(profile, F, args, verbose)
    slocsuccess.extend(S)
if strategy in strategies[0:5]:##NO SLOC-C NOR SLOC
    F = initSet
if strategy in  strategies[np.r_[0:5,6,9:14]]:##BT or BT-C or BT-Cf
    F = set(profile.convertSloc2BtId(F))
    args.filtering = False
    if strategy in strategies[np.r_[2:4,10:12]]:##BT-Cf
        args.filtering = True
    if strategy in strategies[np.r_[1:5,10:14]]:##BT-C or BT-Cf
        (S,F) = backtraceClusterBFS(profile, F, args, verbose=verbose)
        btsuccess.extend(S)
    if strategy in strategies[np.r_[0,3,4,6,9,11,13]]:##BT
        (S,F) = backtraceBFS(profile, F, args, verbose=verbose)
        btsuccess.extend(S)

print("Can be converted to single precision: ")
print("SLOC")
print(sorted(slocsuccess))
print("BT")
print(sorted(btsuccess))
print("Must remain in double precision: (BT)")
print(sorted(F))
