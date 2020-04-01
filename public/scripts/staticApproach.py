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
valid = execApplicationMultiSiteLvl1(binary, args, stratDir, toTestList)
if verbose>2:
    print("Level1, Valid Name list of multi-site static call sites:", valid)
