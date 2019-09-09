#include <cassert>
#include <cstdlib>
#include <execinfo.h>

#include "Debug.hpp"
#include "PrecisionTuner.hpp"    

using namespace std;

const unsigned int PrecisionTuner::MAXSTACKSIZE         = 500;

// Profiling mode
const string PrecisionTuner::DUMP_JSON_PROFILING_FILE     = "DUMPJSONPROFILINGFILE";
// Applying strategy mode
const string PrecisionTuner::DUMP_JSON_STRATSRESULTS_FILE = "DUMPJSONSTRATSRESULTSFILE";
const string PrecisionTuner::READ_JSON_PROFILING_FILE     = "READJSONPROFILINGFILE";
const string PrecisionTuner::READ_JSON_STRAT_FILE         = "READJSONSTRATFILE";

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

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
        double value, double parameter){
    float fvalue, fparameter, fres;
    double dres, res;

    fvalue = (float)value;
    fparameter = (float)parameter;

    vector<void*> btVec = __getContextHashBacktrace();
    fres = (double) sp_func(fvalue, fparameter);
    dres = func(value, parameter);
    return PrecisionTuner::__overloading_function(btVec, s,fres,dres, value);
}

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value){
    double dres, res;
    float fvalue, fres;

    fvalue = (float)value;

    vector<void*> btVec = __getContextHashBacktrace();
    fres = (double) sp_func(fvalue);
    dres = func(value);
    return PrecisionTuner::__overloading_function(btVec, s,fres,dres, value);
}

/*** PRIVATE FUNCTIONS ***/

vector<void*> PrecisionTuner::__getContextHashBacktrace() {
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

double PrecisionTuner::__overloading_function(vector<void*> &btVec, string s, float fres, double dres, double value){
    bool singlePrecision;
    double res;
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);

    switch(__mode){ 
        case APPLYING_STRAT:
            singlePrecision = __strategy.singlePrecision(__profile);
            DynFuncCall dfc(btVec, singlePrecision);
            __strategy.updateResults(dfc);
            break;
        case PROFILING:
            singlePrecision = false;
            DynFuncCall dfc(btVec);
            __profile.updateHashMap(dfc);
            break;
        default:
            cerr << "PrecisionTuner ERROR: no __mode chosen" << endl;
    }
    res = singlePrecision ? (double) fres : dres; 
    
    DEBUG("infoplus",double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " dres=" << dres << " fres=" << fres << " RelError: " << relErr << " value=" << value <<endl; else cerr << s << " dres=" << dres<< " value=" << value << endl;);
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return res;
}
