#ifndef Profile_H
#define Profile_H

#include "DynFuncCall.hpp"

using namespace std;
using namespace Json;

class Profile{
    private: 
        bool __mode;
        // Function return addresses, sensible to
        // LINUX Address space layout randomization (ASLR)
        // Obtained with **backtrace** function from execinfo.h (or unwind)
        unordered_map<uintptr_t, shared_ptr<DynFuncCall>> __backtraceDynamicMap;
        // Obtain with **backtrace_symbols**, link to static addresses in binary
        // Does not depend on ASLR
        // Slower to fill: backtrace costs less than backtrace_symbols
        map<string, shared_ptr<DynFuncCall>> __backtraceStaticMap;
        unsigned long __totalDynCount = 0;
        unsigned long __currentDynCount = 0;
        Value __profileJsonDictionary;
        unsigned long __totalCallStacks = 0;

        /// PRIVATE Functions
        //TODO: factorize this in our own HashMap object implementing JSon stuff
        void __buildProfiledDataFromJsonFile();
        void __dumpCSVdynamicCalls();
        void __dumpJsonPermanentHashMap(bool);
        // 2 following are calling previous one
        void __dumpReducedJsonPermanentHashMap();
        void __dumpFullJsonPermanentHashMap();
        // Debug functions
        void __displayBacktraceDynMap();
        void __displayBacktraceStaticMap();
        // TODO
        uintptr_t __dynHashKey(vector<void*> btVec);
        string __staticHashKey(vector<void*> btVec);
        // JSON FILE ENV VARS
        static const string DUMP_JSON_STRATSRESULTS_FILE;
        static const string READ_JSON_PROFILE_STRAT_FILE;
        static const string DUMP_JSON_PROFILING_FILE;
        static const string DUMP_CSV_PROFILING_FILE;

        static const string BACKTRACE_LIST;
        static const string DEFAULT_BACKTRACE_LIST;

        static const string DEFAULT_READ_JSON_STRAT_FILE;
        static const string DEFAULT_DUMP_JSON_PROF_FILE;
        static const string DEFAULT_DUMP_CSV_PROF_FILE;
        static const string DEFAULT_DUMP_JSON_STRATRESULT_FILE;
        /// JSON Keys
        // List of all the call stack dictionnaries
        static const string JSON_MAIN_LIST;
        /* Inside each independant call stack dictionnary */
        // Dynamic calls total count
        static const string JSON_TOTALDYNCOUNT_KEY;
        // LOWERED Dynamic calls count
        static const string JSON_TOTALCALLSTACKS_KEY;
        static const string JSON_HASHKEY_KEY;
        static const string JSON_CSV_FILENAME;
        bool singlePrecision(vector<void*> & btVec, string label);
        void updateHashMap(DynFuncCall &);
        void writeBacktraceKeyFile(string);
    public:
        //Profile();
        ~Profile();
        Profile(bool);
        bool applyStrategy(vector<void*> & btVec, string label);
        void applyProfiling(vector<void*> & btVec, string label, ShadowValue &sv);
        void dumpJson();
        void dumpJsonPlusCSV();
};
#endif //Profile_H
