#!/usr/bin/env python3
import sys
import pdb

from parse import parseProfiling
from Profile import Profile

args = parseProfiling()
Profile(None,args=args)
