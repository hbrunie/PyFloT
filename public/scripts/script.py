#!/opt/local/bin/python
#from subprocess import Popen, PIPE
import subprocess
import os
import argparse

def check_result(checkstring, output):
    return checkstring in output

class Profile:
    maxbound = 0
    total_dyncount_text = "None"

    def __init__(self, total_dyncount_text):
        self.total_dyncount_text = total_dyncount_text
        self.get_code_profile(args.binary)
        return None

    def __repr__(self):
        s = "Profile: {} {}".format(self.maxbound, self.total_dyncount_text)
        return s

    def get_code_profile(self, binary):
        procenv = os.environ.copy()
        command = []
        command.append(binary)
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, env=procenv)
        strout = out.decode("utf-8")
        #get count of lowered from output
        for l in strout.splitlines():
            if self.total_dyncount_text in l:
                self.maxbound = int(l.split()[-1])
                break

def execute_once(binary, minb, maxb, verif_text):
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
    res = check_result(verif_text, strout)
    if res:
        return score
    else:
        return -1

def display(score, strategy):
    print("Best score: " + str(score))
    print("Best strategy: " + str(strategy))

import argparse
import configparser
import sys

def parse():
    """ Parse config file, update with command line arguments
    """
    # defaults arguments
    defaults = { "min":0, "max":0 , "verif_text":"VERIFICATION SUCCESSFUL", "total_dyncount_text":"TOTAL_DYNCOUNT", 
            "backtrace_json_file":"data.json"}
    # Parse any conf_file specification
    conf_parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    if args.conf_file:
        config = configparser.ConfigParser()
        config.read([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)
    parser.add_argument("--binary", help="binary file absolute path")
    parser.add_argument("--min", type=int)
    parser.add_argument("--max", type=int)
    parser.add_argument("--total_dyncount_text", help="Text for total dyncount")
    parser.add_argument("--backtrace_json_file", help="JSON file containing backtrace, allcall stacks, number\
            of dynamic calls. Obtain with profiling")
    parser.add_argument("--verif_text", help="Text searched in output to verify the code executed without accuracy error")
    args = parser.parse_args(remaining_argv)
    assert args.binary, "binary absolute path is required"
    return args

def strategy(maxb):
    strat = [(0,maxb),(0,maxb//2),(maxb//2,maxb), (int(3/4 * maxb), maxb)]
    for s in strat:
        yield s

max_score = -1
args = parse()
best_strategy = "Not defined"
if args.min >= args.max:
    profile = Profile(args.total_dyncount_text)
    for minb,maxb in strategy(profile.maxbound):
        score = execute_once(args.binary, minb, maxb, args.verif_text)
        print(score)
        if score > max_score:
            max_score = score
            best_strategy = minb, maxb
            break
else:
    max_score = execute_once(args.binary, args.min, args.max, args.verif_text)
    best_strategy = args.min, args.max
display(max_score, best_strategy)
