#!/usr/bin/env python3
import pdb
from parse import parseStatic

from Common import updateEnv
from Common import runApp
from Profile import Profile

from generateStrat import createStratFilesIndividuals
from generateStrat import createStratFilesMultiSiteStatic

## Individual analysis (BFS inspired from Mike Lam papers)
def slocBFS(profile, searchSet, params, binary, dumpdir, checkText2Find, verbose):
    ## Composed constants
    stratDir            = dumpdir + "/strats/sloc/"
    resultsDir          = dumpdir + "/results/"
    readJsonProfileFile = dumpdir + profile._profileFile
    cmd = f"{binary} {params}"
    envStr = updateEnv(resultsDir, profile._profileFile, binary)
    ## SLOC CallSite identification (1 level CallStack)
    toTestList = createStratFilesIndividuals(profile, stratDir, searchSet, sloc=True)
    if verbose >2:
        print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
    ## Get the successful individual static call sites
    validDic = {}
    for (name, btCallSiteList) in toTestList:
        valid = runApp(cmd, stratDir, name, checkText2Find, envStr, profile._nbTrials, btCallSiteList)
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
        print("Level1, Valid name list of individual-site static call sites: ", validDic)
    ## For all remaining Static Calls
    ## Sort all strategies per performance impact,
    ## start trying them from the most to the less impact.
    assert len(validDic.keys())>0
    if len(validDic.keys()) < 2:
        ## take Best individual as solution
        onlyCorrectIndividual = list(validDic.values())[0]
        spConvertedSet = set(onlyCorrectIndividual)
        searchSet = searchSet - spConvertedSet
        return (spConvertedSet,searchSet)
    toTestListGen = createStratFilesMultiSiteStatic(profile, stratDir, validDic)
    assert(toTestListGen)
    ## Execute the application on generated strategy files
    ## Generate strategies choosing k among n.
    ## Analyze k-strategies before generating strategies for the next k.
    toStop = True
    while toStop:
        try:
            toTestList = next(toTestListGen)
        except StopIteration:
            print("No more strategy to test.")
            break
        if verbose>2:
            print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])
        for (name, btCallSiteList) in toTestList:
            valid = runApp(cmd, stratDir, name,  checkText2Find, envStr, profile._nbTrials, btCallSiteList)
            if valid:
                spConvertedSet = set(btCallSiteList)
                profile.trialSuccess(btCallSiteList)
                ## Revert success because we testing individual
                searchSet = searchSet - spConvertedSet
                profile.display()
                break
            else:
                profile.trialFailure()
                profile.display()
    return (spConvertedSet,searchSet)

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
    profile = Profile(profileFile)
    initSet = profile._doublePrecisionSet
    slocBFS(profile, searchSet, params,binary,dumpdir,checkText2Find,verbose)
