#include <unordered_map>
#include <string>
#include <iostream>
#include <vector>

#include "DynFuncCall.hpp"
#include "Strategy.hpp"
#include "Profile.hpp"
using namespace std;

//#define CHECK_NULL(X) 				\
//  do {if(NULL == (X)) {cerr << ": NULL" << endl; } \
//  } while (0)
#define CHECK_NULL(X, Y, Z) 				\
  do {if(NULL == (X)) {cerr << "Error: " << Y << " == NULL" << endl; Z = false;} \
  } while (0)

enum MODE{PROFILING, APPLYING_STRAT};

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
        Strategy __strategy;
        enum MODE __mode;
        unsigned long __totalLoweredCount = 0;
        unsigned long __totalDynCount = 0;
        unsigned long __currentDynCallCount = 0;
        Value __profileJsonDictionary;
        unsigned long __totalCallStacks = 0;
        /* Profiling */
        Profile __profile;
        char * __jsonFileFromProfiling;

        void __display();
        void __dumpJson(ostream&, Value&);
        void __dumpStratResultsJson(const char *);
        //TODO: factorize this in our own HashMap object implementing JSon stuff
        void __dumpHashMapJson(ostream &os, unordered_map<uint64_t, DynFuncCall> &hashMap);
        //void __dumpProfileJson(const char *);
        double __overloading_function(string s, float fres, double dres, double value);
        void __dump_stack(uint64_t key);
        void __buildProfiledDataFromJsonFile(string fileAbsPath);
        void __buildStrategyFromJsonFile(string fileAbsPath);
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
        static const string DUMP_JSON_PROFILING_FILE;
        static const string DUMP_JSON_STRATSRESULTS_FILE;
        static const string READ_JSON_PROFILING_FILE;
        static const string READ_JSON_STRAT_FILE;

    public:
        PrecisionTuner();
        ~PrecisionTuner();
        uint64_t get_context_hash_backtrace(bool lowered);
        double overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
                double value, double parameter);
        double overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value);
};
