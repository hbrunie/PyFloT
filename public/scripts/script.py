#!/usr/bin/env python3
import sys

from parse import parse
from Profiling import Profiling

args = parse()
print(args.stratfiles)
## First code execution

profile = Profiling(args.binary, args.ptunerdir, args.profilefile, args.param, 
        args.outputfile,
        doNotExec=args.onlyGenStrat or args.onlyApplyingStrat)
if args.onlyProfile:
    exit(0)
stopSearch = False
## Calls Strategy constructor
<<<<<<< HEAD
stratGen = profile.developStrategy(args.onlyApplyingStrat, args.stratgenfiles, 
        args.readstratfiles)
=======
stratGen = profile.developStrategy()
>>>>>>> master
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
