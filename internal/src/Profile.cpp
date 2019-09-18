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
// ONE == 4 because of Ptuning internal calls below __overloaded_mathFunction
#define ONE 4
using namespace std;
using namespace Json;

const string Profile::JSON_TOTALCALLSTACKS_KEY  = "TotalCallStacks";
const string Profile::JSON_TOTALDYNCOUNT_KEY    = "CallsCount";
const string Profile::JSON_MAIN_LIST            = "IndependantCallStacks";
const string Profile::JSON_HASHKEY_KEY          = "HashKey";

Profile::~Profile(){
    // delete all DynCallFunc objects: automatic with shared pointers
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

/* the Static Hash Key corresponds to a non ASLR dependent HashKey
 * User can define the level of callstack he wants to use for
 * defining the DynamicCallSite.
 * By default the level is 1: only the __overloaded_mathFunction call is taken into account. 
 */
string Profile::__staticHashKey(vector<void*> btVec){
    string statHashKey;
    string tmpHash;
    // Choosing level: ONE <= size <= btVec.size();
    uint64_t size = ONE;
    void ** btpointer = &btVec[0];
    char ** symbols = backtrace_symbols(btpointer, size);
    unsigned int cnt = 0;
    char * tmp = symbols[cnt];
    while(NULL != tmp && cnt < size){
        string stmp(tmp);
        std::vector<std::string> result;
        std::istringstream iss(stmp);
        DEBUG("statickey",cerr << " result: " ;);
        for(std::string s; iss >> s; ){
            DEBUG("statickey",cerr << s << " " ;);
            result.push_back(s);
        }
        DEBUG("statickey",cerr << endl << __FUNCTION__ << ":" << __LINE__
            << " Result size: "<< result.size() << endl;);
        DEBUG("statickey",cerr << " Elts chosen for static key: " <<endl << result[3]<< " " << result[5] << endl;);
        statHashKey += result[3];
        statHashKey += result[5];
        //If main function call is reached, stop the callstack unstacking.
        if(result[3].compare("main")==0)
            cnt=size;
        cnt++;
        tmp = symbols[cnt];
    }
    DEBUG("statickey",cerr << __FUNCTION__ << ":" << __LINE__ 
            << " staticHashKey: " << statHashKey << endl;);
    return statHashKey;
}

uint64_t Profile::__dynHashKey(vector<void*> btVec){
    uintptr_t dynHashKey = 0;
    uint64_t cnt = 0;
    for(auto it = btVec.begin(); it != btVec.end() && cnt < ONE; it++){
        void *ip = *it;
        assert(NULL != ip);
        assert( (dynHashKey+ (uintptr_t) ip) < numeric_limits<uintptr_t>::max());
        DEBUG("dynHashKey",cerr << __FUNCTION__ << ":" << __LINE__ << dynHashKey
                << " " << cnt << "/" << ONE << " " << (uintptr_t) ip << endl;);
        dynHashKey += (uintptr_t) ip;
        cnt++;
    }
    return dynHashKey;
}

bool Profile::applyStrategy(vector<void*> & btVec){
    //compute hash
    uintptr_t dynHashKey = __dynHashKey(btVec);
    shared_ptr<DynFuncCall> dfc;
    DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__ << " " << dfc << endl);
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__<<  " Static map " << endl;
                __displayBacktraceStaticMap(););
    // if exist or not go on perm HashMap
    auto hashKeyIte = __backtraceDynamicMap.find(dynHashKey);
    if(hashKeyIte == __backtraceDynamicMap.end()){
        string staticHashKey = __staticHashKey(btVec);
        DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " staticHashKey:" << 
               staticHashKey << endl);
        auto stathashKeyIte = __backtraceStaticMap.find(staticHashKey);
        if(stathashKeyIte == __backtraceStaticMap.end()){
            cerr << __FUNCTION__ << ":" << __LINE__ << " ERROR staticHashKey:" << staticHashKey << endl;
            exit(-1);
        }
        dfc = __backtraceStaticMap[staticHashKey];
        DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
        __backtraceDynamicMap[dynHashKey] = dfc;
    }else{
        dfc = __backtraceDynamicMap[dynHashKey];
        DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
    }
    // Then compare currentDyncount with set
    bool res = dfc->applyStrategy();
    DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__<< " Dynamic map " << endl;__displayBacktraceDynMap(););
    return res;
}

/* Compute hash and add or update DynamicHashMap
 */
void Profile::applyProfiling(vector<void*> & btVec){
    uintptr_t dynHashKey = __dynHashKey(btVec);
    shared_ptr<DynFuncCall> dfc(nullptr);
    auto dynHashKeyIte = __backtraceDynamicMap.find(dynHashKey);
    /* Can not find the element in Dynamic Hash Map */
    if(dynHashKeyIte == __backtraceDynamicMap.end()) {
        dfc = make_shared<DynFuncCall>(btVec, dynHashKey);
        __backtraceDynamicMap[dynHashKey] = dfc;
        /* Update Static HashMap */
        string staticHashKey = __staticHashKey(btVec);
        /* The element is necessarily not in StaticHashMap either,
         * Because static and dynamic HashMap are "identical" */
        __backtraceStaticMap[staticHashKey] = dfc;
        __totalCallStacks += 1;
        DEBUG("total",cerr << __FUNCTION__ << ":" << __LINE__<< " Total Call Stack " << __totalCallStacks <<endl;);
    }else{
        // The element is in Dynamic Hash Map
        DEBUG("total",cerr << __FUNCTION__ << ":" << __LINE__<< " Elt already in Dynamic Hash Map " << __totalCallStacks <<endl;);
        dfc = __backtraceDynamicMap[dynHashKey];
    }
    dfc->applyProfiling();
    __totalDynCount++;
}

void Profile::dumpJson(){
    __dumpJsonPermanentHashMap();
}

void Profile::__displayBacktraceStaticMap(){
    DEBUG("info",cerr << __FUNCTION__ << ":" << __LINE__<< endl;);
    for (auto it = __backtraceStaticMap.begin(); it != __backtraceStaticMap.end(); it++){
        string key = it->first;
        shared_ptr<DynFuncCall>value = it->second;
        DEBUG("info",cerr << *value << endl;);
    }
}

void Profile::__displayBacktraceDynMap(){
    DEBUG("info",cerr << __FUNCTION__ << ":" << __LINE__<< endl;);
    for (auto it = __backtraceDynamicMap.begin(); it != __backtraceDynamicMap.end(); it++){
        shared_ptr<DynFuncCall>value = it->second;
        DEBUG("info",cerr << *value << endl;);
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
        shared_ptr<DynFuncCall>value = it->second;
        Value statHashKey(key);
        Value jsonDynFuncCall = value->getJsonValue();
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
        cerr << __FUNCTION__ << ":" << __LINE__<< "Bad or failed "<< endl;
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
        shared_ptr<DynFuncCall> data = make_shared<DynFuncCall>(callStack, sstaticHashKey);
        DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__ << data << endl;);
        __backtraceStaticMap[sstaticHashKey] = data;
    }
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__ << endl;__displayBacktraceStaticMap(););
}
