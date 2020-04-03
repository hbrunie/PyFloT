from generateStrat import execApplication
from generateStrat import createStratFilesStatic
from generateStrat import createStratFilesMultiSiteStatic
from generateStrat import execApplication
from generateStrat import execApplicationMultiSite
from generateStrat import display
from generateStrat import getVerbose


## 2 levels
binary = "/global/cscratch1/sd/hbrunie/applications/AMReX-Combustion/PeleC/Exec/RegTests/PMF/PeleC1d.gnu.haswell.ex"
args = "inputs-1d-regt max_step=1"
## Level 1 --> Static calls
## First pruning based on Individual Reduced Precision

verbose = getVerbose()

readJsonProfileFile=".pyflot-1ite/profile.json"
stratDir = ".pyflot-1ite/strats/static/"
##No order in names --> individual
toTestList = createStratFilesStatic(stratDir,readJsonProfileFile)
if verbose >2:
    print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
## Get the successful inidividual static call sites
validList = execApplication(binary, args, stratDir, toTestList)
if verbose>2:
    print("Level1, Valid name list of individual-site static call sites: ", validList[0])

## For all remaining Static Calls
## Sort all strategies per performance impact (names),
## start trying them from the most to the less impact.
##Extract only names
toTestList = createStratFilesMultiSiteStatic(stratDir,readJsonProfileFile,
        validList)
if verbose>2:
    print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])

## Execute the application on generated strategy files
valid = execApplicationMultiSite(binary, args, stratDir, toTestList)
if verbose>2:
    print("Level1, Valid Name list of multi-site static call sites:", valid)
display()
