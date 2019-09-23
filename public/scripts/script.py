#!/usr/bin/env python3
import sys

from parse import parse
from Profiling import Profiling

args = parse()
## First code execution
profile = Profiling(args.binary, args.directory, args.profilefile)
stopSearch = False
## Calls Strategy constructor
stratGen = profile.developStrategy()
while not stopSearch:
    try:
        ## Calls Strategy constructor
        strat = next(stratGen)
    except StopIteration:
        print("No more strategy to test")
        sys.exit()
    if not args.onlyProfile:
        stopSearch = strat.applyStrategy(args.verif_text)
