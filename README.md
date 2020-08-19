# Precision Tuning tool: PyFloT v0.1
![](https://zenodo.org/badge/211203973.svg)

## Abstract
The goal of this tool is to help finding a mixed precision solution
to reduce execution time while maintaining a certain notion of correctness.
We consider that the program to study is using floating point variables,
all in double precision.

The user must first profile the program to find the hotspots.
Then, there are 2 possibilities.
Either the user applies our tool's link time interposition function (based on [GOTCHA](https://github.com/LLNL/GOTCHA))
to catch at runtime the hotspots routines that are called through a shared dynamic library.
Either the user instruments corresponding code regions of the hotspots, and replace targeted calls by our library calls.
Finally, once compiled and linked with our tool, the instrumented program is executed.
Note that, in theory, the input data should not change between the profiling and the application of our tool;
but in practice we found that our tools solution stays correct on several input data.

The tool will execute the program several times.
In the end, for each static **math function** calls of the instrumented code regions, the tool will provide a temporal scope on which its precision can be reduced.

This work will be presented at the International Conference for High Performance Computing, Networking, Storage and Analysis (SC'20) in November 2020.

## Installation Instructions
### Requirements
* Linux system
* Makefile build system
* CMake
* GOTCHA and Jsoncpp (git submodule update --init --recursive)
* Update the file `environ.source`
* Execute command: source environ.source
### Installation
After setting up the requirements, you can install PyFloT by

```
make
```

### Reproducing our results
Follow instructions in `reproducibility/instructions.md`
