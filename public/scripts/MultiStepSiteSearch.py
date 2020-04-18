#!/usr/bin/env python3
from parse import parseStaticWithCluster

from updateProfile import updateProfileMultiStepSiteSearch
from staticApproach import slocBasedBFS
from staticWithClusterApproach import slocClusterBasedBFS
from dynamicApproach import backtraceBasedBFS
from dynamicWithClusterApproach import backtraceClusterBasedBFS
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
##TODO: why need profileFile to apply strategy (libC++)?
(S,F) = slocClusterBasedBFS(initSet, params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)
success += S
(S,F) = slocBasedBFS(F, params,binary,dumpdir,profileFile,checkTest2Find)
success += S
(S,F) = backtraceClusterBasedBFS(F, params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)
success += S
(S,F) = backtraceBasedBFS(F, params,binary,dumpdir,profileFile,checkTest2Find)
success += S

print("Can be converted to single precision: ")
for btInfo in map(profile.getInfoByBtID(), success):
    print(btInfo)
print("Must remain in double precision: ")
for btInfo in map(profile.getInfoByBtID(), F):
    print(btInfo)
