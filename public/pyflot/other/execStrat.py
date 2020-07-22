import os
verbose=3
count = 0
def runCheckScript():
    global count
    if count%2 == 0:
        count +=1
        return True
    else:
        count +=1
        return False

def execApplication(binary, args, stratDir, stratList, multiSite=False):
    """ stratList is a list of tuple (name,hashKeys)
        In case of multiSite, hashKeys is a list
        Otherwise is just a single hashkey
    """
    cmd = f"{binary} {args}"
    validNames = []
    validHashKeys = []
    procenv = {}
    resultsDir = "./.pyflot/results/"
    procenv["PRECISION_TUNER_READJSON"] = "./.pyflot/profile/profile.json"
    procenv["PRECISION_TUNER_DUMPCSV"] = "./whocares.json"
    procenv["PRECISION_TUNER_OUTPUT_DIRECTORY"] = resultsDir
    procenv["PRECISION_TUNER_MODE"] = "APPLYING_STRAT"
    #procenv["DEBUG"] = ""
    os.system(f"mkdir -p {resultsDir}")
    for var,value in procenv.items():
        os.environ[var] = value
    for (name,hashKey) in stratList:
        ## File name Should be same as in generateStrat.py
        backtrace = f"{stratDir}/strat-{name}.txt"
        os.environ["BACKTRACE_LIST"] = backtrace
        os.environ["PRECISION_TUNER_DUMPJSON"] = f"./dumpResults-{name}.json"
        #print(f"execute {name}",backtrace,cmd)
        os.system(cmd)
        valid = runCheckScript()
        if verbose>2:
            print(f"BacktraceListFile ({backtrace}) Valid? {valid}")
        if valid:
            if multiSite:
                return ([name],hashKey)
            validNames.append(name)
            validHashKeys.append(hashKey)
    return (validNames,validHashKeys)
