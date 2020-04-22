#!/usr/bin/env python3
from parse import parseWithCluster
import pdb

from Profile import Profile
from staticApproach import slocBFS
from slocCluster import slocClusterBFS
from dynamicApproach import backtraceBFS
from backtraceCluster import backtraceClusterBFS
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

## Fill initial type configuration list indexed by backtrace based call site ID
profile = Profile(profileFile,0)
initSet = profile._doublePrecisionSlocSet
slocsuccess = []
btsuccess = []
verbose = 0
## S:success F:failure
S = set()
F = set()
##TODO: why need profileFile to apply strategy (libC++)?
print("nbTrials ratioDynSP")
print("0 0")
#(S,F) = slocClusterBFS(profile, initSet, params,binary,dumpdir,checkText2Find,tracefile, 100000, verbose=verbose)
slocsuccess += S
F = initSet
#(S,F) = slocBFS(profile, F, params,binary,dumpdir,checkText2Find, verbose)
slocsuccess.extend(S)
F = set(profile.convertSloc2BtId(F))
(S,F) = backtraceClusterBFS(profile, F, params,binary,dumpdir,checkText2Find,tracefile,100000,verbose=verbose)
btsuccess.extend(S)
#(S,F) = backtraceBFS(profile, F, params,binary,dumpdir,checkText2Find,verbose=verbose)
btsuccess.extend(S)
if verbose >1:
    print("Can be converted to single precision: ")
    print("SLOC")
    print(sorted(slocsuccess))
    print("BT")
    print(sorted(btsuccess))
    print("Must remain in double precision: (BT)")
    print(sorted(F))
