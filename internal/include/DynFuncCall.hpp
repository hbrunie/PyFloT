#ifndef DynFuncCall_H
#define DynFuncCall_H

#include <iostream>
#include <list>
#include <string>
#include <unordered_map>
#include <vector>

#include <json/json.h>

using namespace std;
using namespace Json;

struct FloatSet{
    float low;
    float high;
};

class DynFuncCall
{
    private:
        // Dynamic calls total count
        static const string JSON_CALLSCOUNT_KEY;
        // List of Hexadecimal virtual addresses
        static const string JSON_CALLSTACK_ADDR_LIST_KEY;
        // LOWERED Dynamic calls count
        static const string JSON_INREGION0_KEY;
        static const string JSON_INREGION1_KEY;
        static const string JSON_INREGION2_KEY;
        static const string JSON_LOWERCOUNT_KEY;
        static const string JSON_LOWERBOUND_KEY;
        static const string JSON_UPPERBOUND_KEY;
        vector<void*> __btVec;
        vector<void*> __staticBtVec;
        bool __inRegionBool0;
        unsigned long __inRegion0;
        bool __inRegionBool1;
        unsigned long __inRegion1;
        bool __inRegionBool2;
        unsigned long __inRegion2;
        unsigned long __loweredCount;
        unsigned int __lowerBound;
        unsigned int __upperBound;
        unsigned long __dyncount;
        unsigned long __profiledDyncount;
        uintptr_t __dynHashKey;
        string __statHashKey;
        list<struct FloatSet> __stratMultiSet;
    public:
        DynFuncCall();
        // static: called in __buildProfiledDataFromJsonFile
        DynFuncCall(Value, string);
        //
        DynFuncCall(vector<void*>);
        // dynamic HashKey, used in applyProfiling
        DynFuncCall(vector<void*>, uintptr_t);
        // static
        DynFuncCall(vector<void*>, string);
        // static
        DynFuncCall(vector<void*>, string, bool);
        DynFuncCall(vector<void*>, uint32_t);
        DynFuncCall(vector<void*>, uint32_t, bool);
        Value getJsonValue();
        vector<void*> getBtVector();
        bool applyStrategy();
        void applyProfiling();
        void dumpStack();
        friend ostream& operator<<(ostream& os, const DynFuncCall& cd);
};
#endif // DynFuncCall_H
