from init import initDoublePrecisionSet
from init import initStaticCallsSet
from init import initDynamicCallsSet

def FastExploration(Yset):
    """ Take as argument Yset, containing all dynamic calls which should
        be executed in double precision.
    """
    nbCalls = 0
    ExecuteApplication(Xset)
    getNumberCalls(Xset)
    if CheckFinalResult():
        return nbCalls
    else:
        return 0

def MultiSiteSearch(DPset, Eset):
    """ Take as argument:
            - set of Double Precision Calls
            - set of Dynamic Calls Clusters
              (either based on Static call site or
                dynamic call stack/backtrace)
    """
    # S = Union SC s.t. FE(SC)>0
    S = set()
    for sc in SCset:
        if FastExploration(Eset - sc) > 0:
            S.union(sc)
    SortedSearch = combinations(S).sort(score, reverse=True)
    while len(SortedSearch) > 0:
        X = SortedSearch.pop(0)
        if FastExploration(Eset - X) > 0:
            return DPset - X

def HierarchicalSearch(DPset, SCset, DCset):
    """
    """
    DPset = MultiSiteSearch(DPset, SCset)
    DPset = MultiSiteSearch(DPset, DCset)
    return DPset

DPset = initDoublePrecisionSet()
DCset = initDynamicCallsSet(SPset)
SCset = initStaticCallsSet(DCset)

DPset = HierarchicalSearch(DPset, SCset, DCset)
displaySet(DPset)
