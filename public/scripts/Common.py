import os
verbose = 0
def getVerbose():
    return verbose

checkCount = 0
def checkTest3Exp():
    global checkCount
    if checkCount%2 == 0:
        checkCount +=1
        return True
    else:
        checkCount +=1
        return False

def checkPMF(f, checkText):
    ## Check PMF result
    res = checkText
    with open(f, "r") as inf:
        for l in inf.readlines():
            if res in l:
                return True
    return False

def runCheckScript(f, checkText):
    #return checkTest3Exp()
    return checkPMF(f, checkText)

def runApp(cmd, stratDir, name, checkText, envStr, nbTrials, btCallSiteIdList):
    ## MOCKUP
    for i in btCallSiteIdList:
        if i in range(50,60):
            return False
    return True
    outputFile = "output"
    outputFileLocal = stratDir + outputFile + f"-{nbTrials}.dat"
    ## File name Should be same as in generateStrat.py
    backtrace = f"{stratDir}/strat-{name}.txt"
    os.environ["BACKTRACE_LIST"] = backtrace
    if verbose>3:
        print(f"BACKTRACE_LIST={backtrace}")
    os.environ["PRECISION_TUNER_DUMPJSON"] = f"./dumpResults-{name}.json"
    if verbose>3:
        print(f"{envStr} PRECISION_TUNER_DUMPJSON="+f"./dumpResults-{name}.json")
        print(cmd)
    os.system(cmd + f" >> {outputFileLocal}")
    valid = runCheckScript(outputFileLocal, checkText)
    if verbose>2:
        print(f"BacktraceListFile ({backtrace}) Valid? {valid}")
    return valid

def updateEnv(resultsDir, profileFile, binary):
    procenv = {}
    ##TODO: use script arguments
    procenv["TARGET_FILENAME"] = binary
    ##TODO: why need profileFile to apply strategy (libC++)?
    procenv["PRECISION_TUNER_READJSON"] = profileFile
    ##TODO change with real csv filename
    procenv["PRECISION_TUNER_DUMPCSV"] = "./whocares.csv"
    procenv["PRECISION_TUNER_OUTPUT_DIRECTORY"] = resultsDir
    procenv["PRECISION_TUNER_MODE"] = "APPLYING_STRAT"
    os.system(f"mkdir -p {resultsDir}")
    envStr = "TARGET_FILENAME="
    envStr += binary
    envStr += " PRECISION_TUNER_READJSON="
    envStr += profileFile
    envStr += " PRECISION_TUNER_DUMPCSV="
    envStr += "./whocares.csv"
    envStr += " PRECISION_TUNER_OUTPUT_DIRECTORY="
    envStr += resultsDir
    envStr += " PRECISION_TUNER_MODE=APPLYING_STRAT"
    for var,value in procenv.items():
        os.environ[var] = value
    return envStr

def __execApplication(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile, multiSite):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    validNames = []
    validHashKeys = []
    statCallsSP=0
    dynCallsSP=0
    ##TODO:
    ## SCORE should be computed in separated function elsewhere.
    cmd = f"{binary} {args}"
    envStr = updateEnv(resultsDirectory, profileFile, binary)
    for (name, btCallSiteList) in stratList:
        valid = runApp(cmd, stratDir, name, checkText,envStr)
        if valid:
            dynCallsSP = max(dynCallsSP,dynCallsCount)
            statCallsSP = max(statCallsSP,statCallsCount)
            if multiSite:
                ##TODO: why making sum?
                ## Will it sum over several multisite strat tested, and count the invalid one too?
                #dynCallsSP += dynCallsCount
                #statCallsSP += statCallsCount
                display()
                return ([name],hashKey)
            else:
                validNames.append(name)
                validHashKeys.append(hashKey)
            display()
    if multiSite:
        return []
    else:
        return (validNames,validHashKeys)

def execApplication(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    return __execApplication(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile, False)

def execApplicationMultiSite(binary, args, stratDir, stratList, checkText, resultsDirectory, profileFile):
    """ stratList is a list of tuple (name,hashKeys)
        GOAL: Returns best multisite solution, if not return best individual solution
    """
    return __execApplication(binary,args,stratDir,stratList, checkText, resultsDirectory, profileFile, True)
