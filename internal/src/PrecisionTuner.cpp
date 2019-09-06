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
#include "Strategy.hpp"    
#include "PrecisionTuner.hpp"    

using namespace std;
using namespace Json;

const unsigned int PrecisionTuner::MAXSTACKSIZE         = 500;
const string PrecisionTuner::JSON_TOTALCALLSTACKS_KEY   = "TotalCallStacks";
const string PrecisionTuner::JSON_TOTALDYNCOUNT_KEY     = "CallsCount";
const string PrecisionTuner::JSON_TOTALLOWEREDCOUNT_KEY = "LowerCount";
const string PrecisionTuner::JSON_MAIN_LIST             = "IndependantCallStacks";
const string PrecisionTuner::JSON_HASHKEY_KEY           = "HashKey";

// JSON FILE ENV VARS
// Profiling mode
const string PrecisionTuner::DUMP_JSON_PROFILING_FILE     = "DUMPJSONPROFILINGFILE";
// Applying strategy mode
const string PrecisionTuner::DUMP_JSON_STRATSRESULTS_FILE = "DUMPJSONSTRATSRESULTSFILE";
const string PrecisionTuner::READ_JSON_PROFILING_FILE     = "READJSONPROFILINGFILE";
const string PrecisionTuner::READ_JSON_STRAT_FILE         = "READJSONSTRATFILE";

/* PrecisionTuner functions*/
PrecisionTuner::PrecisionTuner(){
    /* 2 modes: Profiling, Applying Strategy (AS)
     * if  DUMP_JSON_PROFILING_FILE is set: Profiling mode
     * otherwise AS mode
     */
    debugtypeOption(getenv("DEBUG"));
    DEBUG("info", cerr << "STARTING PrecisionTuner constructor" << endl;);
    char * envVarString = getenv(DUMP_JSON_PROFILING_FILE.c_str());
    if(envVarString){// Profiling mode
        DEBUG("info", cerr << "PROFILING mode PrecisionTuner constructor" << endl;);
        __mode = PROFILING;
        // TODO:NO READING JSON --> execute, generate Json and dump it.
    }else{// Applying strategy mode
        DEBUG("info", cerr << "APPLYING strategy mode PrecisionTuner constructor" << endl;);
        __mode = APPLYING_STRAT;
        bool checkOk = true;
        CHECK_NULL(envVarString = getenv(READ_JSON_PROFILING_FILE.c_str()),READ_JSON_PROFILING_FILE,checkOk);
        if(checkOk){
            string profileData(envVarString);
            __profile  = Profile(profileData);
        }
        CHECK_NULL(envVarString = getenv(DUMP_JSON_STRATSRESULTS_FILE.c_str()), DUMP_JSON_STRATSRESULTS_FILE, checkOk);
        CHECK_NULL(envVarString = getenv(READ_JSON_STRAT_FILE.c_str()), READ_JSON_STRAT_FILE, checkOk);
        if(checkOk){
            string dumpStratResults(envVarString);
            string readStratFromJsonFile(envVarString);
            __strategy = Strategy(readStratFromJsonFile, dumpStratResults);
        }

        //__buildProfiledDataFromJsonFile(envVarString);
        //__buildStrategyFromJsonFile(envVarString);
    }
    DEBUG("info", cerr << "ENDING PrecisionTuner constructor" << endl;);
}

PrecisionTuner::~PrecisionTuner(){
    switch(__mode){ 
        case APPLYING_STRAT:
            __strategy.dumpJson();
            break;
        case PROFILING:
            __profile.dumpJson();
            break;
        default:
            cerr << "PrecisionTuner ERROR: no __mode chosen" << endl;
    }
}

uint64_t PrecisionTuner::get_context_hash_backtrace(bool blowered) {
    DEBUG("info",cerr << "STARTING uint64_t PrecisionTuner::get_context_hash_backtrace(bool blowered)" << blowered <<endl;);
    uint64_t hash = 0;
    vector<void*> btVec;
    void * buffer[MAXSTACKSIZE];
    assert(NULL != buffer);
    const int size = backtrace(buffer, MAXSTACKSIZE);
    assert(size>0);
    for(int i=0;i<size;i++){
        void * ip = (void*) ((char**)buffer)[i];
        assert(NULL != ip);
        assert( (hash + (uint64_t) ip) < numeric_limits<uint64_t>::max());
        btVec.push_back(ip);
        hash += (uint64_t) ip;
    }
    // if this hash is never seen before, record it.
    unordered_map<uint64_t, DynFuncCall>::iterator hashIte = __backtraceDynamicMap.find(hash);
    DEBUG("info",cerr << "LOOKING FOR HASH: "<< hash << " uint64_t PrecisionTuner::get_context_hash_backtrace(bool blowered)" <<endl;);
    if(hashIte == __backtraceDynamicMap.end()) {
        DynFuncCall dfc(btVec,blowered);
        __backtraceDynamicMap[hash] = dfc;
        __totalCallStacks += 1;
        DEBUG("info",cerr << "New Key in backtraceMap vec = " << hash << " : " << btVec.size() << endl ;);
    }else{ // Count the number of calls to this callstack
        __backtraceDynamicMap[hash].called(blowered);
    }

    DEBUG("info",cerr << "ENDING uint64_t PrecisionTuner::get_context_hash_backtrace(bool blowered)" << blowered <<endl;);
    return  hash;
}

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
        double value, double parameter){
    float fvalue, fparameter, fres;
    double dres, res;

    fvalue = (float)value;
    fparameter = (float)parameter;

    fres = (double) sp_func(fvalue, fparameter);
    dres = func(value, parameter);
    return PrecisionTuner::__overloading_function(s,fres,dres, value);
}

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value){
    double dres, res;
    float fvalue, fres;

    fvalue = (float)value;

    fres = (double) sp_func(fvalue);
    dres = func(value);
    return PrecisionTuner::__overloading_function(s,fres,dres, value);
}

double PrecisionTuner::__overloading_function(string s, float fres, double dres, double value){
    bool singlePrecision;
    double res;

    singlePrecision = __strategy.singlePrecision(__currentDynCallCount);
    get_context_hash_backtrace(singlePrecision);
    __totalDynCount++;
    if(singlePrecision){
        res = (double) fres;
        __totalLoweredCount ++;
    }else{
        res = dres;
    }
    double relErr = fabs(fres - dres) / fabs(dres);
    DEBUG("infoplus",if(singlePrecision)  cerr << s << " dres=" << dres << " fres=" << fres << " RelError: " << relErr << " value=" << value <<endl; else cerr << s << " dres=" << dres<< " value=" << value << endl;);
    return res;
}

//void PrecisionTuner::__dumpProfileJson(const char * jsonFileEnvVar){
//    const char* jsonFile;
//    bool useCout;
//    filebuf fb;
//    Value jsonDictionnary;
//    Value jsonTotalCallStacks;
//    Value jsonDynFuncCallsList;
//    ostream outfile(NULL);
//
//    jsonFile = getenv(jsonFile);
//    useCout = true;
//    if(NULL == jsonFile) {
//            fprintf(stderr, "Wrong jsonfile abspath: %s\n", jsonFile);
//            fprintf(stderr, "Dumping on stdout\n");
//            
//    }else{
//        fb.open(jsonFile,ios::out);
//        if(!fb.is_open()){
//            fprintf(stderr, "Wrong jsonfile abspath: %s\n",jsonFile);
//            fprintf(stderr, "Dumping on stdout\n");
//        }else
//            useCout = false;
//    }
//    if (!useCout)
//        ostream outfile(&fb);
//}

void PrecisionTuner::__dumpHashMapJson(ostream &os, unordered_map<uint64_t, DynFuncCall> &hashMap){
    Value jsonDictionnary;
    Value jsonDynFuncCallsList;
    for (auto it = hashMap.begin(); it != hashMap.end(); ++it){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        Value hashkey((UInt)key);
        Value jsonDynFuncCall = value.getJsonValue();
        jsonDynFuncCall[JSON_HASHKEY_KEY] = hashkey; 
        jsonDynFuncCallsList.append(jsonDynFuncCall);
    }
    DEBUG("infoplus",cerr <<jsonDynFuncCallsList<< endl;);
    jsonDictionnary[JSON_MAIN_LIST] = jsonDynFuncCallsList;
    os << jsonDictionnary << endl;
    //if (useCout)
    //    cout <<jsonDictionnary; 
    //else
    //    outfile << jsonDictionnary; 
    //TODO: find proper C++ way to do this fopen with defaut == cout
    // close the file
}

void PrecisionTuner::__dump_stack(uint64_t key) {
    assert(__backtraceDynamicMap.find(key) != __backtraceDynamicMap.end());
    __backtraceDynamicMap[key].dumpStack();
}

bool stream_check(ifstream& s){
    if(s.bad() || s.fail()){
        cerr << "Bad or failed "<< endl;
    }
    if(s.good() && s.is_open())
        return true;
    return false;
}

void PrecisionTuner::__displayBacktraceDynMap(){
    for (auto it = __backtraceDynamicMap.begin(); it != __backtraceDynamicMap.end(); it++){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        cerr << value << endl;
    }
}

void PrecisionTuner::__buildStrategyFromJsonFile(string fileAbsPath){
}

void PrecisionTuner::__buildProfiledDataFromJsonFile(string fileAbsPath){
    /*TODO: Find a different name for callStack the object
      containing number of calls, its call stack addresses and lowered count.
      Because it is the name as the call stack, which is the list of virtual addresses.
     */
    //unordered_map<uint64_t, struct CallData> backtraceMap;
    DEBUG("info",cerr << "STARTING __build_callstacks_map_from_json_file" << endl;);
    std::ifstream infile(fileAbsPath, std::ifstream::binary);
    if(!stream_check(infile))
        exit(-1);
    Value jsonDictionnary;
    infile >>  jsonDictionnary;
    DEBUG("info",cerr << "READING JSON __build_callstacks_map_from_json_file" << endl;);
    DEBUG("infoplus",cerr << jsonDictionnary << endl;);


    __totalCallStacks = jsonDictionnary[JSON_TOTALCALLSTACKS_KEY].asUInt64();
    __totalLoweredCount = jsonDictionnary[JSON_TOTALLOWEREDCOUNT_KEY].asUInt64();
    __totalDynCount = jsonDictionnary[JSON_TOTALDYNCOUNT_KEY].asUInt64();
    Value callStacksList = jsonDictionnary[JSON_MAIN_LIST];
    /* Fill the backtraceMap with JSON values */
    cerr << callStacksList.size() << endl;
    for(unsigned int callStackIndex = 0; callStackIndex < callStacksList.size(); callStackIndex++){
        // Get the callStack dictionnary
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
