## Default
* Link with our dynamic library ./public/lib/PrecisionTuning.so
    * using `LD_LIBRARY_PATH` environment variable
* or replace `math.h` with `./public/include/PT_math.h` if intercepting at runtime is not possible, because of function renaming in INTEL compiler case for example.

### Usefull environment variable:

`PRECISION_TUNER_OUTPUT_DIRECTORY`: to chose where profiling files should be dumped.

### Automatic optimization

See `./public/scripts/script.py`

## Executing on laptop

## Executing on CORI supercompute
```bash
cp make.Cori.def make.def
make
```
