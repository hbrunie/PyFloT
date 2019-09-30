#!/usr/bin/env python3
import sys

from parse import parse
from Profiling import Profiling

args = parse()
## First code execution
profile = Profiling(args.binary, args.directory, args.profilefile, args.param,
        args.outputfile, args.onlyGenStrat, args.onlyApplyingStrat)
if args.onlyProfile:
    exit(0)
stopSearch = False
## Calls Strategy constructor
stratGen = profile.developStrategy()
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
