Precision Tuning tool
===========
Abstract
--------
The goal of this tool is to help finding a mixed precision solution
to reduce execution time while maintaining some notion of correctness.
We consider that the program to study is using floating point variables,
all in double precision.

First the user should profile the program to find hotspots.
Then, there are 2 possibilities. Either one uses the link time interposition feature of our tool 
to catch at runtime the hotspots routines which are called through a dynamic shared library.
Or one can instrument the hotspot corresponding code regions, and replace targetted calls by our library calls.
Finally, once compiled and linked with our tool, the instrumented program should be run.
Note that, in theory, the input data should not change between the profiling and the application of our tool;
but in practice we found that our tools solution stays correct on several input data (validate on PeleC/PMF1D, PeleC/PMF2D and
CCTBX/simtbx/nanoBraggSpotsCUDAkernel)

The tool will execute the program several times.
In the end, for each static **math function** calls of the instrumented code regions, the tool will provide a temporal scope on which its precision can be reduced.
Work in progress: extension to any hotspots function, other than just libm math functions.

**How does it work?**

*Definition and assumption:*
* A strategy consists in reducing to single precision some of the selected dynamic calls.
These are identifiable with 2 different granularities: SLOC (Source code LOCation) and BT (backtrace full call stack).
* A chosen new strategy is considered **valid** if, when running the program with the chosen new strategy, the results obtained respect user-defined accuracy requirements, compared to the original strategy.
User as the possiblity to look for a specific string in the output of its program. work in progress: gives his own script to be launched by PyFloT.


*Finding a good strategy:*

* Apply MultiStepSearch Heuristic

**Application Source Code Refactoring**
Modifications for solutions that include SLOC sites are trivial, due
to our decision to lower all events associated with a site. The
decisions to lower sites associated with particular backtraces are
more complex and application specific.
We do not provide compiler support, thus there is no automated procedure
(i.e. precisely identify interprocedural loops and/or branches)
Here is a basic guidance to determine the minimal number of code changes.
There are two guiding principles: 1) minimize the number of
changes; and 2) minimize the number of branches introduced
and in particular avoid fine grained per call branches.

Consider the call graph presented in Figure![Image description](./images/picture1.pdf), 
where the paths ACDFG (green) and ABDEG (orange) lead to the leaf G that can be
executed in single precision. When the program takes the path ABDFG
(purple), G needs to be executed in double precision. In this example
the path describes the backtrace. The minimal number of modifications
is given by taking the set union of the backtraces that lead to
executing G in low precision, followed by its difference to the
union of backtraces that execute G in high precision, e.g
{\footnotesize $(\{A,C,D,F,G\}
  \cup \{A,B,D,E,G\}) \setminus \{A,B,D,F,G\} = \{C,E\}$}.
The best starting point for refactoring is examining the set of
functions ${C,E}$. There are multiple strategies available, depending
on the
identification of  loop and branch structures in the code and user
software engineering and maintenance concerns. One possible strategy
is cloning nodes across the path, as illustrated in
Figure~\ref{fig:bt}(B). Another strategy is marking the path and
adding control divergence checks in dominator nodes for paths that
share function calls. This is illustrated in Figure~\ref{fig:bt}(C),
where we mark the execution of C and decide to specialize F.
