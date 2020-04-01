from generateStrat import execApplication
from generateStrat import createStratFilesLvl1
from generateStrat import createStratFilesLvl2
from generateStrat import createStratFilesMultiSite
from generateStrat import execApplicationIndividualLvl1
from generateStrat import execApplicationMultiSiteLvl1

## 2 levels
binary = "./test3Exp"
args = ""
## Level 1 --> Static calls
## First pruning based on Individual Reduced Precision

verbose = 3

readJsonProfileFile=".pyflot/profile/profile.json"

## Dynamic Calls (Full CallStack)
## Same approach, prune based on Individual Reduced Precision (BFS: Mike Lam)
stratDir = ".pyflot/strats/dynamic/"
toTestList = createStratFilesDynamic(stratDir, readJsonProfileFile)
if verbose>2:
    print("Level2 Individual: ToTest name list: ", [x[0] for x in toTestList])
## Get the successful inidividual static call sites
validList = execApplication(binary, args, stratDir,
        toTestList, 2)
if verbose>2:
    print("Level2, Valid name list of individual-site dynamic call sites: ", validList[0])

## Then merge with strategies sorted by performance impact
## Be aware: static calls strategy from level 1 is still used here.
toTestList = createStratFilesMultiSite(stratDir,
        readJsonProfileFile, validList,2)
if verbose>2:
    print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])

validList = execApplication(binary, args, stratDir,
        toTestList, 2, multiSite=True)
if verbose>2:
    print("Level2, Valid Name list of multi-site dynamic call sites:", validList[0])
