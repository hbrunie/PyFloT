import os
tests = ["./testConstructor", "./testExp", "./testHeader", "./testMathFunctions"]
optionBin = ["--onlyProfile", "--onlyGenStrat", "--onlyApplyingStrat"] 
script = "../../public/scripts/script.py"
    
for binary in tests:
    ptunerdir = f"{binary}_ptunerdir/"
    options = f"--stratfiles {binary}_readstrat.json --ptunerdir {ptunerdir} --binary {binary} --profilefile {binary}_profiling.json"
    for opt in optionBin:
        command = f"{script} {options} {opt}"
        print(command)
        os.system(command)
    os.system(f"rm {ptunerdir}*.txt {ptunerdir}*.json")

