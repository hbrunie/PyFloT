#!/usr/bin/env python3
from parse import parseStatic

from generateStrat import execApplication
from generateStrat import createStratFilesIndividuals
from generateStrat import createStratFilesMultiSiteStatic
from generateStrat import execApplication
from generateStrat import execApplicationMultiSite
from generateStrat import getVerbose

## Individual analysis (BFS inspired from Mike Lam papers)
def slocBFS(params,binary,dumpdir,profileFile,checkTest2Find,verbose):
    ## Composed constants
    stratDir            = dumpdir + "/strats/static/"
    resultsDir = dumpdir + "/results/"
    readJsonProfileFile = dumpdir + profileFile
    cmd = f"{binary} {args}"
    envStr = updateEnv(resultsDirectory, profile.__profileFile, binary)
    toTestList = createStratFilesIndividuals(profile, stratDir, sloc=True)
    if verbose >2:
        print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
    ## Get the successful individual static call sites
    #validList = execApplication(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
    ## Get the successful individual static call sites
    validDic = {}
    for (name, btCallSiteList) in toTestList:
        valid = runApp(cmd, stratDir, name, checkText, envStr)
        if valid:
            validDic[name] = btCallSiteList
            profile.trialSuccess(btCallSiteList)
            ## Revert success because we testing individual
            profile.display()
            profile.revertSuccess(btCallSiteList)
        else:
            profile.trialFailure()
            profile.display()
    if verbose>2:
        print("Level1, Valid name list of individual-site static call sites: ", validList[0])

    ## For all remaining Static Calls
    ## Sort all strategies per performance impact,
    ## start trying them from the most to the less impact.
    toTestListGen = createStratFilesMultiSiteStatic(stratDir,readJsonProfileFile,validList)
    if verbose>2:
        print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])

    ## Execute the application on generated strategy files
    ## Generate strategies choosing k among n.
    ## Analyze k-strategies before generating strategies for the next k.
    toStop = True
    while toStop:
        try:
            toTestList = next(toTestListGen)
        except StopIteration:
            print("No more strategy to test.")
            exit(0)
        if verbose>2:
            print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])
        validList = execApplicationMultiSite(binary, params, stratDir, toTestList, checkText2Find, dumpdir, profileFile)
        if verbose>2:
            if len(validList)>0:
                print("Level2, Valid Name list of multi-site static call sites:", validList[0])
        ## valid type configuration found. Stop the search.
        if len(validList)>0:
            exit(0)

if __name__ == "__main__":
    ## Parsing arguments
    args           = parseStatic()
    params         = args.param
    binary         = args.binary
    dumpdir        = args.dumpdir
    profileFile    = args.profilefile
    checkText2Find = args.verif_text
    ## get verbose level from generateStrat.py
    verbose = getVerbose()
    slocBFS(params,binary,dumpdir,profileFile,checkTest2Find,verbose)
