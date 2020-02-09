#!/usr/bin/env python3
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from config import parse

import json
import sys
import re
import os

def sourceCode(callstack):
    " Extract function callstack info(filename+LOC) from callstack return from backtrace_symbols"
    res = None
    for call in callstack:
         regex = "[-_a-zA-Z/.0-9]+\\([a-zA-Z_0-9+]*\\)\\s\\[(0x[a-f0-9]+)\\]"
         m = re.search(regex, call)
         #TODO: intercept command result and store in python var
         os.system("addr2line -f -C -e ./PeleC1d.gnu.haswell.ex {}".format(m.group(1)))
    return res #TODO

import statistics
def fatTail(l):
    " Returns the number of elements in tail"
    return statistics.mean(l) + 2*np.sqrt(np.var(l)/(len(l)-1));

def dumpStatistics(arglist):
    "Dump stats using different python package. Comment what not wanted"
    #print("Use statistics ",stats.describe(arglist)) ## from statistics
    print("Use numpy ","mean({:.4E}) median({:.4E}) stdev({:.4E}) min({:.4E}) max({:.4E})".format(np.mean(arglist), np.median(arglist), np.std(arglist), min(arglist), max(arglist))) ## from numpy
    #print("Use statistics and numpy ","mean({:.4E}) median({:.4E}) stdev({:.4E}) min({:.4E}) max({:.4E}) skew({:.4E}) fat_tail({:.4E}) kurtosis({:.4E})".format(np.mean(arglist), np.median(arglist), np.std(arglist), min(arglist), max(arglist), skew(arglist), fatTail(arglist), kurtosis(arglist))) ## from numpy + statistics


def plotDfFigure(output, df, x, y, colorId, title, xlabel, ylabel, scalefactor, xlim, ylim,
        symlog=True, Format="png", xtickOff = False):
    "Plot figure with DataFrame of pdande"
    #fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    ax1 = df.plot.scatter(x=x,y=y,c=df.Color)
    ax1.set(xlim=xlim,ylim=ylim)
    if symlog:
        ax1.set_yscale('symlog',linthreshy=1e-25)
    size = plt.gcf().get_size_inches()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if xtickOff:
        plt.tick_params(
        axis='y',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        left=False,      # ticks along the bottom edge are off
        right=False,         # ticks along the top edge are off
        labelleft=False) # labels along the bottom edge are off

    plt.subplots_adjust(right=0.4)
    plt.legend(handles=[mpatches.Patch(color=COLORS[callSiteId], label=f'Dynamic backtrace from comp_Kc {callSiteId%3}/3') for callSiteId in range(3*6+8,3*6+8+3)], loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig(f'plotDfScatter-{output}.{Format}')

def plotFigure(arglist, fname, identity, appName, source, 
        boxplot = False,
        scalefactor = 1,
        Format="png"):
    """ Create a plotBox-{filename}-{len(arglist)}.{Format} showing 
        the distribution of the argument values in arglist.
    """ 
    rang = abs(max(arglist)-min(arglist))
    border = 0.1*rang
    mymin=0
    ##BoxPlot
    xlabel = "Call sites"
    ylabel = "Exponential call argument value."
    tile = "Boxplot of exponential call argument values distribution: "
    ##PointsPlot
    xlabel = "Exp calls in execution time order. Serial execution."
    ylabel = "Exponential call argument value. Floating point expression evaluated."
    title = "Exponential call argument values against time: "

    typ = "Points"
    if boxplot:
        plt.boxplot(arglist)
        plt.ylim(min(arglist)-border,max(arglist)+border)
    else:##plotPoints
        typ = "Points"
        border = 0.001*rang
        plt.plot(range(len(arglist)),arglist, 'ro')
        plt.axis([0, len(arglist), min(min(arglist)-border, mymin), max(arglist)+border])
        size = plt.gcf().get_size_inches()
        if scalefactor > 1:
            plt.gcf().set_size_inches(size[0]*scalefactor, size[1]*scalefactor, forward=True)
            plt.rcParams.update({'font.size': 18})

    plt.title(title + f"execution profile of {appName}.")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    s = len(arglist)
    plt.savefig(f'plot{typ}-{identity}-{fname}-len{s}.{Format}')

def alist(icss, s, i):
    return [x[s]  if x[s] else 0 for x in icss[i]["ShadowValues"]]

COLORS = ["blue", "orange", "green","red", "purple", "brown", "pink", "gray", "olive", "cyan"]
TABCOLORS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
##[6, 6, 6, 8, 3, 7, 7, 7, 3]
COLORS=["#AED6F1","#85C1E9","#5DADE2","#3498DB","#2E86C1","#2874A6",
        "#F8C471","#F5B041","#F39C12","#D68910","#B9770E","#7E5109",
        "#7DCEA0","#52BE80","#27AE60","#229954","#1E8449","#196F3D",
        "#F5B7B1","#F1948A","#EC7063","#E74C3C","#CB4335","#B03A2E","#943126","#78281F",
        "#BB8FCE","#8E44AD","#6C3483",
        "#E59866", "#DC7633", "#D35400", "#BA4A00", "#A04000", "#873600", "#6E2C00",
        "#EFA7EF", "#EE8FEE", "#E865E8", "#E44CE4","#DA31DA","#D526D5","#C31AC3",
        "#D5D5D5", "#C0C0C0","#A5A5A5","#929292","#808080","#666666","#494949",
        "#829C47","#728C37","#5D7624"
        ]
TABCOLORS = COLORS

def pdDynamicCalls(fname):
    """ Treat dynamic calls
    """
    with open(fname,"r") as inf:
        ## Load JSON file
        d = json.load(inf)
        ## Extract all DYNAMIC call sites: depending on profiling (if depth == 1 --> STATIC call sites)
        icss = d["IndependantCallStacks"]
        ## generate DataFrame from JSON dictionary of all call sites
        dfList = []
        minList = []
        maxList = []
        staticID = 0
        staticCallSiteTmp = "None"
        dynamicPathPerCallSite = []
        ## CallStack goes from [3:-2]
        for ics in icss:
            if staticCallSiteTmp != ics["CallStack"][3]:
                dynamicPathPerCallSite.append(0)
                staticCallSiteTmp = ics["CallStack"][3]
                staticID += 1
            ics["CallSite"] = staticID
            dynamicPathPerCallSite[-1] += 1
        print(staticID, dynamicPathPerCallSite, sum(dynamicPathPerCallSite))

import os

#USE ONLY ONE OF THESE:

#os.environ["MODIN_ENGINE"] = "dask"  # Modin will use Dask
os.environ["MODIN_ENGINE"] = "ray"  # Modin will use Ray

import modin.pandas as pd

def pdTreatFile(fname,appName, output, csv=False):
    with open(fname,"r") as inf:
        ## Load JSON file
        d = json.load(inf)
        ## Define some colors for nice display
        color_dict = {}
        ## Extract all DYNAMIC call sites: depending on profiling (if depth == 1 --> STATIC call sites)
        icss = d["IndependantCallStacks"]
        ## generate DataFrame from JSON dictionary of all call sites
        dfList = []
        minList = []
        maxList = []
        def my_map_func(l):
            if len(l) < 2:
                return 0
            double = l[0]
            arg = l[1]
            EPSILON = 1e-25
            if abs(double) < EPSILON:
                return 0.
            elif arg > 90:
                return 0.
            else:
                print(arg,double)
                exit(-1)
        for i in range(0,len(icss)):
            if csv:
                colnames = ["index","arg","double","single","absErr","relErr","spBoolean"]
                dfList.append(pd.read_csv(icss[i]["CSVFileName"],names=colnames, header=None))
            else:
                dfList.append(pd.DataFrame.from_dict(icss[i]["ShadowValues"], orient='columns'))
        for i,df in enumerate(dfList):
            df.to_feather(f"dfToFeather-{i}.feather")

        for i,df in enumerate(dfList):
            df.loc[df.relErr.isnull(), 'relErr'] = df.loc[df.relErr.isnull(), ['double','arg']].apply(my_map_func, axis=1)
            #df["relErr"] = df["relErr"].fillna(computeRelErr(df["double"],df["single"]),1e-25)
            ## ReName the callStack for clear display
            df["CallStack"] ="cs{i}"
            ## Attribute color to call site 0
            #color_dict["cs{i}"] = TABCOLORS[i]
            #df["Color"] = COLORS[i]
            #df["absErr"] = [1]*len(df["absErr"])
            df["Color"] = TABCOLORS[i%len(TABCOLORS)]
            ## Extract min/max values (absErr) from call site 4
            minList.append(min(alist(icss, "absErr", i)))
            maxList.append(max(alist(icss, "absErr", i)))
            ## TODO deal with the different order of magnitude
            #df = df.loc[df.absErr >= 10]

            print("relErr")
            dumpStatistics(df['relErr'].tolist())
            print("absErr")
            dumpStatistics(df['absErr'].tolist())
            #print(i,len(alist(icss,i)),len([x for x in alist(icss,i) if x > (M - 1000) ]))

        ## Merge all df in one
        df0 = dfList[0]
        print(len(df0))
        for df in dfList[1:]:
            df0 = df0.append(df)
            print(len(df0))

        ## Index each dynamic call by Extract the magnitude of list values
        ##TODO: this CAN BE COMPLETELY WRONG!!!! take the index given by profiling
        #df["index"] = range(sum([len(x["ShadowValues"]) for x in icss]))
        #tmplist = []
        #for x in icss:
        #    for y in x["ShadowValues"]:
        #        tmplist.append(y["index"])
        #df0["index"] = tmplist

        df0["index"] = [x["index"] for ics in icss for x in ics["ShadowValues"]]

        xmin = min(df0["index"])
        xmax = max(df0["index"])

        #title = "Single precision exponential calls relative to double precision error\nagainst time in Premixed Flame Regression Test from PeleC code.\nTest was run in serial on Haswell (Cori)."
        title = "Call order."
        title = ""
        xlabel = "Order of execution at runtime."
        #ylabel ="Relative Error (|DPvalue - SPvalue| / |SPvalue|)"
        ylabel =""
        scalefactor = 1
        xlim = (xmin,xmax)
        xlim = (66800,67200)
        #ylim = (-1e-25,1e35)
        #ylim = (0,4)
        plotDfFigure(output, df0, "index", "absErr", 4, title, xlabel,
                ylabel, scalefactor, xlim, ylim, symlog=True, Format="png", xtickOff=False)

def treatFile(fname,appName, output):
    with open(fname,"r") as inf:
        d = json.load(inf)
        icss = d["IndependantCallStacks"]
        totalCallCount = 0
        csSize = []
        callSitesCallCounts = []
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
            res = []
            test_list = shvalues_absErr
            for val in test_list:
                if val != None :
                    res.append(val)
            shvalues_absErr = res
            if [x for x in shvalues_absErr if x>1e-25]:
                m = min([x for x in shvalues_absErr if x>1e-25])
            else:
                m = 1e-5
            if shvalues_absErr:
                M = max(1,max(shvalues_absErr))
            else:
                M=1
            #plt.hist(shvalues_absErr, bins=[0]+np.geomspace(m, M, 100),color=colors[i]) 
            if i==4:
                print(res)
            plt.hist(shvalues_absErr, bins=100, log=True, color=colors[i]) 
            plt.ylabel("Exponential calls count")
            plt.xlabel("Absolute Error (|DPvalue - SPvalue|)")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            #plt.xscale("symlog")
            #plt.title("Distribution of exponential calls relative error.")
            plt.savefig(f"plotHist-callsite{i}.png")
            plt.clf()
            source = sourceCode(cs_main)
            #plotBox(shvalues_arg, fname,appName, source)
            #plotPoints(shvalues_absErr, fname,appName, output, source)
            csSize.append(len(cs_main))
            totalCallCount += ics["CallsCount"]
            callSitesCallCounts.append(ics["CallsCount"]) 
        #plt.title("Boxplot of exponential calls count against callsites.")
        #plt.xlabel("Callsites")
        #plt.yscale("symlog")
        #plt.xticks(rotation=45, ha='right')
        #plt.ylabel("Exponential calls count.")
        #plt.tight_layout()
        #plt.bar([f"callSites{i}" for i in range(len(callSitesCallCounts))],callSitesCallCounts, color=colors)
        #plt.savefig('plotBox-CallSitesCallsCount-peleC.png')
    return (totalCallCount, csSize)

args = parse()
appName = args.appName
for fname,output in zip(args.jsondata,args.outputfile):
    pdTreatFile(fname,appName,output,csv=True)
    #pdDynamicCalls(fname)
