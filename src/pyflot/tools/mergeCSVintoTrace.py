from parse import parseMergeCSVintoTrace
import sys
import os
import pdb
def bashCmd(directory, dumpdir):
    tmpfile = "mergeCSVintoTrace.tmp"
    traceAbsPath = f"{dumpdir}/mergeCSVintoTrace.trace"
    cmd = f"for f in `ls {directory}/*.csv` ; do sed -i -e '/^$/d' $f ; done ;"
    os.system(cmd)
    cmd = f"for f in `ls {directory}/*csv` ; do tail -n +2 $f >> {tmpfile} ; done;"
    os.system(cmd)
    cmd = f"sort -n -s -k1,1 {tmpfile} >> {traceAbsPath}"
    os.system(cmd)
    cmd = f"rm -f {tmpfile}"
    os.system(cmd)
    return traceAbsPath

def checkTrace(inf):
    #pdb.set_trace()
    missingIndexes = []
    missingIndex = False
    last_timestamp = 0.
    index = 0
    totalIndex = 0
    totalMiss = 0
    plast = 0
    for l in inf.readlines():
        totalIndex += 1
        ls = l.split()
        ## check complete index counting
        first = index
        while index != int(ls[0]):
            missingIndex = True
            totalMiss += 1
            index += 1
        last = index
        if missingIndex:
            if first != plast:
                missingIndexes.append(float(last-first)/float(first - plast))#, first, last))
            else:
                missingIndexes.append((first - plast,last-first))#, first, last))
            plast = index
        missingIndex = False
        index += 1
        ## check time is increasing
        assert(float(last_timestamp)<float(ls[1]))
        last_timestamp = float(ls[1])
    print(missingIndexes)
    print("In between", ", missed interval")
    print(len(missingIndexes))
    print(totalIndex,totalMiss,float(totalMiss)/float(totalIndex))

args = parseMergeCSVintoTrace()
trace = bashCmd(args.directory, args.dumpdir)
if args.check:
    with open(trace, "r") as inf:
        checkTrace(inf)
