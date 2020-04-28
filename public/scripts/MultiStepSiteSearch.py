#!/usr/bin/env python3
from parse import parseWithCluster

from Profile import Profile
from staticApproach import slocBFS
from slocCluster import slocClusterBFS
from dynamicApproach import backtraceBFS
from backtraceCluster import backtraceClusterBFS
## Parsing arguments
verbose = 10
args           = parseWithCluster(verbose)
##SLOC BT -C -Cf ->
strategy = args.strategy
## Composed constants
profileFile = args.readdir + "/" + args.profilefile

## Fill initial type configuration list indexed by backtrace based call site ID
profile = Profile(profileFile,2)
initSet = profile._doublePrecisionSlocSet
slocsuccess = []
btsuccess = []
## S:success F:failure
S = set()
F = set()
##TODO: why need profileFile to apply strategy (libC++)?
print("nbTrials ratioSlocSP ratioBtSP ratioDynSP dynCallsSP slocCallSiteSP btCallSiteSP totalDynCalls totalSlocCallSites totalBtCallSites")
print("0 0 0 0 0 0 0 0 0 0")
print("strategy",strategy)
if strategy == "SLOC":
    (S,F) = slocClusterBFS(profile, initSet, args, verbose=verbose)
    slocsuccess += S
    (S,F) = slocBFS(profile, F, args, verbose)
    slocsuccess.extend(S)
if strategy == "BT" or strategy == "BT-C->BT" or strategy == "BT-Cf->BT":
    F = initSet
    F = set(profile.convertSloc2BtId(F))
    if strategy == "BT-C->BT" or strategy == "BT-Cf->BT":
        args.filtering = False
        if strategy == "BT-Cf->BT":
            args.filtering = True
        (S,F) = backtraceClusterBFS(profile, F, args, verbose=verbose)
        btsuccess.extend(S)
    (S,F) = backtraceBFS(profile, F, args, verbose=verbose)
    btsuccess.extend(S)

print("Can be converted to single precision: ")
print("SLOC")
print(sorted(slocsuccess))
print("BT")
print(sorted(btsuccess))
print("Must remain in double precision: (BT)")
print(sorted(F))
