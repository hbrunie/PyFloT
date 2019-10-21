cp make.Cori.def make.def
make
replace math.h by ./public/include/PT_math.h
Link with our dynamic library ./public/lib/PrecisionTuning.so
Use python script in ./public/scripts/script.py for automatic optimization
