Precision Tuning tool
===========
Abstract
--------
The goal of this tool is to help finding a mixed precision solution
to reduce execution time while maintaining some notion of correctness.
We consider that the program to study is using floating point variables,
all in double precision.

First the user should profile the program to find hotspots.
Then, hotspot corresponding code regions should be instrumented with tool.
Finally, once compiled and linked with our tool, the instrumented program should be run.
Note that the input data should not change between the profiling and the application of our tool.

The tool will execute the program several times.
In the end, for each static **math function** calls of the instrumented code regions, the tool will provide a temporal scope on which its precision can be reduced.

**How does it work?**

*Definition and assumption:*
* A strategy consists in reducing to single precision some of the selected dynamic calls. Note that we make the difference between the static call sites and the dynamic calls.

* A chosen new strategy is considered **valid** if, when running the program with the chosen new strategy, the results obtained respect user-defined accuracy requirements, compared to the original strategy.
* A temporal scope corresponds to a set, not necessarily contiguous, of dynamic calls to a **math function** static call site.
* 3 possibilities for defining a dynamic call
    1. Using counter
	* A dynamic call is defined by the value of a static counter which is uniquely assigned to that function call site.
	* Assumption is made that  for a given call site, the dynamic calls to that function are always executed in the same order between different execution of the program with the same input data.
    2. Using hash function
	* A dynamic call is defined by the value of a dynamic hash. This hash may be computed using different parameters.
	As it is not clear yet what are the parameters that allows to differentiante the sensitivity towards reduced precision, we
	should build it modular.
	* For example, it could be computed based on the callstack and the log2 of the input data of the math function.
	* Note, building a complex hash function will have an impact on performance.
	* Note, the has could be the same for a set of
    1. Exact definition: its use is purely theoric. If the program is executed twice on same input data, with same software environment (number of threads, ...), a dynamic call is uniquely identifiable with the **exact definition**.
	This hypothetic **exact definition** may be obtained by hashing the input function parameter with the right accuracy (too many digits could make thinks that its not the same call, whereas it could be just due to some randomness in its computation, like threads ordering), adding to it the hash of the callstack, plus the value of all the outer loop iterators.



*Finding a good strategy:*

* Apply Delta debugging algorithm to the set made of all dynamic calls.


*Delta Debugging algorithm:*

- Divide initial into two subsets
- For each subset:
    - Run program with all dynamic calls from that subset in single precision
    - IF this is a valid strategy
	- keep these dynamic calls in single precision for the solution strategy;
    - ELSE
	- divide the subset into two subsets, and continue recursively

**Instrumentation details**

* Implementation **A**
    * Easy to use, user has only to replace ```#include <math.h>``` by ```#include "mathPrecisionTuning.h"``` and to instrument the code regions corresponding to the runtime hotspots.
    * Drawbacks: the conditional branch implementation is located inside the math function call, thus breaking lots of compiler optimizations. Overhead due to that may be significant, and makes the tool useless, because it would not be able to improve the performance by reducing the precision.

* Implementation **B**
    * Instrumenting with the branching statement higher in the Control Flow graph, would reduce the overhead by allowing more compiler optimizations, but it would be harder to automatize, and it would agglomerate dynamic calls with maybe very different parameters value into one decision locality.

* In both implementation the wrapper would be a python script allowing to launch the program several times and parsing the output to compare them, while executing the Delta Debugging algorithm by modifying some environment variables, or config file read by our tool.

**More details**

* Inside mathPrecisionTuning.cpp:
    - Code for all __precisionTuning_[mathfunction]
	- call to the actual [mathfunction] with chosen precision
	- chosen precision depends on the if stmt


* Inside ```mathPrecisionTuning.h```
    - #include<math.h>
    - #define exp __precisionTuning_exp
    - ... for every math functions
    - #include "mathPrecisionTuning.cpp"


**Other thoughts**

- we have made the choice to do the branching between double and single precision
    at runtime. It could impact the performance. Could it be move to compile time?
    How many binary do we want to generate?
