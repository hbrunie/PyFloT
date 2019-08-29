#include <stdlib.h>
#include <execinfo.h>
#include <cstdio>

#include "PrecisionTuner.hpp"    

static const unsigned int MAXSTACKSIZE = 500;

using namespace std;
PrecisionTuner::PrecisionTuner(){
    char * tmp = getenv("MINBOUND");
    if(tmp)
        __minbound = atol(tmp);
    tmp = getenv("MAXBOUND");
    if(tmp)
        __maxbound = atol(tmp);
}

PrecisionTuner::~PrecisionTuner(){
    __display();
    //__dump_json();
}

uint64_t PrecisionTuner::get_context_hash_backtrace() {
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
        __backtraceMap[hash] = {btVec,1,0};
        __totalCallStacks += 1;
#ifdef DEBUG2
        printf("\n New Key in backtraceMap vec = %lx: %d\n",hash, btVec.size()) ;
#endif
    }else{ // Count the number of calls to this callstack
        __backtraceMap[hash].dyncount += 1;
    }
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
    bool singlePrecision = false;
    double res;
    if(__dyncount >= __minbound && __dyncount < __maxbound){
        res = (double) fres;
        __loweredCount ++;
        singlePrecision = true;
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
    __dyncount++;
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
        fprintf(stderr, "Please fill the JSONFILE environment variable\n");
        exit(-1);
    }

    //jsonFile = JSONFILE.c_str();
    fp = fopen(jsonFile, "w");
    if(NULL == fp){
        fprintf(stderr, "Wrong jsonfile abspath: %s\n", jsonFile);
        exit(-1);
    }
    fprintf(fp, "{\n");
    fprintf(fp, "\t\"TotalCount\": %d,\n",__totalCallStacks);
    fprintf(fp, "\t\"IndependantCallStacks\": [\n");

    int callStackCount = 1;
    for (auto it = __backtraceMap.begin(); it != __backtraceMap.end(); ++it){
        uint64_t key = it->first;
        struct CallData value = it->second;
        vector <void*> stack = value.btVec;
        fprintf(fp, "\t\t{\"HashKey\": \"0x%lx\", \n\t\t\t\"CallsCount\": %lu, \n\t\t\t\"LowerCount\": %lu,\n\t\t\t\"CallStack\":[",
                key, value.dyncount, value.loweredCount);
        for(int i = 0; i < stack.size()-1; i++){
            void * ip = stack[i];
            fprintf(fp, "\"0x%lx\", ", ip);
        }
        fprintf(fp, "\"0x%lx\"]\n\t",stack[stack.size()-1]);
        const char *end = (callStackCount == __totalCallStacks) ? "}\n" : "},\n";
        fprintf(fp,"%s",end);
        callStackCount++;
    }
    fprintf(fp, "\t]\n");
    fprintf(fp, "}");
    fclose(fp);
}

void PrecisionTuner::__dump_stack(uint64_t key) {
    assert(__backtraceMap.find(key) != __backtraceMap.end());
    vector <void*>& stack = __backtraceMap[key].btVec;

    fprintf(stderr, "\n %d", stack.size());
    for(int i = 0; i < stack.size(); i++)
        fprintf(stderr, "\t %lx", stack[i]);

}
