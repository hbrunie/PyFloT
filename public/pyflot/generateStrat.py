import json
import pdb
import os
import re
from itertools import permutations
import itertools

verbose = 0

def createStratFilesCluster(profile, stratDir, communities, depth, sloc):
    """ Always return under form of BtId
        community is a set of btCallSite ID
        communities: ({0, 1, 2, 3, 4}, {5, 6})
    """
    stratList = []
    os.system(f"mkdir -p {stratDir}")
    for counter,community in enumerate(communities):
        ##build community name
        name = f"depth-{depth}-community-{counter}"
        stratList.append((name, community))
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            hashKeyList = profile.getHashKeyList(community, sloc)
            for key in hashKeyList:
                ouf.write(key+"\n")
                #TODO: check this is the right keys ...
    ##Sort the strategy to test by performance weight: x: (name, community)
    if sloc:
        stratList.sort(key=lambda x: profile.clusterslocweight(x[1]), reverse=True)
    else:
        stratList.sort(key=lambda x: profile.clusterbtweight(x[1]), reverse=True)
    if verbose>0:
        n=len(communities)
        print(f"{n} files created.")
    ## Return list of tuples (names, community)
    return stratList

def createStratFilesMultiSite(profile, stratDir, validDic, sloc):
    """
        Generates files containing backtrace keys (@) for strategies to be tested.
        Individual configurations have been tested in previous phase:
        For each call site, type configuration reducing only this one precision has been tested.
        validDic: {'depth-0-community-0': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
    """
    ## Create strategies directory
    os.system(f"mkdir -p {stratDir}")
    ## Extract names of valid type configurations tested during individual phase
    nameSet = set(validDic.keys())
    setSize = len(nameSet)
    ## define approach name: backtrace or sloc
    approachName = "backtrace"
    if sloc:
        approachName = "SLOC"
    ## Testing multi-site type configurations reducing precision
    ## of simultaneously n valid individual,
    ## starting with n equal sizeSet and decreasing.
    for n in range(setSize,1,-1):
        ## List of all subset strategies of n among sizeSet
        namesubsets = list(itertools.combinations(nameSet, n))
        couplesubsets = []
        ##sort subsets according to weight
        for namesubset in namesubsets:
            btIdList = []
            for name in namesubset:
                btIdList.extend(validDic[name])
            couplesubsets.append((list(namesubset), btIdList))
        if sloc:
            couplesubsets.sort(key= lambda x: profile.clusterslocweight(x[1]), reverse=True)
        else:
            couplesubsets.sort(key= lambda x: profile.clusterbtweight(x[1]), reverse=True)
        stratList = []
        for key,couplesubset in enumerate(couplesubsets):
            name = f"multiSite-{approachName}-i{key}-k{n}-among{setSize}"
            stratList.append((name,list(couplesubset[1])))
            fkeys = f"strat-{name}.txt"
            fnames = f"strat-{name}-ids.txt"
            ##If sloc: need to convert btCallSite ID into slocCallSite ID for getHashKeyList
            ##TODO not needed anymore
            CallSiteIdSet = couplesubset[1]
            with open(stratDir+fkeys, 'a') as ouf:
                ## Write backtrace or sloc id
                towrite = list(CallSiteIdSet)
                for x in towrite[:-1]:
                    ouf.write(x+" ")
                ouf.write(x+"\n")
            ## Convert sloc id to bt id set if necessary
            if sloc:
                CallSiteIdSet = set()
                for x in couplesubset[1]:
                    CallSiteIdSet.add(profile._correspondanceBt2SLOC[x])
            keys = profile.getHashKeyList(CallSiteIdSet, sloc)
            with open(stratDir+fnames, 'a') as ouf:
                for key in keys:
                    ouf.write(key+"\n")
        ## Return list of performance ordered subset names
        yield stratList
    ## Generating strategy files: do not generate best individual
    print("No MultiStrategy found. Back to best individual strategy.")
    return []

def createStratFilesMultiSiteSLOC(stratDir, jsonFile, validNameHashKeyList):
    return createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, True)

def createStratFilesMultiSiteBacktrace(stratDir, jsonFile, validNameHashKeyList):
    return createStratFilesMultiSite(stratDir, jsonFile, validNameHashKeyList, False)

def createStratFilesIndividuals(profile, stratDir, searchSet, sloc):
    """ Static: level1
        Create strategy files, for each individual SLOC or BT call sites
        searchSet contains the call site identity:
            - btCallSite["SlocId"]
            - btCallSite["BtId"]
    """
    stratList = []
    os.system(f"mkdir -p {stratDir}")
    ## CallSiteId represents slocCallSiteId if sloc, else btCallSiteId
    if sloc:
        searchList = list(searchSet)
        searchList.sort(key= lambda x: profile.slocweight(x), reverse=True)
    else:
        searchList = list(searchSet)
        searchList.sort(key= lambda x: profile.btweight(x), reverse=True)
    for CallSiteId in searchList:
        ## CallSiteId represents slocCallSiteId if sloc, else btCallSiteId
        if sloc:
            name = f"sloc-{CallSiteId}"
        else:
            name = f"bt-{CallSiteId}"
        stratList.append((name, [CallSiteId]))
        with open(stratDir+f"strat-{name}.txt", 'a') as ouf:
            ##TODO: be  sure CallSiteId is btCallSite ID and not slocCallSite ID
            hashKeyList = profile.getHashKeyList([CallSiteId], sloc)
            for key in hashKeyList:
                ouf.write(key+"\n")
    if verbose>0:
        n = len(stratList)
        print(f"{n} files created.")
    ## Return list of tuples (names, community)
    return stratList
