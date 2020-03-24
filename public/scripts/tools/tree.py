import json
import os
import re

from generateStrat import updateProfile

readJsonProfileFile=".pyflot/profile/dumpProfile.json"
#regex = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
profile = {}

def Tree(readJsonProfileFile):
    """Display tree
    """
    global profile
    with open(readJsonProfileFile, 'r') as json_file:
        profile = json.load(json_file)
    (staticCalls,dynCalls) = updateProfile(profile)
    for scs in staticCalls:
        print("static,",scs["name"])
        for x in dynCalls:
            if scs["HashKey"] in x["HashKey"]:
                print("--->dynamic,",x["name"])

Tree(".pyflot/profile/profile.json")
