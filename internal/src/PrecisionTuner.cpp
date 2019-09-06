#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>


#include <execinfo.h>
#include <json/json.h>

#include "PrecisionTuner.hpp"    
//#include "DynFuncCall.hpp"    
using namespace std;
using namespace Json;

const unsigned int PrecisionTuner::MAXSTACKSIZE         = 500;
const string PrecisionTuner::JSON_TOTALCALLSTACKS_KEY   = "TotalCallStacks";
const string PrecisionTuner::JSON_TOTALDYNCOUNT_KEY     = "CallsCount";
const string PrecisionTuner::JSON_TOTALLOWEREDCOUNT_KEY = "LowerCount";
const string PrecisionTuner::JSON_MAIN_LIST             = "IndependantCallStacks";
const string PrecisionTuner::DUMP_JSON_FILE             = "DUMPJSONFILE";
const string PrecisionTuner::READ_JSON_FILE             = "READJSONFILE";
const string PrecisionTuner::DEFAULT_READ_JSON_FILE     = "./data.json";
const string PrecisionTuner::JSON_HASHKEY_KEY           = "HashKey";

/* PrecisionTuner functions*/
PrecisionTuner::PrecisionTuner(){
    char * envVarString = getenv("MINBOUND");
    if(envVarString)
        __minbound = atol(envVarString);
    envVarString = getenv("MAXBOUND");
    if(envVarString)
        __maxbound = atol(envVarString);
    envVarString = getenv(READ_JSON_FILE.c_str());
    if(envVarString){
#ifdef DEBUG
        cerr << envVarString<< endl;
#endif
        if (strcmp(envVarString,"DEFAULT")==0)
            __buildAllDataFromJsonFile(DEFAULT_READ_JSON_FILE.c_str());
        else
            __buildAllDataFromJsonFile(envVarString);
    }
}

PrecisionTuner::~PrecisionTuner(){
    __display();
    __dump_json();
}

uint64_t PrecisionTuner::get_context_hash_backtrace(bool blowered) {
#ifdef DEBUG
    cerr << "uint64_t PrecisionTuner::get_context_hash_backtrace(bool blowered)" << blowered <<endl;
#endif
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
    if(hashIte == __backtraceDynamicMap.end()) {
        DynFuncCall dfc(btVec,blowered);
        __backtraceDynamicMap[hash] = dfc;
        __totalCallStacks += 1;
#ifdef DEBUG
        cerr << "New Key in backtraceMap vec = " << hash << " : " << btVec.size() << endl ;
#endif
    }else{ // Count the number of calls to this callstack
        __backtraceDynamicMap[hash].called(blowered);
    }
    if(__profiling){
    }else{
        __buildAllDataFromJsonFile(__jsonFileFromProfiling);
    }

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

    singlePrecision = __totalDynCount >= __minbound && __totalDynCount < __maxbound;
    get_context_hash_backtrace(singlePrecision);
    __totalDynCount++;
    if(singlePrecision){
        res = (double) fres;
        __totalLoweredCount ++;
    }else{
        res = dres;
    }
#ifdef DEBUG
    double relErr = fabs(fres - dres) / fabs(dres);
    if(singlePrecision)
        cerr << s << " dres=" << dres << " fres=" << fres << " RelError: " << relErr << " value=" << value <<endl;
    else
        cerr << s << " dres=" << dres<< " value=" << value << endl;
#endif
    return res;
}

void PrecisionTuner::__display(){
    fprintf(stderr,"TOTAL LOWERED %lu\n", (unsigned long) __totalLoweredCount);
    fprintf(stderr,"TOTAL_DYNCOUNT %lu\n", (unsigned long) __totalDynCount);
    fprintf(stderr,"MINBOUND %lu MAXBOUND %lu\n", __minbound, __maxbound);
}

void PrecisionTuner::__dump_json(){
    const char* jsonFile;
    bool useCout;
    filebuf fb;
    Value jsonDictionnary;
    Value jsonTotalCallStacks;
    Value jsonDynFuncCallsList;
    ostream outfile(NULL);

    jsonFile = getenv(DUMP_JSON_FILE.c_str());
    useCout = true;
    if(NULL == jsonFile) {
            fprintf(stderr, "Wrong jsonfile abspath: %s\n", jsonFile);
            fprintf(stderr, "Dumping on stdout\n");
            
    }else{
        fb.open(jsonFile,ios::out);
        if(!fb.is_open()){
            fprintf(stderr, "Wrong jsonfile abspath: %s\n",jsonFile);
            fprintf(stderr, "Dumping on stdout\n");
        }else
            useCout = false;
    }
    if (!useCout)
        ostream outfile(&fb);

    jsonTotalCallStacks = (UInt)__totalCallStacks;
    jsonDictionnary[JSON_TOTALCALLSTACKS_KEY] = jsonTotalCallStacks;
    for (auto it = __backtraceDynamicMap.begin(); it != __backtraceDynamicMap.end(); ++it){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        Value hashkey((UInt)key);
        Value jsonDynFuncCall = value.getJsonValue();
        jsonDynFuncCall[JSON_HASHKEY_KEY] = hashkey; 
        jsonDynFuncCallsList.append(jsonDynFuncCall);
    }
#ifdef DEBUG
    cerr <<jsonDynFuncCallsList<< endl;
#endif
    jsonDictionnary[JSON_MAIN_LIST] = jsonDynFuncCallsList;
    if (useCout)
        cout <<jsonDictionnary; 
    else
        outfile << jsonDictionnary; 
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

unordered_map<uint64_t, DynFuncCall> PrecisionTuner::__buildAllDataFromJsonFile(string fileAbsPath){
    /*TODO: Find a different name for callStack the object
      containing number of calls, its call stack addresses and lowered count.
      Because it is the name as the call stack, which is the list of virtual addresses.
     */
    //unordered_map<uint64_t, struct CallData> backtraceMap;
#ifdef DEBUG
    cerr << "STARTING __build_callstacks_map_from_json_file" << endl;
#endif
    std::ifstream infile(fileAbsPath, std::ifstream::binary);
    if(!stream_check(infile))
        exit(-1);
    Value jsonDictionnary;
    infile >>  jsonDictionnary;
#ifdef DEBUG
    cerr << "READING JSON __build_callstacks_map_from_json_file" << endl;
    cerr << jsonDictionnary << endl;
#endif


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
#ifdef DEBUG
    cerr << "DISPLAY __build_callstacks_map_from_json_file" << endl;
    __displayBacktraceDynMap();
    cerr << "ENDING __build_callstacks_map_from_json_file" << endl;
#endif
    return __backtraceDynamicMap;
}
