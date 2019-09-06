#include <unordered_map>
#include <string>
#include <iostream>
#include <vector>

#include "DynFuncCall.hpp"
using namespace std;
class PrecisionTuner
{
    private:
        // Function return addresses, sensible to
        // LINUX Address space layout randomization (ASLR)
        // Obtained with **backtrace** function from execinfo.h (or unwind)
        unordered_map<uint64_t, DynFuncCall> __backtraceDynamicMap;
        // Obtain with **backtrace_symbols**, link to static addresses in binary
        // Does not depend on ASLR
        // Slower to fill: backtrace costs less than backtrace_symbols
        unordered_map<uint64_t, DynFuncCall> __backtraceStaticMap;
        unsigned long __totalLoweredCount = 0;
        unsigned long __totalDynCount = 0;
        unsigned long __minbound = 0;
        unsigned long __maxbound = 0;
        unsigned long __totalCallStacks = 0;
        /* Profiling */
        bool __profiling;
        char * __jsonFileFromProfiling;

        void __display();
        void __dump_json();
        double __overloading_function(string s, float fres, double dres, double value);
        void __dump_stack(uint64_t key);
        unordered_map<uint64_t, DynFuncCall> __buildAllDataFromJsonFile(string fileAbsPath);
        void __buildCallStacksMap();
        void __displayBacktraceDynMap();
        //ostream *__check();

        static const unsigned int MAXSTACKSIZE;
        /* JSON values and sections keys */
        // Number of independant call stacks
        static const string JSON_TOTALCALLSTACKS_KEY;
        // List of all the call stack dictionnaries
        static const string JSON_MAIN_LIST;
        /* Inside each independant call stack dictionnary */
        // Dynamic calls total count
        static const string JSON_TOTALDYNCOUNT_KEY;
        // LOWERED Dynamic calls count
        static const string JSON_TOTALLOWEREDCOUNT_KEY;
        static const string JSON_HASHKEY_KEY;
        // JSON FILE ENV VARS
        static const string DUMP_JSON_FILE;
        static const string READ_JSON_FILE;
        static const string DEFAULT_READ_JSON_FILE;

    public:
        PrecisionTuner();
        ~PrecisionTuner();
        uint64_t get_context_hash_backtrace(bool lowered);
        double overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
                double value, double parameter);
        double overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value);
};
