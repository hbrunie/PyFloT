#ifndef Profile_H
#define Profile_H
#include <unordered_map>
#include <string>
#include <iostream>
#include <vector>

#include <json/json.h>
#include "DynFuncCall.hpp"

using namespace std;
using namespace Json;

class Profile{
    private: 
        // List of all the call stack dictionnaries
        static const string JSON_MAIN_LIST;
        static const string JSON_TOTALCALLSTACKS_KEY;
        static const string JSON_HASHKEY_KEY;

        unordered_map<uint64_t, DynFuncCall> __backtraceStaticMap;
        unsigned long __totalLoweredCount = 0;
        unsigned long __totalDynCount = 0;
        unsigned long __currentDynCallCount = 0;
        Value __profileJsonDictionary;
        unsigned long __totalCallStacks = 0;
        void __dumpHashMapJson(ostream &os, unordered_map<uint64_t, DynFuncCall> &hashMap);
        void __buildProfiledDataFromJsonFile(string);
    public:
        Profile();
        Profile(string);
        void dumpJson();
};
#endif //Profile_H
