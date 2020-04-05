profile = {}
def initDoublePrecisionSet():
    """ return set of all double precision static call sites
        Now traces contains only double precision calls
        thus return every calls.
    """
    global profile
    ## Load profile via json file
    ## get all static call sites in a set,
    ## identified by a name and HashKey (CallStack)
    ## Returns the set of static call sites

def initDynamicCallsSet(SCset):
    ## get all dynamic call sites COPY in a set,
    ## identified by a name and HashKey (CallStack)
    ## Returns the set of dynamic call sites

def initStaticCallsSet(DPset):
    ## merge Dynamic Call Sets into Static Call sets

