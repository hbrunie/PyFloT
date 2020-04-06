#!/usr/bin/env python3
import sys

from parse import parseProfiling
from Profiling import Profiling

args = parseProfiling()
dontExecApp4Profile = args.onlyGenStrat or args.onlyApplyingStrat
profile = Profiling(args, dontExecApp4Profile)
if args.onlyProfile:
    exit(0)
stopSearch = False
## Calls Strategy constructor
stratGen = profile.developStrategy(args.stratfiles)
while not stopSearch:
    try:
        ## Calls Strategy constructor
        strat = next(stratGen)
    except StopIteration:
        if args.onlyGenStrat:
            print("No more strategy to generate.")
        else:
            print("No more strategy to test.")
        sys.exit()
    if not args.onlyGenStrat:
        stopSearch = strat.applyStrategy(args.verif_text)
