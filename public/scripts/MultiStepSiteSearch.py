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
profile = Profile(profileFile,verbose)
initSet = profile._doublePrecisionSet
success = []
## S:success F:failure
S = []
F = []
##TODO: why need profileFile to apply strategy (libC++)?
print("slocClusterBFS")
(S,F) = slocClusterBFS(profile, initSet, params,binary,dumpdir,checkText2Find,tracefile, 100000, verbose=0)
print("F",F)
success.extend(S)
print("slocBFS")
(S,F) = slocBFS(profile, F, params,binary,dumpdir,checkText2Find, 10)
print("F",F)
print("slocBFSend")
success.extend(S)
print("backtraceClusterBFS")
(S,F) = backtraceClusterBFS(profile, F, params,binary,dumpdir,checkText2Find,tracefile,100000,verbose=40)
print("F",F)
success.extend(S)
print(" backtraceBFS")
(S,F) = backtraceBFS(profile, F, params,binary,dumpdir,checkText2Find,verbose=10)
print("F",F)
success.extend(S)

print("Can be converted to single precision: ")
print(sorted(success))
print("Must remain in double precision: ")
print(sorted(F))
