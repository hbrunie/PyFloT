#!/usr/bin/env python3
from parse import parseStatic

from generateStrat import execApplication
from generateStrat import createStratFilesDynamic
from generateStrat import createStratFilesMultiSiteDynamic
from generateStrat import execApplication
from generateStrat import execApplicationMultiSite
from generateStrat import display
from generateStrat import getVerbose

## Parsing arguments
args = parseStatic()

## 2 levels
#binary = "/global/cscratch1/sd/hbrunie/applications/AMReX-Combustion/PeleC/Exec/RegTests/PMF/PeleC1d.gnu.haswell.ex"
#args = "inputs-1d-regt max_step=1"
params   = args.param
binary   = args.binary
dumpdir = args.dumpdir
profileFile = args.profilefile
stratDir = dumpdir + "/strats/dynamic/"
readJsonProfileFile = dumpdir + profileFile
checkText2Find = args.verif_text

verbose = getVerbose()

## Dynamic Calls (Full CallStack)
## Same approach, prune based on Individual Reduced Precision (BFS: Mike Lam)
toTestList = createStratFilesDynamic(stratDir, readJsonProfileFile)
if verbose>2:
    print("Level2 Individual: ToTest name list: ", [x[0] for x in toTestList])
## Get the successful inidividual static call sites
validList = execApplication(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
if verbose>2:
    print("Level2, Valid name list of individual-site dynamic call sites: ", validList[0])

## Then merge with strategies sorted by performance impact
## Be aware: static calls strategy from level 1 is still used here.
toTestListGen = createStratFilesMultiSiteDynamic(stratDir,
        readJsonProfileFile, validList)
toStop = True
while toStop:
    try:
        toTestList = next(toTestListGen)
    except StopIteration:
        print("No more strategy to test.")
        display()
        exit(0)
    if verbose>2:
        print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])
    validList = execApplicationMultiSite(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
    if verbose>2:
        if len(validList)>0:
            print("Level2, Valid Name list of multi-site dynamic call sites:", validList[0])
    if len(validList)>0:
        display()
        exit(0)


