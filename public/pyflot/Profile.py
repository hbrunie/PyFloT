#from colorama import Fore, Back, Style
import os
import json
import pdb
import re

from Trial import Trial

class Profile:
    """ Rename it metada? (profile + score)
    """
    _totalDynCalls          = 0
    _totalSlocCallSites     = 0
    _totalBtCallSites       = 0

    _slocCallSitesSP        = 0
    _btCallSitesSP          = 0
    _dynCallsSP             = 0

    _verbose                = 1
    _doublePrecisionBtSet   = set()
    _doublePrecisionSlocSet = set()
    _profile                = {}
    _correspondanceBt2SLOC  = []
    ## List indexed by SLOC id,
    ## each element is a set of backtrace ID corresponding to
    ## same SLOC id
    _slocListOfBtIdSet = []
    _prevBtCallSitesSP = 0

    def __init__(self, jsonFile, args=None, verbose=1):
        self._verbose = verbose
        if jsonFile == None:
            self.profiling(args)
        else:
            self._profileFile = jsonFile
            with open(jsonFile, 'r') as json_file:
                self._profile = json.load(json_file)
            self.updateProfile()
            self._doublePrecisionSlocSet = set(range(self._totalSlocCallSites))
            Trial._btTypeConfiguration_g =  [0] *self._totalBtCallSites
            Trial._slocTypeConfiguration_g =  [0] *self._totalSlocCallSites
            Trial._scorefile = args.dumpdir + "/" + args.scorefile
            self._onlyOnce = True
            if verbose >1:
                print("List indexed by CLOC id, containing corresponding set BtId: ",self._slocListOfBtIdSet)
        return None

    def initScore(self,args):
        t = Trial(args, self._verbose, initScore=True)
        t.display()
    def getInfoByBtId(self,x):
        return [x]

    def clusternbBtInSLOC(self, sloc):
        n = 0
        for s in sloc:
            n+=len(self._slocListOfBtIdSet[s])
        return n

    def nbBtInSLOC(self, sloc):
        return len(self._slocListOfBtIdSet[sloc])

    def clusterbtweight(self, s):
        weights = []
        for x in s:
            weights.append(self._weightPerBtCallSite[x])
        return sum(weights)

    def btweight(self, x):
        return self._weightPerBtCallSite[x]

    def slocweight(self, x):
        btIdSetList = self._slocListOfBtIdSet[x]
        return self.clusterbtweight(btIdSetList)

    def clusterslocweight(self, s):
        weights = []
        for x in s:
            btIdSetList = self._slocListOfBtIdSet[x]
            weights.append(self.clusterbtweight(btIdSetList))
        return sum(weights)

    def convertBt2SlocSearchSet(self,ss):
        """ Community is a tuple of sets
        """
        newSS = self.convertBt2SlocId(list(ss))
        newSS = set(newSS)
        return newSS


    def convertSloc2BtCommunity(self,com):
        """
        """
        newCom = []
        for c in com:
            newCom.append(self.convertSloc2BtId(c))
        return tuple(newCom)

    def indexInSloc(self,x):
        "bt"
        l = list(self._slocListOfBtIdSet[self._correspondanceBt2SLOC[x]])
        l.sort()
        return l.index(x)

    def convertBt2SlocSingleId(self,i):
        return self._correspondanceBt2SLOC[i]

    def convertBt2SlocId(self,l):
        """and sort
        """
        r = set()
        for i in l:
            r.add(self._correspondanceBt2SLOC[i])
        r = list(r)
        r.sort()
        return r

    def convertSloc2BtId(self, l):
        """ and sort
            in params: list of sloc call sites id [0,1,2]
            use _slocListOfBtIdSet[i] --> set of Bt Id corresponding to SLOC call sites ID i
        """
        r = []
        for i in l:
            r.extend(list(self._slocListOfBtIdSet[i]))
        r.sort()
        return r

    def getHashKeyList(self,l,sloc):
        r = []
        for e in l:
            hk = None
            if sloc:
                for x in self._slocCallSitesList:
                    if x["SlocId"] == e:
                        hk = x["SlocSymbolsHashKey"]
                        break
            else:#BT
                for x in self._btCallSitesList:
                    if x["BtId"] == e:
                        hk = x["HashKey"]
                        break
            assert hk != None
            r.append(hk)
        return r

    def updateProfile(self):
        """ SLOC and backtrace identities are defined by the order of their appearance
            in the profile.json file.
            TODO: make it more robust, according to alphabet order of their BtAddrHashKeys?
        """
        slocreg = "([a-zA-Z0-9._-]+):([0-9]+)"
        btsymbolreg = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
        self._btCallSitesList = self._profile["IndependantCallStacks"]
        self._slocCallSitesList = []
        self._totalBtCallSites = len(self._btCallSitesList)
        self._doublePrecisionBtSet = set(range(self._totalBtCallSites))
        self._weightPerBtCallSite = []
        slocDict = {}
        currentSlocId = 0
        for btCallSite in self._btCallSitesList:
            currentBtId = btCallSite["Index"]
            self._totalDynCalls += btCallSite["CallsCount"]
            self._weightPerBtCallSite.append(btCallSite["CallsCount"])
            ## Building SLOC HashKeys: addr2line
            m = re.search(slocreg, btCallSite["Addr2lineCallStack"][0])
            assert(m)
            slocHKey = m.group(0)
            m = re.search(btsymbolreg, btCallSite["CallStack"][0])
            assert(m)
            slocSymbolsHKey = m.group(1)
            ## Building Backtrace HashKeys: addr2line
            btHKey = ""
            for callstack in  btCallSite["Addr2lineCallStack"]:
                ##addr2line identification
                m = re.search(slocreg, callstack)
                ## don't treat callstack after main
                if callstack == "??:0":
                    break
                assert(m)
                btHKey += m.group(0)
            ## identification
            btCallSite["BtId"] = currentBtId
            ## HashKey already exist in btCallSite: it is the BtHashKey without addr2line
            btCallSite["BtAddrHashKey"] = btHKey
            btCallSite["SlocAddrHashKey"] = slocHKey
            btCallSite["SlocSymbolsHashKey"] = slocSymbolsHKey
            ## If already in dict update CallsCount
            if slocDict.get(slocHKey):
                ## Retrieve slocCallSite from dictionnary
                slocCallSite                    = slocDict[slocHKey]
                ## Update number of dynamic calls done through this SLOC call site
                slocCallSite["SlocCallsCount"] += btCallSite["CallsCount"]
                ## update list indexed by SLOC id, containing backtrace Callsite id set
                self._slocListOfBtIdSet[slocCallSite["SlocId"]].add(currentBtId)
                self._correspondanceBt2SLOC.append(slocCallSite["SlocId"])
            ## If not already in dict
            else:
                btCallSite["SlocId"] = self._totalSlocCallSites
                self._correspondanceBt2SLOC.append(self._totalSlocCallSites)
                self._totalSlocCallSites += 1
                ## update list of backtrace ID corresponding to same SLOC id
                self._slocListOfBtIdSet.append(set([currentBtId]))
                ##Copy of Backtrace Call Site into SLOC Call site
                slocCallSite = btCallSite.copy()
                slocCallSite["SlocAddrHashKey"] = slocHKey
                slocCallSite["SlocCallsCount"] = slocCallSite["CallsCount"]
                slocDict[slocHKey] = slocCallSite
                self._slocCallSitesList.append(slocCallSite)

    def profiling(self, args):
        """ Do profiling
        """
        print("Profiling application ...")
        print(args)
        dumpdir     = args.dumpdir + "/"
        binary      = args.binary
        outputfile  = dumpdir + args.outputfile
        profilefile = dumpdir + args.profilefile
        params = args.params
        _ENVVAR_DUMPDIR            = "PRECISION_TUNER_OUTPUT_DIRECTORY"
        _ENVVAR_PTUNERMODE         = "PRECISION_TUNER_MODE"
        _ENVVAR_OMPNUMTHREADS      = "OMP_NUM_THREADS"
        _ENVVAR_PTUNERDEBUG        = "DEBUG"
        _ENVVAR_BINARY             = "TARGET_FILENAME"
        _ENVVAR_PTUNERDUMPPROF     = "PRECISION_TUNER_DUMPJSON"
        #_ENVVAR_PTUNERDUMPPROFCSV = "PRECISION_TUNER_DUMPCSV"
        _MODE_STRAT                = "APPLYING_STRAT"
        procenv                         = os.environ.copy()
        procenv[_ENVVAR_PTUNERDUMPPROF] = profilefile
        procenv[_ENVVAR_OMPNUMTHREADS]  = "1"
        procenv[_ENVVAR_DUMPDIR]        = dumpdir
        procenv[_ENVVAR_BINARY]         = binary
        ## create profile dump directory if not already exist
        os.system("mkdir -p {}".format(dumpdir))
        print("env: {}={} {}={} {}={} {}={}".format(_ENVVAR_BINARY,procenv[_ENVVAR_BINARY],
            _ENVVAR_DUMPDIR, procenv[_ENVVAR_DUMPDIR],
            _ENVVAR_OMPNUMTHREADS, procenv[_ENVVAR_OMPNUMTHREADS],
            _ENVVAR_PTUNERDUMPPROF, procenv[_ENVVAR_PTUNERDUMPPROF]))
        #procenv["PRECISION_TUNER_DEBUG"] = ""
        command = []
        command.append(binary + " " + params)
        print("PROFILING Command: ",command)
        for var,value in procenv.items():
            os.environ[var] = value
        print(" ".join(command))
        os.system(" ".join(command) + f" >> {outputfile}")
        print("Application profiled")
