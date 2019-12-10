from parse import parse
import itertools
import math
import subprocess
import os

args = parse()
print(args)

def execute(command, outputfile, procenv):
    out = ""
    try:
        output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, shell=True,
                universal_newlines=True, env=procenv)
    except subprocess.CalledProcessError as exc:
        out = "Status : FAIL\nCode: {}\n{}".format(exc.returncode, exc.output)
    else:
        out = "Output: \n{}\n".format(output)
    with open(outputfile, "w") as ouf:
        ouf.write(out)
    return out

def numStrat(n):
    if n <= 2:
        return n
    else:
        s = 0
        for k in range(1,n):
            s += math.factorial(n) / (math.factorial(k)*math.factorial(n-k))
        return 2 + s

def generateStrat(linelist):
    stratlist = []
    n = len(linelist)
    for k in range(n+1):
        stratlist.extend([set(i) for i in itertools.combinations(set(linelist), k)])
    #print(stratlist)
    assert len(stratlist) == pow(2,n) == numStrat(n)
    return stratlist

def create():
    n = 0
    with open(args.stratfile, "r") as inf:
        linelist = inf.readlines()
        l = generateStrat(linelist)
        n = len(l)
        for i,strat in enumerate(l):
            with open(f"strat{i}.txt","w") as out:
                for line in strat:
                    out.write(line)
    return n

def launch(n):
    procenv = os.environ.copy()
    for i in range(n):
        outputfile = "outputStrat{}.out".format(i)
        cmd = "PRECISION_TUNER_READJSON=dump.json PRECISION_TUNER_DUMPJSON=dumpStratResults{}.json BACKTRACE_LIST=./strat{}.txt PRECISION_TUNER_MODE=APPLYING_STRAT ./test5Exp 3.14".format(i,i)
        #cmd = "PRECISION_TUNER_DUMPJSON=dumpStratResults{}.json BACKTRACE_LIST=./strat{}.txt PRECISION_TUNER_MODE=APPLYING_PROF ./test5Exp 3.14".format(i,i)
        print(cmd)
        execute(cmd, outputfile, procenv)

n = create()
launch(n)
#generateStrat([1,2,3,4])
#for i in range(10):
#    print(i,numStrat(i))
