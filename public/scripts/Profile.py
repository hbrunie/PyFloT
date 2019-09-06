class Profile:
    __binary = "None"
    __dumpJsonProfileFile = "None"

    def __init__(self, binary, dumpJsonProfileFile):
        self.__binary = binary
        self.__dumpJsonProfileFile = dumpJsonProfileFile
        assert self.__dumpJsonProfileFile != "None"
        self.get_code_profile()
        return None

    def __repr__(self):
        s = "Profile: binary({}) dumpJsonProfileFile({})".format(
                self.__binary, self.__dumpJsonProfile)
        return s

    def getCodeProfile(self):
        procenv = os.environ.copy()
        procenv["DUMPJSONPROFILINGFILE"] = __dumpJsonProfileFile
        command = []
        command.append(self.__binary)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        ## TODO:check the dumpJsonProfilingFile file has been created
        ## TODO:check its content

    def developStrategy(self):
        strategies = []
        stop = False
        count = 0
        while (True):
            readJsonStratFile = directory + "readJsonStrat_{}.json".format(count)
            dumpJsonStratResultsFile = directory + "dumpJsonStratResults_{}.json".format(count)
            strat = Strategy(__dumpJsonProfileFile, readJsonStratFile, dumpJsonStratResultsFile)
            yield strat
            count += 1
