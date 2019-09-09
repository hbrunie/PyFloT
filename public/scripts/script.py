#!/opt/local/bin/python
#from subprocess import Popen, PIPE
import subprocess
import os
import argparse
import sys

from parse import parse
from Profiling import Profiling

args = parse()
profile = Profiling(args.binary, args.directory)
stopSearch = False
stratGen = profile.developStrategy()
while not stopSearch:
    try:
        strat = next(stratGen)
    except StopIteration:
        print("No more strategy to test")
        sys.exit()
    stopSearch = strat.applyStrategy(args.verif_text)
