#include <cstdio>
#include <execinfo.h>
#include <fstream>
#include <json/json.h>
#include <stdlib.h>

#include "PrecisionTuner.hpp"    
using namespace std;
using namespace Json;

const unsigned int PrecisionTuner::MAXSTACKSIZE = 500;
const string PrecisionTuner::JSON_TOTALCALLSTACKS_KEY = "TotalCallStacks";
const string PrecisionTuner::JSON_MAIN_LIST = "IndependantCallStacks";
const string PrecisionTuner::JSON_CALLSTACK_LIST  = "CallStack";
const string PrecisionTuner::JSON_CALLSCOUNT_KEY = "CallsCount";
const string PrecisionTuner::JSON_LOWERCOUNT_KEY = "LowerCount";
const string PrecisionTuner::JSON_HASHKEY_KEY = "HashKey";

PrecisionTuner::PrecisionTuner(){
    char * envVarString = getenv("MINBOUND");
    if(envVarString)
        __minbound = atol(envVarString);
    envVarString = getenv("MAXBOUND");
    if(envVarString)
        __maxbound = atol(envVarString);
    envVarString = getenv("JSONFILE");
    if(envVarString)
        __build_callstacks_map_from_json_file(envVarString);
}

PrecisionTuner::~PrecisionTuner(){
    __display();
    __dump_json();
}

uint64_t PrecisionTuner::get_context_hash_backtrace(bool blowered) {
    unsigned long lowered = blowered ? 1 : 0;
    uint64_t hash = 0;
    vector<void*> btVec;
    void * buffer[MAXSTACKSIZE];
    const int size = backtrace(buffer, MAXSTACKSIZE);
    for(int i=0;i<size;i++){
        void * ip = (void*) ((char**)buffer)[i];
        btVec.push_back(ip);
        hash += (uint64_t) ip;
    }
    // if this hash is never seen before, record it.
    unordered_map<uint64_t, struct CallData>::iterator hashIte = __backtraceMap.find(hash);
    if(hashIte == __backtraceMap.end()) {
        __backtraceMap[hash] = {btVec,1,lowered};
        __totalCallStacks += 1;
#ifdef DEBUG
        printf("\n New Key in backtraceMap vec = %lx: %d\n",hash, btVec.size()) ;
#endif
    }else{ // Count the number of calls to this callstack
        __backtraceMap[hash].dyncount += 1;
        __backtraceMap[hash].loweredCount += lowered;
    }
    /* IF the backtraceMap has already been built by reading JSON delivered thanks to profiling
     * 
     *
     */
    //read_json_file(jsonFile);

    return  hash;
}

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
        double value, double parameter){
    float fvalue = (float)value;
    float fparameter = (float)parameter;
    double dres, res;
    float fres;

    fres = (double) sp_func(fvalue, fparameter);
    dres = func(value, parameter);
    return PrecisionTuner::__overloading_function(s,fres,dres, value);
}

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value){
    float fvalue = (float)value;
    double dres, res;
    float fres;

    fres = (double) sp_func(fvalue);
    dres = func(value);
    return PrecisionTuner::__overloading_function(s,fres,dres, value);
}

double PrecisionTuner::__overloading_function(string s, float fres, double dres, double value){
    bool singlePrecision = __dyncount >= __minbound && __dyncount < __maxbound;
    double res;

    get_context_hash_backtrace(singlePrecision);
    __dyncount++;
    if(singlePrecision){
        res = (double) fres;
        __loweredCount ++;
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
    fprintf(stderr,"LOWERED %lu\n", (unsigned long) __loweredCount);
    fprintf(stderr,"TOTAL_DYNCOUNT %lu\n", (unsigned long) __dyncount);
    fprintf(stderr,"MINBOUND %lu MAXBOUND %lu\n", __minbound, __maxbound);
}

void PrecisionTuner::__dump_json(){
    const char* jsonFile = getenv("JSONFILE");
    FILE * fp = NULL;
    if(NULL == jsonFile){
        fprintf(stderr, "JSONFILE environment variable not filled --> dumping on stdout\n");
        fp = stdout;
    }else{
        fp = fopen(jsonFile, "w");
        if(NULL == fp){
            fprintf(stderr, "Wrong jsonfile abspath: %s\n", jsonFile);
            fprintf(stderr, "Dumping on stdout\n");
            fp = stdout;
        }
    }
    fprintf(fp, "{\n");
    fprintf(fp, "\t\"TotalCount\": %lu,\n",__totalCallStacks);
    fprintf(fp, "\t\"IndependantCallStacks\": [\n");

    int callStackCount = 1;
    for (auto it = __backtraceMap.begin(); it != __backtraceMap.end(); ++it){
        unsigned long key = it->first;
        struct CallData value = it->second;
        vector <void*> stack = value.btVec;
        fprintf(fp, "\t\t{\"HashKey\": \"0x%lx\", \n\t\t\t\"CallsCount\": %lu, \n\t\t\t\"LowerCount\": %lu,\n\t\t\t\"CallStack\":[",
                key, value.dyncount, value.loweredCount);
        for(int i = 0; i < stack.size()-1; i++){
            void * ip = stack[i];
            fprintf(fp, "\"0x%lx\", ", (unsigned long)ip);
        }
        fprintf(fp, "\"0x%lx\"]\n\t",(unsigned long)stack[stack.size()-1]);
        const char *end = (callStackCount == __totalCallStacks) ? "}\n" : "},\n";
        fprintf(fp,"%s",end);
        callStackCount++;
    }
    fprintf(fp, "\t]\n");
    fprintf(fp, "}");
    fclose(fp);
}
#include <cassert>
void PrecisionTuner::__dump_stack(uint64_t key) {
    assert(__backtraceMap.find(key) != __backtraceMap.end());
    vector <void*>& stack = __backtraceMap[key].btVec;

    fprintf(stderr, "\n %lu", stack.size());
    for(int i = 0; i < stack.size(); i++)
        fprintf(stderr, "\t %lx", (unsigned long) stack[i]);

}
/*
   {"Anna" : { 
   "age": 18,
   "profession": "student"},
   "Ben" : {
   "age" : "nineteen",
   "profession": "mechanic"}
   }
 */
#include <sstream>
#include <iostream>

unordered_map<uint64_t, struct CallData> PrecisionTuner::__build_callstacks_map_from_json_file(char * fileAbsPath){
    /*TODO: Find a different name for callStack the object containing number of calls, 
      its call stack addresses and lowered count. 
     Because it is the name as the call stack, which is the list of virtual addresses. 
     */
    unordered_map<uint64_t, struct CallData> backtraceMap;
    std::ifstream infile(fileAbsPath, std::ifstream::binary);
    Value jsonDictionnary;
    infile >>  jsonDictionnary;

    __totalCallStacks = jsonDictionnary[JSON_TOTALCALLSTACKS_KEY].asUInt64();
    Value allCallStacks = jsonDictionnary[JSON_MAIN_LIST];
    /* Fill the backtraceMap with JSON values */
    for(unsigned int callStackIndex = 0; callStackIndex < allCallStacks.size(); callStackIndex++){
        // Get the callStack dictionnary
        Value callStack = allCallStacks[callStackIndex];
        Value callStackList = callStack[JSON_CALLSTACK_LIST];
        Value hashKey = callStack[JSON_HASHKEY_KEY];
        // It is made of CallStack list, CallsCount, HashKey and LowerCount
        vector<void *> btVector;
        unsigned long dyncount = callStack[JSON_CALLSCOUNT_KEY].asUInt64();
        unsigned long loweredCount = callStack[JSON_LOWERCOUNT_KEY].asUInt64();
        for(unsigned int btVecInd = 0; btVecInd < callStackList.size(); btVecInd++){
            string s = callStackList[btVecInd].asString();
            unsigned long value;
            istringstream iss(s);
            iss >> hex >> value;
            btVector.push_back((void*) value);
        }
        struct CallData data = {btVector, dyncount, loweredCount};
        string s = hashKey.asString();
        unsigned long value;
        istringstream iss(s);
        iss >> hex >> value;
        backtraceMap[value] = data;
        //TODO: backtraceMap seems not to be filled. 
        // implement a pretty print for struct CallData
        ///Does not appear when dumping the JSON
    }
    return __backtraceMap;
}

void PrecisionTuner::testJson(string jsonFile){
#ifdef DEBUG
    cerr << jsonFile << endl;
#endif
    char cstr[jsonFile.size() + 1];
	strcpy(cstr, jsonFile.c_str());
    __build_callstacks_map_from_json_file(cstr);
}
