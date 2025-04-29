#!/usr/bin/env python3
import sys
from pyflot.main.pyflot_main import PyflotMain

main = PyflotMain()
main.run_from_args(sys.argv[1:])