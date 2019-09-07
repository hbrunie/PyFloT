#include <cassert>
#include <cstdlib>
#include <execinfo.h>

#include "Debug.hpp"
#include "PrecisionTuner.hpp"    

using namespace std;

const unsigned int PrecisionTuner::MAXSTACKSIZE         = 500;

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
        __profile = Profile(true, envVarString);
        // TODO:NO READING JSON --> execute, generate Json and dump it.
    }else{// Applying strategy mode
        DEBUG("info", cerr << "APPLYING strategy mode PrecisionTuner constructor" << endl;);
        __mode = APPLYING_STRAT;
        bool checkOk = true;
        CHECK_NULL(envVarString = getenv(READ_JSON_PROFILING_FILE.c_str()),READ_JSON_PROFILING_FILE,checkOk);
        if(checkOk){
            string profileData(envVarString);
            __profile  = Profile(false, profileData);
        }
        CHECK_NULL(envVarString = getenv(DUMP_JSON_STRATSRESULTS_FILE.c_str()), DUMP_JSON_STRATSRESULTS_FILE, checkOk);
        CHECK_NULL(envVarString = getenv(READ_JSON_STRAT_FILE.c_str()), READ_JSON_STRAT_FILE, checkOk);
        if(checkOk){
            string dumpStratResults(envVarString);
            string readStratFromJsonFile(envVarString);
            __strategy = Strategy(readStratFromJsonFile, dumpStratResults);
        }
    }
    DEBUG("info", cerr << "ENDING " << __FUNCTION__<< endl;);
}

PrecisionTuner::~PrecisionTuner(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    DEBUG("infoplus",cerr << __FUNCTION__ << __mode << endl;);
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

vector<void*> PrecisionTuner::getContextHashBacktrace() {
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    vector<void*> btVec;
    void * buffer[MAXSTACKSIZE];
    assert(NULL != buffer);
    const int size = backtrace(buffer, MAXSTACKSIZE);
    DEBUG("info",cerr << __FUNCTION__ << "size: "<< size << endl;);
    assert(size>0);
    for(int i=0;i<size;i++){
        void * ip = (void*) ((char**)buffer)[i];
        assert(NULL != ip);
        btVec.push_back(ip);
    }
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return btVec;
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
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);

    singlePrecision = __strategy.singlePrecision(__profile);
    vector<void*> btVec = getContextHashBacktrace();
    DynFuncCall dfc(btVec, singlePrecision);
    __profile.updateHashMap(dfc);
    res = singlePrecision ? (double) fres : dres; 
    
    DEBUG("infoplus",double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " dres=" << dres << " fres=" << fres << " RelError: " << relErr << " value=" << value <<endl; else cerr << s << " dres=" << dres<< " value=" << value << endl;);
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return res;
}

//void PrecisionTuner::__dumpProfileJson(const char * jsonFileEnvVar){
//    const char* jsonFile;
//    bool useCout;
//    filebuf fb;
//    Value jsonDictionary;
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
