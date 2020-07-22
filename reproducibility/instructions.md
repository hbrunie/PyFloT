## Installing PyFloT (same instructions as in the README.md):

```
git clone git@github.com:hbrunie/PyFloT.git
cd PyFloT
git submodule update --init --recursive
```

* install python3.7+
* install g++8.3+ # On Cori it is important to module load PrgEnv-gnu

** change the path inside environ.source --> /absolute/path/to/PyFloT/ **

```
source ./environ.source
make
```

## New instructions, complementary from README.md:

```
chmod u+x ${PYFLOT_ROOTDIR}/public/scripts/MultiStepSiteSearch.py
chmod u+x ${PYFLOT_ROOTDIR}/public/scripts/script.py
```

### To execute the analysis on PeleC PMF1D:

* Install peleC in a directory outsite of pyflot, following instructions: https://github.com/hbrunie/PeleC
* Read carefully this instructions, some lines must be updated

```
cd ${PYFLOT_ROOTDIR}/reproducibility
export PMF_DIRECTORY=/path/to/PeleC/Exec/RegTests/PMF/ ## Update this path
cp GNUMakefile-pyflot ${PMF_DIRECTORY}/GNUmakefile
cp default-pyflot-profiling.config ${PMF_DIRECTORY}/
cp default-pyflot-analyzing.config ${PMF_DIRECTORY}/
cd ${PMF_DIRECTORY}
make -j 32
export PMF_BINARY_BASENAME=./Pele1d.xxx,yyy.ex #xxx and yyy are respectively compiler, and architecture used: my case gnu and haswell
pyflot-profiling -c ./default-pyflot-profiling.config
```

You should obtain something similar to:
```
[...]
Ending run at 20:52:02 UTC on 2020-07-22.
Run time = 5.278572263
Run time w/o init = 4.986587073
AMReX (20.07-26-gde150caec585) finalized
Application profiled
```

* Copy/paste `AMReX (20.07-26-gde150caec585) finalized` (or the equivalent you obtained) inside the file default-pyflot-analyzing.config, at line 8
in place of `AMReX (93fb085d2834) finalized`.
    * This is the text used by **PyFloT** to know if the execution ran correctly.
    * The astute user would have noted that this does not garantee the correctness of final results: for this one must compare the flame speed using PeleLM scripts.
* Execute `pyflot-analyzing  -c ./default-pyflot-analyzing.config`

You should obtain this in the stdout:

```
nbTrials ratioSlocSP ratioBtSP ratioDynSP dynCallsSP slocCallSiteSP btCallSiteSP totalDynCalls totalSlocCallSites totalBtCallSites
0 0 0 0 0 0 0 0 0 0
strategy SLOC
Running BFS sloc
1 73.64
2 73.64
3 73.64
4 73.64
5 73.64
6 73.64
7 73.64
8 99.97
Can be converted to single precision: 
SLOC
[0, 1, 2, 4, 5, 6]
BT
[]
Must remain in double precision: (BT)
[3]
```
If not, open an issue on github, or send me an email: [email link](hbrunie@lbl.gov).
