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
    print("Use statistics ",stats.describe(arglist)) ## from statistics
    print("Use numpy ","mean({:.4E}) median({:.4E}) stdev({:.4E}) min({:.4E}) max({:.4E})".format(np.mean(arglist), np.median(arglist), np.std(arglist), min(arglist), max(arglist))) ## from numpy
    print("Use statistics and numpy ","mean({:.4E}) median({:.4E}) stdev({:.4E}) min({:.4E}) max({:.4E}) skew({:.4E}) fat_tail({:.4E}) kurtosis({:.4E})".format(np.mean(arglist), np.median(arglist), np.std(arglist), min(arglist), max(arglist), skew(arglist), fatTail(arglist), kurtosis(arglist))) ## from numpy + statistics


def plotDfFigure(df, x, y, colorId, title, xlabel, ylabel, scalefactor, xlim, ylim, symlog=True, Format="png"):
    "Plot figure with DataFrame of pdande"
    #fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax1 = df.plot.scatter(x=x,y=y,c=df.Color)
    ax1.set(xlim=xlim,ylim=ylim)
    if symlog:
        ax1.set_yscale('symlog',linthreshy=1e-25)
    size = plt.gcf().get_size_inches()
    plt.legend(handles=[mpatches.Patch(color=COLORS[callSiteId], label=f'call site{callSiteId}') for callSiteId in range(9)])
    plt.savefig(f'plotDfScatter.{Format}')

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

def treatCallSite(icss ,ID):
    """ Treat on call site
    """
    df = pd.DataFrame.from_dict(icss[ID]["ShadowValues"], orient='columns')
    df["CallStack"] =f"cs{ID}" 
    color_dict[f"cs{ID}"] = COLORS[ID]
    if ID== 4:
        df["absErr"] = df["absErr"].fillna(1e31)
    df0 = df0.append(df)
    df1 = df1.append(df.loc[df.absErr >= 10])
    dumpStatistics(alist(icss,ID))

    print(ID,len(alist(icss,ID)),len([x for x in alist(icss,ID) if x > (M - 1000) ]))

    m = min(m,min(alist(icss, "absErr", ID)))
    M = max(M, max(alist(icss, "absErr", ID)))

def pdTreatFile(fname,appName, output):
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
        for i in range(0,len(icss)):
            dfList.append(pd.DataFrame.from_dict(icss[i]["ShadowValues"], orient='columns'))

        for i,df in enumerate(dfList):
            if i== 4:
                df["absErr"] = df["absErr"].fillna(1e31)
            ## ReName the callStack for clear display
            df["CallStack"] ="cs{i}" 
            ## Attribute color to call site 0
            #color_dict["cs{i}"] = TABCOLORS[i]
            #df["Color"] = COLORS[i]
            df["Color"] = TABCOLORS[i]
            ## Extract min/max values (absErr) from call site 4
            minList.append(min(alist(icss, "absErr", i)))
            maxList.append(max(alist(icss, "absErr", i)))
            ## TODO deal with the different order of magnitude
            #df = df.loc[df.absErr >= 10]

            #dumpStatistics(alist(icss,i))
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

        title = "Single precision exponential calls relative to double precision error\nagainst time in Premixed Flame Regression Test from PeleC code.\nTest was run in serial on Haswell (Cori)."
        xlabel = "Ordered by execution order"
        ylabel ="Relative Error (|DPvalue - SPvalue| / |SPvalue|)"
        scalefactor = 2
        xlim = (xmin,xmax)
        ylim = (-1e-25,1e35)
        plotDfFigure(df0, "index", "absErr", 4, title, xlabel, ylabel, scalefactor, xlim, ylim)

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
    #treatFile(fname,appName,output) 
    pdTreatFile(fname,appName,output)
