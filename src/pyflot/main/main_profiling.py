#!/usr/bin/env python3
import sys

from pyflot.profiling.Profiling import Profiling
from pyflot.configuration.config_handler import ConfigHandler

config = ConfigHandler()
config.update_from_args(" ".join(sys.argv[1:]))
profile = Profiling(config)
if config.only_profile:
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
