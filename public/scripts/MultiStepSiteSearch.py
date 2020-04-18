#!/usr/bin/env python3
from parse import parseStaticWithCluster

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
stratDir            = dumpdir + "/strats/static/"
readJsonProfileFile = dumpdir + "/" + profileFile
## get verbose level from generateStrat.py
verbose = getVerbose()

slocClusterBasedBFS(params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)

slocBasedBFS(params,binary,dumpdir,profileFile,checkTest2Find)

backtraceClusterBasedBFS(params,binary,dumpdir,profileFile,checkTest2Find,tracefile,threshold)

backtraceBasedBFS(params,binary,dumpdir,profileFile,checkTest2Find)
