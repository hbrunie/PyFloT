#!/usr/bin/env python3
from parse import parseStatic

from generateStrat import execApplication
from generateStrat import createStratFilesIndividuals
from generateStrat import createStratFilesMultiSiteDynamic
from generateStrat import execApplication
from generateStrat import execApplicationMultiSite
from generateStrat import display
from generateStrat import getVerbose

def backtraceBFS(params,binary,dumpdir,profileFile,checkTest2Find):
    stratDir = dumpdir + "/strats/dynamic/"
    readJsonProfileFile = dumpdir + profileFile
    ## Dynamic Calls (Full CallStack)
    ## Same approach, prune based on Individual Reduced Precision (BFS: Mike Lam)
    toTestList = createStratFilesIndividuals(stratDir, readJsonProfileFile)
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

if __name__ == "__main__":
    ## Parsing arguments
    args = parseStatic()
    params   = args.param
    binary   = args.binary
    dumpdir = args.dumpdir
    profileFile = args.profilefile
    checkText2Find = args.verif_text
    verbose = getVerbose()
    backtraceBFS(params,binary,dumpdir,profileFile,checkTest2Find,verbose)
