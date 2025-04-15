# Precision Tuning tool: PyFloT v0.1
![](https://zenodo.org/badge/211203973.svg)

## Abstract
The goal of this tool is to help finding a mixed precision solution
to reduce execution time while maintaining a certain notion of correctness.
We consider that the program to study is using floating point variables,
all in double precision.

The user must first profile the program to find the hotspots.
Then, there are 2 possibilities:
* Either the user applies our tool's link time interposition function (based on [GOTCHA](https://github.com/LLNL/GOTCHA))
to catch at runtime the hotspots routines that are called through a shared dynamic library.
* or the user instruments corresponding code regions of the hotspots, and replace targeted calls by our library calls.

Finally, once compiled and linked with PyFloT, the instrumented program is executed.
PyFloT will execute the program several times.
In the end, for each static *math function* calls of the instrumented code regions, the tool will provide a *temporal scope* on which the function floating point precision can be reduced.

Note that, in theory, the input data used for profiling the application with PyFloT should be the same as the input data used to execute
the transformed program.
Nevertheless, in practice we found that PyFloT suggested floating point reduced precision transformation stays correct on several input data.


This work was presented at the International Conference for High Performance Computing, Networking, Storage and Analysis (SC'20) in November 2020.

## Installation Instructions

### Requirements
* Makefile >= 4.3
* CMake >= 3.13
* GOTCHA and Jsoncpp (git submodule update --init --recursive)
    * add `set(CMAKE_POSITION_INDEPENDENT_CODE ON)` to Json CMakeLists.txt.
    * TODO: move PyFloT dependence to a header-only Json lib.
### Installation
* Update the file `environ.source`
* Execute commands: 
```bash
python3 -m venv venv
source venv/bin/activate
source environ.source
mkdir build
cd build
cmake ..
make
```
### Usage
Details in [usage markdown file](./USAGE.md)

### Reproducing our results
Follow instructions in `reproducibility/instructions.md`
