#!/usr/bin/env python3
from parse import parseWithCluster

from Profile import Profile
from staticApproach import slocBFS
from slocCluster import slocClusterBFS
from dynamicApproach import backtraceBFS
from backtraceCluster import backtraceClusterBFS
from Common import getVerbose
## Parsing arguments
args           = parseWithCluster()
params         = args.param
binary         = args.binary
dumpdir        = args.dumpdir
profileFile    = args.profilefile
checkText2Find = args.verif_text
tracefile      = args.mergedtracefile
threshold      = args.threshold
checkTest2Fine = args.verif_text
## Composed constants
profileFile = dumpdir + "/" + profileFile
## get verbose level from generateStrat.py
verbose = getVerbose()

## Fill initial type configuration list indexed by backtrace based call site ID
profile = Profile(profileFile)
initSet = profile._doublePrecisionSet
success = set()
## S:success F:failure
S = set()
F = set()
##TODO: why need profileFile to apply strategy (libC++)?
(S,F) = slocClusterBFS(profile, initSet, params,binary,dumpdir,checkText2Find,tracefile, 100000, verbose=verbose)
print("end")
exit(0)
success += S
(S,F) = slocBFS(F, params,binary,dumpdir,profileFile,checkText2Find)
success += S
(S,F) = backtraceClusterBFS(F, params,binary,dumpdir,profileFile,checkText2Find,tracefile,threshold)
success += S
(S,F) = backtraceBFS(F, params,binary,dumpdir,profileFile,checkText2Find)
success += S

print("Can be converted to single precision: ")
for btInfo in map(profile.getInfoByBtID(), success):
    print(btInfo)
print("Must remain in double precision: ")
for btInfo in map(profile.getInfoByBtID(), F):
    print(btInfo)
