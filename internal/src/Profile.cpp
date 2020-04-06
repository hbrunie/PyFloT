#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <iostream>
#include <limits>
#include <regex>
#include <sstream>
#include <string>

#include <execinfo.h>
#include <json/json.h>
#include <math.h>

#include "Debug.hpp"
#include "Profile.hpp"
#include "ShadowValue.hpp"
#include "Utils.hpp"

// ONE == 4 because of Ptuning internal calls below __overloaded_mathFunction
#define ONE 4

using namespace std;
using namespace Json;

// Profiling mode
const string Profile::DUMP_JSON_PROFILING_FILE     = "PRECISION_TUNER_DUMPJSON";
const string Profile::DUMP_DIR                     = "PRECISION_TUNER_OUTPUT_DIRECTORY";
// Applying strategy mode
const string Profile::DUMP_JSON_STRATSRESULTS_FILE = "PRECISION_TUNER_DUMPJSON";
const string Profile::DUMP_CSV_PROFILING_FILE      = "PRECISION_TUNER_DUMPCSV";
const string Profile::READ_JSON_PROFILE_STRAT_FILE = "PRECISION_TUNER_READJSON";
const string Profile::BACKTRACE_LIST               = "BACKTRACE_LIST";
const char * Profile::TARGET_EXE_FILENAME          = "TARGET_FILENAME";

const string Profile::JSON_TOTALCALLSTACKS_KEY  = "TotalCallStacks";
const string Profile::JSON_TOTALDYNCOUNT_KEY    = "CallsCount";
const string Profile::JSON_MAIN_LIST            = "IndependantCallStacks";
const string Profile::JSON_HASHKEY_KEY          = "HashKey";
const string Profile::JSON_CSV_FILENAME         = "CSVFileName";

const string Profile::DEFAULT_READ_JSON_STRAT_FILE       = "dumpProfile.json";
const string Profile::DEFAULT_DUMP_CSV_PROF_FILE         = "dumpCSVdynCallSite";
const string Profile::DEFAULT_DUMP_JSON_PROF_FILE        = "dumpProfile.json";
const string Profile::DEFAULT_DUMPDIR                    = "./";
const string Profile::DEFAULT_DUMP_JSON_STRATRESULT_FILE = "dumpJsonStratResults.json";
const string Profile::DEFAULT_BACKTRACE_LIST             = "BacktraceList.txt";

uintptr_t hashLabel(string label){
    uintptr_t key = 0;
    uint32_t p = 0;
    for (auto it = label.cbegin() ; it != label.cend(); ++it){
        uintptr_t letter = (uintptr_t) *it;
        uintptr_t letterBase = pow(letter,p);
        assert( (key+letterBase) <numeric_limits<uintptr_t>::max());
        key += letterBase;
        p++;
    }
    return key;
}

Profile::~Profile(){
    // delete all DynCallFunc objects: automatic with shared pointers
}

Profile::Profile(bool mode) : __mode(mode){//True --> ApplyingStrat
    if(__mode)
        __buildProfiledDataFromJsonFile();
}

/* the Static Hash Key corresponds to a non ASLR dependent HashKey
 * User can define the level of callstack he wants to use for
 * defining the DynamicCallSite.
 * By default the level is 1: only the source code function call is taken into account.
 */
string Profile::__staticHashKey(vector<void*> btVec){
    string statHashKey;
    string tmpHash;
    // Choosing level: ONE <= size <= btVec.size();
    //uint64_t size = btVec.size();//Higher for deeper analysis
    uint64_t size = std::min(btVec.size(),(long unsigned int )(ONE+16));//Higher for deeper analysis
    void ** btpointer = &btVec[0];
    char ** symbols = backtrace_symbols(btpointer, size);
    unsigned int cnt = 0;
    char * tmp = symbols[cnt];
    while(NULL != tmp && cnt < size){
        string backtraceSymbols(tmp);
        DEBUG("statickey",cerr << "backtraceSymbols: " << backtraceSymbols << endl ;);
#ifndef MAC_OS
        // /path/to/libprecisiontuning.so(Mangl_D2_FUncName+0x2e) [0x2aaaaacf5ede]
        regex regex("[-_a-zA-Z/.0-9]+\\(([a-zA-Z_0-9]+)\\+([xa-f0-9]+)\\)\\s\\[0x[a-f0-9]+\\]$");
        smatch m;
        regex_match(backtraceSymbols, m, regex);
        statHashKey += m[1];
        statHashKey += m[2];
        DEBUG("statickey", cerr << "Function: " << m[1] << endl;);
        DEBUG("statickey", cerr << "?main: " << (m[1].compare("main")==0) << endl;);
        if(m[1].compare("main")==0)
            cnt=size;
#else// Mac OS environment
        std::vector<std::string> result;
        std::istringstream iss(backtraceSymbols);
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
#endif
        cnt++;
        tmp = symbols[cnt];
    }
    DEBUG("statickey",cerr << __FUNCTION__ << ":" << __LINE__
            << " staticHashKey: " << statHashKey << endl;);
    return statHashKey;
}

uintptr_t Profile::__dynHashKey(vector<void*> btVec){
    //TODO: factorize dynHashKey and staticHashKey code, always same size?
    uintptr_t dynHashKey = 0;
    uint64_t cnt = 0;
    // Choosing level: ONE <= size <= btVec.size();
    //uint64_t size = btVec.size();//Higher for deeper analysis
    uint64_t size = ONE+16;//Higher for deeper analysis
    for(auto it = btVec.begin(); it != btVec.end() && cnt < size; it++){
        void *ip = *it;
        assert(NULL != ip);
        assert( (dynHashKey+ (uintptr_t) ip) <numeric_limits<uintptr_t>::max());
        DEBUG("dynHashKey",cerr << __FUNCTION__ << ":" << __LINE__ << dynHashKey
                << " " << cnt << "/" << ONE << " " << (uintptr_t) ip << endl;);
        dynHashKey += (uintptr_t) ip;
        cnt++;
    }
    return dynHashKey;
}

bool Profile::applyStrategy(vector<void*> & btVec, string label){
    //compute hash
#ifndef USE_LABEL
    //TODO: more efficient to change hashMap with key string?
    //TODO create a class callstack with string and btVec
    uintptr_t dynHashKey = __dynHashKey(btVec);
    UNUSED(label);
#else
    uintptr_t dynHashKey = hashLabel(label);
    UNUSED(btVec);
#endif
    shared_ptr<DynFuncCall> dfc;
    DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__ << " " << dfc << endl);
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__<<  " Static map " << endl;
          __displayBacktraceStaticMap(););
    // if exist or not go on perm HashMap
    auto hashKeyIte = __backtraceDynamicMap.find(dynHashKey);
    if(hashKeyIte == __backtraceDynamicMap.end()){
        // Current call stack seen for FIRST time
#ifndef USE_LABEL
        string staticHashKey = __staticHashKey(btVec);
#else
        string staticHashKey = label;
#endif
        DEBUG("dfc",cerr << __FUNCTION__
               << ":" << __LINE__<< " staticHashKey:"
               << staticHashKey << endl);

        auto stathashKeyIte = __backtraceStaticMap.find(staticHashKey);
        if(stathashKeyIte == __backtraceStaticMap.end()){
            // Current call stack not in static map:
            // It was not encountered during profiling.
            cerr << __FUNCTION__ << ":" << __LINE__ << " staticHashKey:" << staticHashKey
                << " encountered for first time." << endl;
            // DFC did not exist: create it.
            // TODO: profile it?
            dfc = make_shared<DynFuncCall>(btVec, dynHashKey);
            __backtraceStaticMap[staticHashKey] = dfc;
        }else{
            // DFC already exists
            dfc = __backtraceStaticMap[staticHashKey];
            dfc->updateStrategyBacktrace();
        }
        __backtraceDynamicMap[dynHashKey] = dfc;
    }else{
        // Current call stack already encountered
        dfc = __backtraceDynamicMap[dynHashKey];
        DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
    }
    // Then compare currentDyncount with set
    bool res = dfc->applyStrategyBacktrace();
    DEBUG("dfc",cerr << __FUNCTION__ << ":" << __LINE__<< " " << dfc << endl);
    DEBUG("key",cerr << __FUNCTION__ << ":" << __LINE__<< " Dynamic map " << endl;__displayBacktraceDynMap(););
    return res;
}

/* Compute hash and add or update DynamicHashMap
*/
void Profile::applyProfiling(vector<void*> & btVec, string label, ShadowValue &sv){
#ifndef USE_LABEL
    //TODO: more efficient to change hashMap with key string?
    uintptr_t dynHashKey = __dynHashKey(btVec);
    UNUSED(label);
#else
    uintptr_t dynHashKey = hashLabel(label);
#endif
    shared_ptr<DynFuncCall> dfc(nullptr);
    auto dynHashKeyIte = __backtraceDynamicMap.find(dynHashKey);
    /* Can not find the element in Dynamic Hash Map */
    if(dynHashKeyIte == __backtraceDynamicMap.end()) {
        dfc = make_shared<DynFuncCall>(btVec, dynHashKey);
        __backtraceDynamicMap[dynHashKey] = dfc;
        /* Update Static HashMap */
#ifndef USE_LABEL
        string staticHashKey = __staticHashKey(btVec);
#else
        string staticHashKey = label;
#endif
        /* Dump all statichash key in FILE for use by backtraceStrategy on
         * other executions.
         * */
        //TODO bad name, not JSON file
        ofstream f = writeJSONFile(BACKTRACE_LIST,DEFAULT_BACKTRACE_LIST,
                DUMP_DIR, DEFAULT_DUMPDIR);
        f << staticHashKey << endl;
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
    dfc->applyProfiling(sv);
    __totalDynCount++;
}

void Profile::dumpJsonPlusCSV(){
    __dumpReducedJsonPermanentHashMap();
    __dumpCSVdynamicCalls();
}

void Profile::dumpJson(){
    __dumpFullJsonPermanentHashMap();
}

void Profile::__displayBacktraceStaticMap(){
    DEBUG("info",cerr << __FUNCTION__ << ":" << __LINE__<< endl;);
    for (auto it = __backtraceStaticMap.begin(); it != __backtraceStaticMap.end(); it++){
        string key = it->first;
        shared_ptr<DynFuncCall>value = it->second;
        cerr << *value << endl;
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

void Profile::__dumpCSVdynamicCalls(){
    ofstream dumpFile;
    unsigned int index = 0;
    string fileName;
    for (auto it = __backtraceStaticMap.begin(); it != __backtraceStaticMap.end(); ++it){
        dumpFile = writeCSVFile(DUMP_CSV_PROFILING_FILE,
                DEFAULT_DUMP_CSV_PROF_FILE, DUMP_DIR, DEFAULT_DUMPDIR, index);
        shared_ptr<DynFuncCall>value = it->second;
        dumpFile << "index timeStamp argument doubleP singleP absErr relErr spBoolean callSite" << endl;
        dumpFile << value->getCSVformat(index) << endl;;
        index++;
    }
}

void Profile::__dumpFullJsonPermanentHashMap(){
    __dumpJsonPermanentHashMap(false);
}
void Profile::__dumpReducedJsonPermanentHashMap(){
    __dumpJsonPermanentHashMap(true);
}

void Profile::__dumpJsonPermanentHashMap(bool dumpReduced){
    DEBUGINFO("STARTING");
    char * targetExe = getenv(TARGET_EXE_FILENAME);
    assert(NULL != targetExe);
    Value jsonDictionary;
    Value jsonDynFuncCallsList;
    Value jsonTotalCallStacks = (UInt)__totalCallStacks;
    jsonDictionary[JSON_TOTALCALLSTACKS_KEY] = jsonTotalCallStacks;
    unsigned int index = 0;
    for (auto it = __backtraceStaticMap.begin(); it != __backtraceStaticMap.end(); ++it){
        string key = it->first;
        shared_ptr<DynFuncCall>value = it->second;
        Value statHashKey(key);
        Value jsonDynFuncCall;
        //Reduced in JSON, rest of data in CSV
        if(dumpReduced)
            jsonDynFuncCall = value->getReducedJsonValue(targetExe);
        else
            jsonDynFuncCall = value->getFullJsonValue(targetExe);
        jsonDynFuncCall[JSON_HASHKEY_KEY] = statHashKey;
        jsonDynFuncCall[JSON_CSV_FILENAME] =
            string("dumpCSVdynCallSite-") + to_string(index++) + string(".csv");
        jsonDynFuncCallsList.append(jsonDynFuncCall);
    }
    jsonDictionary[JSON_MAIN_LIST] = jsonDynFuncCallsList;
    DEBUGINFO("JSON Dict: " << endl << jsonDictionary);
    ofstream dumpFile;
    if(__mode == 0)//Applying prof is private to Precision TUner ...
        dumpFile = writeJSONFile(DUMP_JSON_PROFILING_FILE,
                DEFAULT_DUMP_JSON_PROF_FILE, DUMP_DIR, DEFAULT_DUMPDIR);
    else
        dumpFile = writeJSONFile(DUMP_JSON_STRATSRESULTS_FILE, DEFAULT_DUMP_JSON_STRATRESULT_FILE
                , DUMP_DIR, DEFAULT_DUMPDIR);
    dumpFile << jsonDictionary << endl;;
    DEBUGINFO("ENDING");
}

// Applying Strategy
// Read JSON strategy file and fill hashmap.
void Profile::__buildProfiledDataFromJsonFile(){
    DEBUGINFO("STARTING");
    Value jsonDictionary;
    ifstream readProf = readFile(READ_JSON_PROFILE_STRAT_FILE, DEFAULT_READ_JSON_STRAT_FILE);
    readProf >>  jsonDictionary;
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
