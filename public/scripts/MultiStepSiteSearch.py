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

##TODO: why need profileFile to apply strategy (libC++)?
slocClusterBasedBFS(profile, params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)

slocBasedBFS(params,binary,dumpdir,profileFile,checkTest2Find)

backtraceClusterBasedBFS(params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)

backtraceBasedBFS(params,binary,dumpdir,profileFile,checkTest2Find)
