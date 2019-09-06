#!/opt/local/bin/python
#from subprocess import Popen, PIPE
import subprocess
import os
import argparse

from parse import parse
from Profile import Profile

def checkResult(checkstring, output):
    return checkstring in output

def executeOnce(binary, minb, maxb, verif_text):
    bounds = "{}-{}".format(minb, maxb)
    score = maxb - minb
    procenv = os.environ.copy()
    procenv["MINBOUND"] = str(minb)
    procenv["MAXBOUND"] = str(maxb)

    #dynamic combination to test: strategy choice
    command = []
    command.append(binary)
    out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
    strout = out.decode("utf-8")
    print(strout)

    #get count of lowered from output
    for l in strout.splitlines():
        if "LOWERED" in l:
            print(l.split())
            lowered_count = int(l.split()[-1])
    assert(lowered_count == score), "lowered count {} != score {} | bounds {} | OUTPUT\n {}".format(lowered_count, score,bounds,strout)
    res = checkResult(verif_text, strout)
    if res:
        return score
    else:
        return -1

args = parse()
profile = Profile(args.binary, args.dumpJsonProfileFile)
stopSearch = False
while not stopSearch:
    strat = profile.developStrategy()
    stopSearch = strat.applyStrategy()
