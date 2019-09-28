ptunerdir=./testConstructor_ptunerdir/
## TEST applying profiling
../../public/scripts/script.py --ptunerdir ${ptunerdir} --onlyApplyingProf --binary ./testConstructor\
    --profilingfile testConstructor_profiling.json
## TEST generating strategy
../../public/scripts/script.py --ptunerdir ${ptunerdir} --onlyGenStrat --binary ./testConstructor\
    --stratgenfiles testConstructor_readstrat.json
## TEST applying one strategy
../../public/scripts/script.py --ptunerdir ${ptunerdir} --onlyApplyingStrat --binary ./testConstructor\
    --readstratfiles testConstructor_readstrat.json
