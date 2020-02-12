cp make.Cori.def make.def
make
Link with our dynamic library ./public/lib/PrecisionTuning.so

or you can also
replace math.h by ./public/include/PT_math.h
if for example intercepting at runtime is not possible (because of function renaming in INTEL compiler case for example).

Usefull environment variable:
PRECISION\_TUNER\_OUTPUT\_DIRECTORY --> to choose where profiling files should be dumped.

Use python script in ./public/scripts/script.py for automatic optimization
