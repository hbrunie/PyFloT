#include <cassert>
#include <cstdlib>
#include <iomanip>
#include <execinfo.h>

#include "Debug.hpp"
#include "PrecisionTuner.hpp"    

using namespace std;

const unsigned int PrecisionTuner::MAXSTACKSIZE         = 500;

// Profiling mode
const string PrecisionTuner::DUMP_JSON_PROFILING_FILE     = "DUMPJSONPROFILINGFILE";
// Applying strategy mode
const string PrecisionTuner::DUMP_JSON_STRATSRESULTS_FILE     = "DUMPJSONSTRATSRESULTSFILE";
const string PrecisionTuner::READ_JSON_PROFILE_STRAT_FILE     = "READJSONPROFILESTRATFILE";

PrecisionTuner::PrecisionTuner(){
    /* 2 modes: Profiling, Applying Strategy (AS)
     * if  DUMP_JSON_PROFILING_FILE is set: Profiling mode
     * otherwise AS mode
     */
    char *envVarString=NULL, * envVarString1 = NULL, * envVarString2=NULL;
#ifndef NDEBUG
    debugtypeOption(getenv("DEBUG"));
#endif
    envVarString = getenv(DUMP_JSON_PROFILING_FILE.c_str());
    DEBUG("info", cerr << __FUNCTION__ << ": "<< DUMP_JSON_PROFILING_FILE
            << " " << envVarString << endl;);
    fprintf(stderr, "%p\n",envVarString);
    if(NULL != envVarString && strlen(envVarString) > 1){
        DEBUG("info", cerr << __FUNCTION__ << ": MODE PROFILING " << endl;);
        __mode = PROFILING;
        string dumpFile(envVarString);
        __profile = new Profile(true, "None", dumpFile);
    }else{// Applying strategy mode
        DEBUG("info", cerr << __FUNCTION__ << ": MODE APPLYING_STRAT " << endl;);
        __mode = APPLYING_STRAT;
        bool checkOk = true;
        CHECK_NULL(envVarString1 = getenv(READ_JSON_PROFILE_STRAT_FILE.c_str()),READ_JSON_PROFILE_STRAT_FILE,checkOk);
        CHECK_NULL(envVarString2 = getenv(DUMP_JSON_STRATSRESULTS_FILE.c_str()), DUMP_JSON_STRATSRESULTS_FILE, checkOk);
        DEBUG("info", cerr << __FUNCTION__ << ": "<< DUMP_JSON_STRATSRESULTS_FILE
                << " " << string(envVarString1) << endl;);
        DEBUG("info", cerr << __FUNCTION__ << ": "<< READ_JSON_PROFILE_STRAT_FILE
                << " " << string(envVarString2) << endl;);
        if(checkOk && strlen(envVarString1) > 1 && strlen(envVarString2) > 1){
            string profileData(envVarString1);
            string dumpStratResults(envVarString2);
            DEBUG("apply", cerr << __FUNCTION__ << "profileData: " << profileData << " dumpStratResults: " << dumpStratResults << endl;);
            __profile  = new Profile(false, profileData, dumpStratResults);
        }
    }
    DEBUG("info", cerr << "ENDING " << __FUNCTION__<< endl;);
}

PrecisionTuner::~PrecisionTuner(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    DEBUG("infoplus",cerr << __FUNCTION__ << __mode << endl;);
    __profile->dumpJson();
    delete(__profile);
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

    singlePrecision = false;
    switch(__mode){ 
        case APPLYING_STRAT:
            singlePrecision = __profile->applyStrategy(btVec);
            break;
        case PROFILING:
            __profile->applyProfiling(btVec);
            break;
        default:
            cerr << "PrecisionTuner ERROR: no __mode chosen" << endl;
    }
    res = singlePrecision ? (double) fres : dres; 

    DEBUG("fperror", cerr << std::setprecision(16) ; double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " dres=" << dres << " fres=" << fres << " AbsError: " << fabs(fres - dres)<<" RelError: " << relErr << " value=" << value <<endl; else cerr << s << " dres=" << dres<< " value=" << value << endl;);
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return res;
}
