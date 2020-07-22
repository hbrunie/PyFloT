import json
import os
import re

profile = {}
verbose = 0

totalDynCalls = 0
totalStatCalls = 0

def updateProfile(profile):
    global totalDynCalls
    global totalStatCalls
    #regex = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
    regex = "([a-zA-Z_0-9]+)\\+([a-f0-9x]+)"
    dynCalls = profile["IndependantCallStacks"]
    staticCalls = []
    staticCallsd = {}
    profile["StaticCalls"] = staticCalls
    profile["StaticCallsd"] = staticCallsd
    maxlvl = 4 #16
    statCount = 0
    dynCount = 0
    for cs in dynCalls:
        cs["dynname"] = f"Dyn-{dynCount}"
        dynCount += 1
        key = ""
        ## Build Static Key with 4 backtrace lvl
        for callstack in  cs["CallStack"][:maxlvl]:
            m = re.search(regex, callstack)
            if not m:
                break
            key += m.group(1) + m.group(2)
        ## If already in dict update CallsCount
        if staticCallsd.get(key):
            scs = staticCallsd[key]
            scs["CallsCount"] += cs["CallsCount"]
            totalDynCalls += cs["CallsCount"]
            statCountMinusOne = statCount - 1
            cs["statname"] = f"statCS-{statCountMinusOne}"
        ## If not already in dict
        ## Add to dict and update name/hashKey/CallsCount
        ## Append to staticCalls list
        else:
            ##Copy of Dynamic Call dictionnary into the staticCall one
            cs["statname"] = f"statCS-{statCount}"
            staticCallsd[key] = cs.copy()
            scs = staticCallsd[key]
            scs["HashKey"] = key
            ##Change dynCall name for static one, in copy
            ##Update StatCall callsCount with dynamic one, in copy
            totalDynCalls += cs["CallsCount"]
            totalStatCalls += 1
            staticCalls.append(scs)
            statCount += 1
    if verbose > 1:
        print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in staticCalls])
        print("Profile: ",[(x["statname"],x["dynname"],x["CallsCount"]) for x in dynCalls])
    return (staticCalls,dynCalls)

def getSourceFromName(name, profile, dynamic = True):
    typename = "statname"
    if dynamic:## dynamic
        calls = profile["IndependantCallStacks"]
    else:
        calls = profile["StaticCalls"]
    allstacks = []
    for call in calls:
        if name in call[typename]:
            allstacks.append(call["Addr2lineCallStack"])
    return allstacks

import sys
jsonFile = sys.argv[1]
name = sys.argv[2]
with open(jsonFile, 'r') as json_file:
    profile = json.load(json_file)
updateProfile(profile)


sourceCode = getSourceFromName(name,profile)
print(sourceCode)
l = []
for x in sourceCode:
    l.append("".join(x))
print("\n".join(l))
