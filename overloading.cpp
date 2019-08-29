#include <alloca.h>
#include <assert.h>
#include <bits/stdc++.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <execinfo.h>
#include <fstream>
#include <iostream>
#include <limits.h>
#include <sstream>
#include <vector>

#include <dlfcn.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>

#include <execinfo.h>
#define MAXSTACKSIZE 500

#include "PrecisionTuner.hpp"

using namespace std;

static string JSONFILE = "Users/hbrunie/Codes/output.json";

/******** Globals variables **********/
struct callData{
    vector<void*> btVec;
    unsigned long int callsCount;
};

static unordered_map<uint64_t, struct callData> backtraceMap;
static unsigned long int TOTAL_CALLS = 0;
static unsigned long int PREV_TOTAL_CALLS = 0;
static PrecisionTuner ptuner;

/******** Function definitions **********/

static void dumpJSON(){
    const char* jsonfile = getenv("JSONFILE");
    FILE * fp = NULL;
    if(NULL == jsonfile){
        fprintf(stderr, "Please fill the JSONFILE environment variable\n");
        exit(-1);
    }

    jsonfile = JSONFILE.c_str();
    fp = fopen(jsonfile, "w");
    if(NULL == fp){
        fprintf(stderr, "Wrong jsonfile abspath: %s\n", jsonfile);
        exit(-1);
    }
    fprintf(fp, "{\n");
    fprintf(fp, "\t\"TotalCount\": %d,\n",TOTAL_CALLS);
    fprintf(fp, "\t\"IndependantCallStacks\": [\n");

    int callStackCount = 1;
    for (auto it = backtraceMap.begin(); it != backtraceMap.end(); ++it){
        uint64_t key = it->first;
        struct callData value = it->second;
        vector <void*> stack = value.btVec;
        fprintf(fp, "\t\t{\"HashKey\": \"0x%lx\", \n\t\t\t\"CallsCount\": %lu,\n\t\t\t\"CallStack\":[",
                key, value.callsCount);
        for(int i = 0; i < stack.size()-1; i++){
            void * ip = stack[i];
            fprintf(fp, "\"0x%lx\", ", ip);
        }
        fprintf(fp, "\"0x%lx\"]\n\t",stack[stack.size()-1]);
        const char *end = (callStackCount == TOTAL_CALLS) ? "}\n" : "},\n";
        fprintf(fp,"%s",end);
        callStackCount++;
    }
    fprintf(fp, "\t]\n");
    fprintf(fp, "}");
    fclose(fp);
}

static inline uint64_t GetContextHashWithBackTrace() {
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
    unordered_map<uint64_t, struct callData>::iterator hash_ite = backtraceMap.find(hash);
    if(hash_ite == backtraceMap.end()) {
        backtraceMap[hash] = {btVec,1};
        TOTAL_CALLS += 1;
#ifdef DEBUG2
        printf("\n New Key in backtraceMap vec = %lx: %d\n",hash, btVec.size()) ;
#endif
    }else{ // Count the number of calls to this callstack
        backtraceMap[hash].callsCount += 1;
    }
    return  hash;
}

static void DumpStack(uint64_t key) {
    assert(backtraceMap.find(key) != backtraceMap.end());
    vector <void*>& stack = backtraceMap[key].btVec;

    fprintf(stderr, "\n %d", stack.size());
    for(int i = 0; i < stack.size(); i++)
        fprintf(stderr, "\t %lx", stack[i]);

}

/* *** Overloading functions *** */

/* exponential function */
double __overloaded_exp(double var) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(expf,exp,var);
}

/* logarithm function */
double __overloaded_log(double var) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(logf, log,var);
}

/* logarithm function */
double __overloaded_log10(double var) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(log10f, log10,var);
}

/* cosinus function */
double __overloaded_cos(double var) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(cosf,cos,var);
}

/* sinus function */
double __overloaded_sin(double var) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(sinf,sin,var);
}

/* sqrt function */
double __overloaded_sqrt(double var) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(sqrtf,sqrt,var);
}

/* power function */
double __overloaded_pow(double var, double p) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(powf,pow,var,p);
}

/* fabs function */
static bool fabs_first=true;
double __overloaded_fabs(double var) {
    uint64_t key = GetContextHashWithBackTrace();
    return ptuner.overloading_function(fabs,fabs,var);
}
