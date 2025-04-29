
from src.pyflot.profiling.Profile import Profile

class BFS:
    def __init__(self, profile: Profile, search_set: set, with_sloc: bool, verbose: bool = False):
        self.profile = profile
        self.search_set = search_set

    def apply(self):
        """ """
        dumpdir = args.dumpdir
        ssloc = "sloc"
        if not sloc:
            ssloc = "backtrace"
        stratDir = args.dumpdir + f"/strats/{ssloc}/"
        resultsDir = args.dumpdir + "/results/"
        if verbose > 0:
            print(f"Running BFS {ssloc}")
        self.profile.trialNewStep()
        readJsonProfileFile = dumpdir + profile._profileFile
        cmd = f"{args.binary} {args.params}"
        if verbose > 2:
            print("command", cmd)
        envStr = updateEnv(resultsDir, profile._profileFile, args.binary, verbose)
        ## SLOC CallSite identification (1 level CallStack)
        toTestList = createStratFilesIndividuals(profile, stratDir, searchSet, sloc)
        if verbose > 2:
            print("Level1 Individual: ToTest name list: ", [x[0] for x in toTestList])
        ## Get the successful individual static call sites
        validDic = {}
        for name, CallSiteList in toTestList:
            valid = runApp(cmd, stratDir, name, args.verif_text, envStr, profile._nbTrials)
            if valid:
                validDic[name] = CallSiteList
                profile.trialReverse(sloc)
                profile.trialSuccess(CallSiteList, sloc, True)
                ## Revert success because we testing individual
                profile.display()
            else:
                profile.trialFailure()
                profile.display()
        if verbose > 2:
            print("Level1, Valid name list of individual-site static call sites: ", validDic)
        ## For all remaining Static Calls
        ## Sort all strategies per performance impact,
        ## start trying them from the most to the less impact.
        if len(validDic.keys()) < 1:
            return (set(), searchSet)
        if len(validDic.keys()) < 2:
            ## take Best individual as solution
            onlyCorrectIndividual = list(validDic.values())[0]
            spConvertedSet = set(onlyCorrectIndividual)
            searchSet = searchSet - spConvertedSet
            return (spConvertedSet, searchSet)
        toTestListGen = createStratFilesMultiSite(profile, stratDir, validDic, sloc)
        assert toTestListGen
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
            if verbose > 2:
                print("Level1 Multi-Site ToTest name list: ", [x[0] for x in toTestList])
            for name, btCallSiteList in toTestList:
                valid = runApp(cmd, stratDir, name, args.verif_text, envStr, profile._nbTrials)
                if valid:
                    spConvertedSet = set(btCallSiteList)
                    profile.trialSuccess(btCallSiteList, sloc)
                    ## Revert success because we testing individual
                    searchSet = searchSet - spConvertedSet
                    profile.display()
                    return (spConvertedSet, searchSet)
                else:
                    profile.trialFailure()
                    profile.display()
        return (spConvertedSet, searchSet)