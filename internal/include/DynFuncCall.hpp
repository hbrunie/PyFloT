#ifndef DynFuncCall_H
#define DynFuncCall_H
#include <unordered_map>
#include <string>
#include <iostream>
#include <vector>

#include <json/json.h>

using namespace std;
using namespace Json;
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
    public:
        DynFuncCall();
        DynFuncCall(Value, Value);
        DynFuncCall(const DynFuncCall &);
        DynFuncCall(vector<void*>, bool);
        DynFuncCall(vector<void*> btVec, unsigned long dyncount, unsigned long loweredCount);
        void called(bool);
        Value getJsonValue();
        void dumpStack();
        friend ostream& operator<<(ostream& os, const DynFuncCall& cd);
};
#endif // DynFuncCall_H