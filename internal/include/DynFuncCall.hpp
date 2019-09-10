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
        vector<void*> __btSymbolsVec;
        unsigned long __loweredCount;
        unsigned long __dyncount;
        uint64_t __hashKey;
        list<struct FloatSet> __stratMultiSet;
    public:
        DynFuncCall();
        DynFuncCall(const DynFuncCall &);
        DynFuncCall(Value, Value);
        DynFuncCall(Value,uint64_t);
        DynFuncCall(vector<void*> btVec);
        DynFuncCall(vector<void*> btVec, uint64_t key);
        DynFuncCall(vector<void*> btVec, bool lowered);
        DynFuncCall(vector<void*> btVec, uint64_t key, bool lowered);
        DynFuncCall(vector<void*> btVec, unsigned long dyncount, unsigned long loweredCount);
        void called(DynFuncCall &);
        Value getJsonValue();
        uint64_t getHashKey();
        vector<void*> getBtVector();
        unsigned long getLoweredCount();
        bool applyStrategy();
        void updateLowerCount(bool lower);
        void dumpStack();
        friend ostream& operator<<(ostream& os, const DynFuncCall& cd);
};
#endif // DynFuncCall_H
