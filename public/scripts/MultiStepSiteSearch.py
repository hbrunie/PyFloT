#!/usr/bin/env python3
from parse import parseStaticWithCluster

from updateProfile import updateProfileMultiStepSiteSearch
from staticApproach import slocBFS
from slocCluster import slocClusterBFS
from dynamicApproach import backtraceBFS
from backtraceCluster import backtraceClusterBFS
## Parsing arguments
args           = parseStaticWithCluster()
params         = args.param
binary         = args.binary
dumpdir        = args.dumpdir
profileFile    = args.profilefile
checkText2Find = args.verif_text
tracefile      = args.mergedtracefile
threshold      = args.threshold
## Composed constants
profileFile = dumpdir + "/" + profileFile
## get verbose level from generateStrat.py
verbose = getVerbose()

## Fill initial type configuration list indexed by backtrace based call site ID
profile = Profile(profileFile)
initSet = profile.__doublePrecisionSet
success = set()
## S:success F:failure
S = set()
F = set()
##TODO: why need profileFile to apply strategy (libC++)?
(S,F) = slocClusterBFS(profile, initSet, params,binary,dumpdir,checkTest2Find,tracefile,threshold)
exit(0)
success += S
(S,F) = slocBFS(F, params,binary,dumpdir,profileFile,checkTest2Find)
success += S
(S,F) = backtraceClusterBFS(F, params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)
success += S
(S,F) = backtraceBFS(F, params,binary,dumpdir,profileFile,checkTest2Find)
success += S

print("Can be converted to single precision: ")
for btInfo in map(profile.getInfoByBtID(), success):
    print(btInfo)
print("Must remain in double precision: ")
for btInfo in map(profile.getInfoByBtID(), F):
    print(btInfo)
