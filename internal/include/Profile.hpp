#ifndef Profile_H
#define Profile_H
#include "DynFuncCall.hpp"

using namespace std;
using namespace Json;

class Profile{
    private: 
        // Function return addresses, sensible to
        // LINUX Address space layout randomization (ASLR)
        // Obtained with **backtrace** function from execinfo.h (or unwind)
        unordered_map<uint64_t, DynFuncCall> __backtraceDynamicMap;
        // Obtain with **backtrace_symbols**, link to static addresses in binary
        // Does not depend on ASLR
        // Slower to fill: backtrace costs less than backtrace_symbols
        unordered_map<uint64_t, DynFuncCall> __backtraceStaticMap;
        unsigned long __totalDynCount = 0;
        unsigned long __currentDynCount = 0;
        string __dumpJsonProfilingFile;
        bool __profiling;
        Value __profileJsonDictionary;
        unsigned long __totalCallStacks = 0;

        /// PRIVATE Functions
        //TODO: factorize this in our own HashMap object implementing JSon stuff
        void __dumpJson(unordered_map<uint64_t, DynFuncCall> &hashMap);
        void __buildProfiledDataFromJsonFile(string fileAbsPath);
        void __displayBacktraceDynMap();

        /// JSON Keys
        // List of all the call stack dictionnaries
        static const string JSON_MAIN_LIST;
        /* Inside each independant call stack dictionnary */
        // Dynamic calls total count
        static const string JSON_TOTALDYNCOUNT_KEY;
        // LOWERED Dynamic calls count
        static const string JSON_TOTALCALLSTACKS_KEY;
        static const string JSON_HASHKEY_KEY;

    public:
        Profile();
        Profile(bool, string);
        void updateHashMap(DynFuncCall &);
        unsigned long getCurrentDynCount()const;
        void dumpJson();
};
#endif //Profile_H
