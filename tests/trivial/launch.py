import os
import subprocess
from outputs import *
tests = ["./testConstructor", "./testExp", "./testHeader", "./testMathFunctions"]
tests = ["./test5Exp"]
optionBin = ["--onlyProfile", "--onlyGenStrat", "--onlyApplyingStrat", ""]
script = "../../public/scripts/script.py"

def dump(f,s):
    with open(f,"a") as inf:
        inf.write(s)
def execute(command):
    try:
        output = subprocess.check_output(
                            command, stderr=subprocess.STDOUT, shell=True,
                                    universal_newlines=True)
    except subprocess.CalledProcessError as exc:
            out = "{}".format(exc.output)
    else:
        out = "{}".format(output)
    return out

for binary in tests:
    ptunerdir = f"{binary}_ptunerdir/"
    #options = f"--stratfiles {binary}_readstrat.json --ptunerdir {ptunerdir} --binary {binary} --profilefile {binary}_profiling.json"
    options = f"--ptunerdir {ptunerdir} --binary {binary} --profilefile {binary}_profiling.json"
    for opt in optionBin:
        command = f"{script} {options} {opt}"
        print(command)
        out = execute(command)
        output = outputs.pop(0)
        #print("cmdout", out)
        #print("refoutput",output)
        #dump("cmdOutput",out)
        #dump("refOutput",output)
        print(out == output)
    os.system(f"rm {ptunerdir}*.txt {ptunerdir}*.json")
