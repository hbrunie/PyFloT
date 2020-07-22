#!/usr/bin/env python3
import argparse
import configparser
import sys
def get_config(confPath):
    config = configparser.ConfigParser()
    config.optionxform=str
    try:
        config.read(confPath)
        return config
    except Exception as e:
         log.error(e)

def parse():
    """ Parse config file, update with command line arguments
    """
    # defaults arguments
    defaults = { "jsondata" : "data.json",
            "appName" : "MyGreatApplication",
            "outputfile" : "OneMoreFile"}
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
        config = get_config([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)

    parser.add_argument("--jsondata", nargs="+",
            help="List of json files containing PrecisionTuning profiling.")

    #parser.add_argument("--appName", nargs="+",
    #help="Application profiled name.")

    #parser.add_argument("--outputfile", nargs="+",
    #help="List of ouput names for plot files.")

    args = parser.parse_args(remaining_argv)
    return args


import numpy as np
#import statistics
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
#from scipy.stats import kurtosis, skew

import json
import sys
import re
import os


def fatTail(l):
    return statistics.mean(l) + 2*np.sqrt(np.var(l)/(len(l)-1));

def sourceCode(callstack):
    res = None
    for call in callstack:
         regex = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
         m = re.search(regex, call)
         #TODO: intercept command result and store in python var
         os.system("addr2line -f -C -e ./PeleC1d.gnu.knl.PTuner.ex {}".format(m.group(1)))
    return res #TODO

def dumpStatistics(arglist):
    print("mean({:.4E}) median({:.4E}) stdev({:.4E}) min({:.4E}) max({:.4E})".format(np.mean(arglist), np.median(arglist), np.stdev(arglist), min(arglist), max(arglist)))


def dumpFullStatistics(arglist):
    print("mean({:.4E}) median({:.4E}) stdev({:.4E}) min({:.4E}) max({:.4E}) skew({:.4E}) fat_tail({:.4E}) kurtosis({:.4E})".format(np.mean(arglist), np.median(arglist), np.stdev(arglist), min(arglist), max(arglist), skew(arglist), fatTail(arglist), kurtosis(arglist)))

def plotBox(arglist, fname, appName, source):
    rang = abs(max(arglist)-min(arglist))
    border = 0.1*rang
    plt.title(f"Boxplot of exponential call argument values distribution: execution profile of {appName}.")
    plt.xlabel("None")
    plt.ylabel("Exponential call argument value. Floating point expression evaluated.")
    plt.boxplot(arglist)
    plt.ylim(min(arglist)-border,max(arglist)+border)
    plt.savefig('plotBox-{}-len{}.png'.format(fname,len(arglist)))

def plotPoints(arglist,fname, appName, output, source):
    print(source)
    rang = abs(max(arglist)-min(arglist))
    mymin=0
    border = 0.001*rang
    plt.title(f"Exponential call argument values against time: execution profile of {appName}.")
    plt.xlabel("Exp calls in execution time order. Serial execution.")
    plt.ylabel("Exponential call argument value. Floating point expression evaluated.")
    plt.plot(range(len(arglist)),arglist, 'ro')
    plt.axis([0, len(arglist), min(min(arglist)-border, mymin), max(arglist)+border])
    size = plt.gcf().get_size_inches()
    plt.gcf().set_size_inches(size[0]*10, size[1]*10, forward=True)
    plt.rcParams.update({'font.size': 600})
    plt.savefig("plotPoints-{}-{}-len{}.png".format(fname,output,len(arglist)))

def treatFile(fname,appName, output):
    with open(fname,"r") as inf:
        d = json.load(inf)
        icss = d["IndependantCallStacks"]
        totalCallCount = 0
        csSize = []
        for i,ics in enumerate(icss):
            cs = ics["CallStack"]
            sv = ics["ShadowValues"]
            ## split call stack into:
            # part in PrecisionTuning lib
            # part in source code
            # part libc, before calling main (_start, etc.)
            cs_ptlib = cs[0:3]
            cs_main = cs[3:-2]
            cs_beforemain = cs[-2:]
            shvalues_arg =[x["arg"] for x in sv]
            shvalues_doublePres = [x["double"] for x in sv]
            shvalues_singlePres = [x["single"] for x in sv]
            shvalues_singlePres = [x["single"] for x in sv]
            shvalues_absErr = [x["absErr"] for x in sv]
            shvalues_relErr = [x["relErr"] for x in sv]
            source = sourceCode(cs_main)
            print(source)
            #plotBox(shvalues_arg, fname,appName, source)
            #plotPoints(shvalues_absErr, fname,appName, output, source)
            csSize.append(len(cs_main))
            totalCallCount += ics["CallsCount"]
    return (totalCallCount, csSize)

args = parse()
appName = args.appName
for fname,output in zip(args.jsondata,args.outputfile):
   treatFile(fname,appName,output)
