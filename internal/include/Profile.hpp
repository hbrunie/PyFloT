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
        string __dumpFile;
        Value __profileJsonDictionary;
        unsigned long __totalCallStacks = 0;

        /// PRIVATE Functions
        //TODO: factorize this in our own HashMap object implementing JSon stuff
        void __buildProfiledDataFromJsonFile(string fileAbsPath);
        void __dumpJsonPermanentHashMap();
        void __displayBacktraceDynMap();
        void __displayBacktraceStaticMap();
        uint64_t __hashKey(vector<void*> btVec);
        uint64_t __staticHashKey(vector<void*> btVec);
        void __updateHashMap(DynFuncCall& dfc, uint64_t hashKey);
        void    __buildStaticBacktraceMap();

        /// JSON Keys
        // List of all the call stack dictionnaries
        static const string JSON_MAIN_LIST;
        /* Inside each independant call stack dictionnary */
        // Dynamic calls total count
        static const string JSON_TOTALDYNCOUNT_KEY;
        // LOWERED Dynamic calls count
        static const string JSON_TOTALCALLSTACKS_KEY;
        static const string JSON_HASHKEY_KEY;
        bool singlePrecision(vector<void*> & btVec);
        void updateHashMap(DynFuncCall &);

    public:
        Profile();
        Profile(bool, string, string);
        bool applyStrategy(vector<void*> & btVec);
        void applyProfiling(vector<void*> & btVec);
        void dumpJson();
};
#endif //Profile_H
