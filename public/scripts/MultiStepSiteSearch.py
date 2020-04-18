#!/usr/bin/env python3
from parse import parseStaticWithCluster

from generateStrat import execApplication
from generateStrat import createStratFilesStatic
from generateStrat import createStratFilesMultiSiteStatic
from generateStrat import execApplication
from generateStrat import execApplicationMultiSite
from generateStrat import display
from generateStrat import getVerbose
from generateStrat import updateProfileCluster
from generateStrat import getCorrStatList

from communities import build_graph
from communities import generate_graph

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

def breadth_first_search()

##SLOC level
## Generate SLOC based clusters
updateProfileCluster(readJsonProfileFile)
corr = getCorrStatList()
(ge, gn) = build_graph(tracefile, corr)
clustering_algorithm(ge, gn, threshold)

## Individual analysis (BFS inspired from Mike Lam papers)
toTestList = createStratFilesStaticCluster(stratDir)
if verbose >2:
    print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
## Get the successful individual static call sites
validList = execApplication(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
if verbose>2:
    print("Level1, Valid name list of individual-site static call sites: ", validList[0])

## For all remaining Static Calls
## Sort all strategies per performance impact,
## start trying them from the most to the less impact.
toTestListGen = createStratFilesMultiSiteStatic(stratDir,readJsonProfileFile,validList)
##Use only first depth of clustering
toTestList = next(toTestListGen)
if verbose>2:
    print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])

validList = execApplicationMultiSite(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
if verbose>2:
    if len(validList)>0:
        print("Level2, Valid Name list of multi-site static call sites:", validList[0])

toTestList = createStratFilesStatic(stratDir,readJsonProfileFile, validList)
