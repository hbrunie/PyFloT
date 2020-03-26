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
stratDir = ".pyflot/strats/level1/"
##No order in names --> individual
toTestList = createStratFilesLvl1(stratDir,readJsonProfileFile)
if verbose >2:
    print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
## Get the successful inidividual static call sites
validList = execApplicationIndividualLvl1(binary, args, stratDir, toTestList)
if verbose>2:
    print("Level1, Valid name list of individual-site static call sites: ", validList[0])

## For all remaining Static Calls
## Sort all strategies per performance impact (names),
## start trying them from the most to the less impact.
##Extract only names
toTestList = createStratFilesMultiSite(stratDir,readJsonProfileFile,
        validList,1)
if verbose>2:
    print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])

## Execute the application on generated strategy files
validList = execApplicationMultiSiteLvl1(binary, args, stratDir, toTestList)
if verbose>2:
    print("Level1, Valid Name list of multi-site static call sites:", validList[0])

## Once found a valid strategy
## For all Static calls STILL executed in double precision
## Pass to level 2

## Level 2 --> Dynamic Calls (Full CallStack)
## Same approach, prune based on Individual Reduced Precision (BFS: Mike Lam)
stratDir = ".pyflot/strats/level2/"
toTestList = createStratFilesLvl2(stratDir, readJsonProfileFile,
                                 validList)
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
