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

const string Profile::JSON_TOTALCALLSTACKS_KEY  = "TotalCallStacks";
const string Profile::JSON_TOTALDYNCOUNT_KEY    = "CallsCount";
const string Profile::JSON_MAIN_LIST            = "IndependantCallStacks";
const string Profile::JSON_HASHKEY_KEY          = "HashKey";

Profile::Profile(){
}

Profile::Profile(bool profiling, string readFile,
        string dumpFile){
        DEBUG("apply",cerr << __FUNCTION__ << " --> dumpFile: " << dumpFile << " profiling: " << profiling << endl;);
    if(profiling){
        __dumpFile = dumpFile;
    }
    else{
        __buildProfiledDataFromJsonFile(readFile);
        __dumpFile = dumpFile;
    }
}

string Profile::__staticHashKey(vector<void*> btVec){
    string statHashKey;
    string tmpHash;
    uint64_t size = btVec.size();
    void ** btpointer = &btVec[0];
    char ** symbols = backtrace_symbols(btpointer, size);
    unsigned int cnt = 0;
    char * tmp = symbols[cnt];
    while(NULL != tmp && cnt < size){
        string stmp(tmp);
        std::vector<std::string> result;
        std::istringstream iss(stmp);
        for(std::string s; iss >> s; ){
            DEBUG("key",cerr <<s << endl;);
            result.push_back(s);
        }
        DEBUG("keyplus",cerr << __FUNCTION__ << ":" << __LINE__
            << "size: "<< result.size() << endl;);
        DEBUG("key",cerr <<endl << result[3] << result[5] << endl;);
        statHashKey += result[3];
        statHashKey += result[5];
        cnt++;
        tmp = symbols[cnt];
    }
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__ 
            << " staticHashKey: " << statHashKey << endl;);
    return statHashKey;
}

uint64_t Profile::__dynHashKey(vector<void*> btVec){
    uint64_t dynHashKey;
    for(auto it = btVec.begin(); it != btVec.end(); it++){
        void *ip = *it;
        assert(NULL != ip);
        dynHashKey += (uint64_t) ip;
        assert( (dynHashKey+ (uint64_t) ip) < numeric_limits<uint64_t>::max());
    }
    return dynHashKey;
}

bool Profile::applyStrategy(vector<void*> & btVec){
    //compute hash
    uint64_t dynHashKey = __dynHashKey(btVec);
    DynFuncCall dfc;
    DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__ << " " << dfc << endl);
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__<<  " Static map " << endl;
                __displayBacktraceStaticMap(););
    // if exist or not go on perm HashMap
    auto hashKeyIte = __backtraceDynamicMap.find(dynHashKey);
    if(hashKeyIte == __backtraceDynamicMap.end()){
        string staticHashKey = __staticHashKey(btVec);
        DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " staticHashKey:" << 
               staticHashKey << endl);
        dfc = __backtraceStaticMap[staticHashKey];
        DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
        __backtraceDynamicMap[dynHashKey] = dfc;
    }else{
        dfc = __backtraceDynamicMap[dynHashKey];
        DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
    }
    // Then compare currentDyncount with set
    bool res = dfc.applyStrategy();
    // then update dfc in ASLRDynamicHashMap
    //TODO: remove this buy using pointer to the object in the HashMap
    __backtraceDynamicMap[dynHashKey].updateLowerCount(res);
    __backtraceDynamicMap[dynHashKey].called();
    DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__<< " Dynamic map " << endl;__displayBacktraceDynMap(););

    return res;
}

void Profile::applyProfiling(vector<void*> & btVec){
    //compute hash
    // add or update DynamicHashMap
    uint64_t dynHashKey = __dynHashKey(btVec);
    DynFuncCall dfc(btVec, dynHashKey);
    dfc.called();
    __updateHashMap(dfc, dynHashKey);

}

void Profile::__updateHashMap(DynFuncCall& dfc, uint64_t dynHashKey){
    // if this dynHashKey is never seen before, record it.
    DEBUG("info",cerr << "LOOKING FOR HASH: "<< dynHashKey << __FUNCTION__ <<endl;);
    __totalDynCount++;
    unordered_map<uint64_t, DynFuncCall>::iterator dynHashKeyIte = __backtraceDynamicMap.find(dynHashKey);
    if(dynHashKeyIte == __backtraceDynamicMap.end()) {
        __backtraceDynamicMap[dynHashKey] = dfc;
        __totalCallStacks += 1;
    }
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ <<endl;);
}

void Profile::__buildStaticBacktraceMapFromDynamicOne(){
    DEBUG("key",cerr << __FUNCTION__ <<endl << " Dynamic map " << endl;__displayBacktraceDynMap(););
    DEBUG("key",cerr << __FUNCTION__ <<endl <<" static map " << endl;__displayBacktraceStaticMap(););
    for (auto it = __backtraceDynamicMap.begin(); it != __backtraceDynamicMap.end(); it++){
        uint64_t key = it->first;
        DynFuncCall value = it->second;
        string staticHashKey = __staticHashKey(value.getBtVector());
        auto hashKeyIte = __backtraceStaticMap.find(staticHashKey);
        if(hashKeyIte == __backtraceStaticMap.end()) {
            __backtraceStaticMap[staticHashKey] = value;
        }else{
            cerr << "ERROR: " << __FUNCTION__ << endl;
        }
    }
}

void Profile::dumpJson(){
    __buildStaticBacktraceMapFromDynamicOne();
    __dumpJsonPermanentHashMap();
}

void Profile::__displayBacktraceStaticMap(){
    cerr << __FUNCTION__ << ":" << __LINE__<< endl;
    for (auto it = __backtraceStaticMap.begin(); it != __backtraceStaticMap.end(); it++){
        string key = it->first;
        DynFuncCall value = it->second;
        cerr << value << endl;
    }
}

void Profile::__displayBacktraceDynMap(){
    for (auto it = __backtraceDynamicMap.begin(); it != __backtraceDynamicMap.end(); it++){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        cerr << value << endl;
    }
}

void Profile::__dumpJsonPermanentHashMap(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    bool useCout = true;
    ofstream fb;
    fb.open(__dumpFile,ios::out);
    if(!fb.is_open()){
        cerr << "Profile: Wrong jsonfile abspath: " 
            << __dumpFile << endl 
            << "Dumping on stdout " << endl;
    }else
        useCout = false;

    Value jsonDictionary;
    Value jsonDynFuncCallsList;
    Value jsonTotalCallStacks = (UInt)__totalCallStacks;
    jsonDictionary[JSON_TOTALCALLSTACKS_KEY] = jsonTotalCallStacks;
    for (auto it = __backtraceStaticMap.begin(); it != __backtraceStaticMap.end(); ++it){
        string key = it->first;
        DynFuncCall value = it->second;
        Value statHashKey(key);
        Value jsonDynFuncCall = value.getJsonValue();
        jsonDynFuncCall[JSON_HASHKEY_KEY] = statHashKey; 
        jsonDynFuncCallsList.append(jsonDynFuncCall);
    }
    jsonDictionary[JSON_MAIN_LIST] = jsonDynFuncCallsList;
    DEBUG("infoplus",cerr << __FUNCTION__ << jsonDictionary<< endl;);
    DEBUG("infoplus",cerr << __FUNCTION__ << useCout << __dumpFile << endl;);
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
    DEBUG("info",cerr << "STARTING "<< __FUNCTION__ << endl;);
    std::ifstream infile(fileAbsPath, std::ifstream::binary);
    if(!stream_check(infile))
        exit(-1);
    Value jsonDictionary;
    infile >>  jsonDictionary;
    DEBUG("info",cerr << "READING JSON "<< __FUNCTION__ << endl;);
    DEBUG("infoplus",cerr << jsonDictionary << endl;);

    __totalCallStacks = jsonDictionary[JSON_TOTALCALLSTACKS_KEY].asUInt64();
    __totalDynCount = jsonDictionary[JSON_TOTALDYNCOUNT_KEY].asUInt64();
    Value callStacksList = jsonDictionary[JSON_MAIN_LIST];
    /* Fill the backtraceMap with JSON values */
    for(unsigned int callStackIndex = 0; callStackIndex < callStacksList.size(); callStackIndex++){
        // Get the callStack dictionary
        Value callStack = callStacksList[callStackIndex];
        Value statHashKey = callStack[JSON_HASHKEY_KEY];
        // TODO: factorize this and the same code in DynFuncCall constructor
        // into JsonUtils.cpp
        string sstaticHashKey = statHashKey.asString();
        DynFuncCall data(callStack, sstaticHashKey);
        DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__ << data << endl;);
        __backtraceStaticMap[sstaticHashKey] = data;
    }
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__ << endl;__displayBacktraceStaticMap(););
}
