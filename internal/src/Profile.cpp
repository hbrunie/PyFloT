#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>

#include <execinfo.h>
#include <json/json.h>

#include "Debug.hpp"
#include "Profile.hpp"
//#include "DynFuncCall.hpp"    
using namespace std;
using namespace Json;

const string Profile::JSON_TOTALCALLSTACKS_KEY   = "TotalCallStacks";
const string Profile::JSON_TOTALDYNCOUNT_KEY     = "CallsCount";
//TODO: Factorize with Strategy
const string Profile::JSON_MAIN_LIST             = "IndependantCallStacks";
const string Profile::JSON_HASHKEY_KEY           = "HashKey";

Profile::Profile(){
}

Profile::Profile(bool profiling, string ReadOrDumpProfileName){
    __profiling = profiling;
    if(profiling)
        __dumpJsonProfilingFile = ReadOrDumpProfileName;
    else{
        __buildProfiledDataFromJsonFile(ReadOrDumpProfileName);
    }
}

void Profile::updateHashMap(DynFuncCall& dfc){
    // if this hashKey is never seen before, record it.
    uint64_t hashKey = dfc.getHashKey();
    DEBUG("info",cerr << "LOOKING FOR HASH: "<< hashKey << __FUNCTION__ <<endl;);
    __totalDynCount++;
    unordered_map<uint64_t, DynFuncCall>::iterator hashKeyIte = __backtraceDynamicMap.find(hashKey);
    if(hashKeyIte == __backtraceDynamicMap.end()) {
        __backtraceDynamicMap[hashKey] = dfc;
        __totalCallStacks += 1;
    }else{ // Count the number of calls to this callstack
        __backtraceDynamicMap[hashKey].called(dfc);
    }

    DEBUG("info",cerr << "ENDING " << __FUNCTION__ <<endl;);
}

unsigned long Profile::getCurrentDynCount() const{
    return __currentDynCount;
}

void Profile::dumpJson(){
    __dumpJson(__backtraceDynamicMap);
}

void Profile::__displayBacktraceDynMap(){
    for (auto it = __backtraceDynamicMap.begin(); it != __backtraceDynamicMap.end(); it++){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        cerr << value << endl;
    }
}

void Profile::__dumpJson(unordered_map<uint64_t, DynFuncCall> &hashMap){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    bool useCout = true;
    ofstream fb;
    fb.open(__dumpJsonProfilingFile,ios::out);
    if(!fb.is_open()){
        cerr << "Profile: Wrong jsonfile abspath: " 
            << __dumpJsonProfilingFile << endl 
            << "Dumping on stdout " << endl;
    }else
        useCout = false;

    Value jsonDictionary;
    Value jsonDynFuncCallsList;
    Value jsonTotalCallStacks = (UInt)__totalCallStacks;
    jsonDictionary[JSON_TOTALCALLSTACKS_KEY] = jsonTotalCallStacks;
    for (auto it = hashMap.begin(); it != hashMap.end(); ++it){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        Value hashkey((UInt)key);
        Value jsonDynFuncCall = value.getJsonValue();
        jsonDynFuncCall[JSON_HASHKEY_KEY] = hashkey; 
        jsonDynFuncCallsList.append(jsonDynFuncCall);
    }
    jsonDictionary[JSON_MAIN_LIST] = jsonDynFuncCallsList;
    DEBUG("infoplus",cerr << __FUNCTION__ << jsonDictionary<< endl;);
    DEBUG("infoplus",cerr << __FUNCTION__ << useCout << __dumpJsonProfilingFile << endl;);
    if (useCout)
        cout <<jsonDictionary << endl; 
    else{
        fb << jsonDictionary << endl;; 
    }
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    //TODO: find proper C++ way to do this fopen with defaut == cout
    // close the file
}

static bool stream_check(ifstream& s){
    if(s.bad() || s.fail()){
        cerr << "Bad or failed "<< endl;
    }
    if(s.good() && s.is_open())
        return true;
    return false;
}

void Profile::__buildProfiledDataFromJsonFile(string fileAbsPath){
    /*TODO: Find a different name for callStack the object
      containing number of calls, its call stack addresses and lowered count.
      Because it is the name as the call stack, which is the list of virtual addresses.
      Can not be Dynamic Function call. It is in between DynFuncCall and Static function call site.
      Maybe Dynamic Function Call Site? Containing ASVR dependent and ASVR independent.
     */
    //unordered_map<uint64_t, struct CallData> backtraceMap;
    DEBUG("info",cerr << "STARTING __build_callstacks_map_from_json_file" << endl;);
    std::ifstream infile(fileAbsPath, std::ifstream::binary);
    if(!stream_check(infile))
        exit(-1);
    Value jsonDictionary;
    infile >>  jsonDictionary;
    DEBUG("info",cerr << "READING JSON __build_callstacks_map_from_json_file" << endl;);
    DEBUG("infoplus",cerr << jsonDictionary << endl;);


    __totalCallStacks = jsonDictionary[JSON_TOTALCALLSTACKS_KEY].asUInt64();
    __totalDynCount = jsonDictionary[JSON_TOTALDYNCOUNT_KEY].asUInt64();
    Value callStacksList = jsonDictionary[JSON_MAIN_LIST];
    /* Fill the backtraceMap with JSON values */
    cerr << callStacksList.size() << endl;
    for(unsigned int callStackIndex = 0; callStackIndex < callStacksList.size(); callStackIndex++){
        // Get the callStack dictionary
        Value callStack = callStacksList[callStackIndex];
        Value hashKey = callStack[JSON_HASHKEY_KEY];
        DynFuncCall data(callStack, hashKey);
        // TODO: factorize this and the same code in DynFuncCall constructor
        // into JsonUtils.cpp
        uint64_t UIntHashKey;
        string s = hashKey.asString();
        istringstream iss(s);
        iss >> hex >> UIntHashKey;
        __backtraceDynamicMap[UIntHashKey] = data;
    }
    DEBUG("infoplus",cerr << "DISPLAY __build_callstacks_map_from_json_file" << endl;);
    DEBUG("infoplus",__displayBacktraceDynMap(););
    DEBUG("info",cerr << "ENDING __build_callstacks_map_from_json_file" << endl;);
}
