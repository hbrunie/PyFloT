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
        static const string JSON_LOWERCOUNT_KEY;
        vector<void*> __btVec;
        vector<void*> __staticBtVec;
        unsigned long __loweredCount;
        unsigned long __dyncount;
        unsigned long __profiledDyncount;
        uint64_t __dynHashKey;
        string __statHashKey;
        list<struct FloatSet> __stratMultiSet;
    public:
        DynFuncCall();
        // static: called in __buildProfiledDataFromJsonFile
        DynFuncCall(Value, string);
        //
        DynFuncCall(vector<void*>);
        // dynamic HashKey, used in applyProfiling
        DynFuncCall(vector<void*>, uint64_t);
        // static
        DynFuncCall(vector<void*>, string);
        // static
        DynFuncCall(vector<void*>, string, bool);
        DynFuncCall(vector<void*>, unsigned long); 
        DynFuncCall(vector<void*>, unsigned long, bool);
        Value getJsonValue();
        vector<void*> getBtVector();
        bool applyStrategy();
        void applyProfiling();
        void dumpStack();
        friend ostream& operator<<(ostream& os, const DynFuncCall& cd);
};
#endif // DynFuncCall_H
