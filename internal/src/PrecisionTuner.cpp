#include <cassert>
#include <cstdlib>
#include <iomanip>
#include <execinfo.h>
#include <math.h>

#include "Debug.hpp"
#include "PrecisionTuner.hpp"

#include <gotcha/gotcha.h>
typedef double (*exp_ptr) (double);

double __overloaded_exp(double var);

gotcha_wrappee_handle_t wrappee_exp_handle;
gotcha_wrappee_handle_t wrappee_expf_handle;
struct gotcha_binding_t wrap_actions [] = {
    { "exp", __overloaded_exp, &wrappee_exp_handle },
    { "expf", __overloaded_exp, &wrappee_expf_handle }
};
using namespace std;

const unsigned int PrecisionTuner::MAXSTACKSIZE         = 500;

// Profiling mode
const string PrecisionTuner::DUMP_JSON_PROFILING_FILE     = "PRECISION_TUNER_DUMPJSONPROFILINGFILE";
const string PrecisionTuner::PRECISION_TUNER_MODE         = "PRECISION_TUNER_MODE";
// Applying strategy mode
const string PrecisionTuner::DUMP_JSON_STRATSRESULTS_FILE     = "PRECISION_TUNER_DUMPJSONSTRATSRESULTSFILE";
const string PrecisionTuner::READ_JSON_PROFILE_STRAT_FILE     = "PRECISION_TUNER_READJSONPROFILESTRATFILE";

PrecisionTuner::PrecisionTuner(){
    /* 2 modes: Profiling, Applying Strategy (AS)
     * if  DUMP_JSON_PROFILING_FILE is set: Profiling mode
     * otherwise AS mode
     */
    char *envVarString=NULL, * envVarString1 = NULL, * envVarString2=NULL;
    fprintf(stderr, "Wrapping %s, %s\n", wrap_actions[0].name, wrap_actions[1].name);
    int res = gotcha_wrap(wrap_actions, 2, "PrecisionTuner");
    fprintf(stderr,"gtcha: %d| %d %d %d %d\n", res,GOTCHA_SUCCESS, GOTCHA_FUNCTION_NOT_FOUND,GOTCHA_INVALID_TOOL,GOTCHA_INTERNAL);
#ifndef NDEBUG
    debugtypeOption(getenv("DEBUG"));
#endif
    envVarString = getenv(PRECISION_TUNER_MODE.c_str());
    if(NULL == envVarString || strlen(envVarString) < 2){
        cerr << "Error: no mode chosen! " << endl;
        exit(-1);
    }
    if(strcmp("APPLYING_STRAT",envVarString) == 0)
        __mode = APPLYING_STRAT;
    else if(strcmp("APPLYING_PROF",envVarString) ==0)
        __mode = APPLYING_PROF;
    else{
        cerr << "Error: no mode chosen! " << endl;
        exit(-1);
    }
    bool checkOk = true;
    if(__mode == APPLYING_PROF){
        cerr << __FUNCTION__ << ": MODE PROFILING" << endl;
        CHECK_NULL(envVarString = getenv(DUMP_JSON_PROFILING_FILE.c_str()),DUMP_JSON_PROFILING_FILE,checkOk);
        if(!checkOk){
            cerr << "Please provide a file for dumping profiling ( *.json)." << endl;
            exit(-1);
        }
        string dumpFile(envVarString);
        __profile = new Profile(true, "None", dumpFile);
    }else{// Applying strategy mode
        cerr << __FUNCTION__ << ": MODE APPLYING_STRAT" << endl;
        CHECK_NULL(envVarString1 = getenv(READ_JSON_PROFILE_STRAT_FILE.c_str()),READ_JSON_PROFILE_STRAT_FILE,checkOk);
        CHECK_NULL(envVarString2 = getenv(DUMP_JSON_STRATSRESULTS_FILE.c_str()), DUMP_JSON_STRATSRESULTS_FILE, checkOk);
        if(!checkOk){
            cerr << "Please provide a file for reading strategy and/or for dumping applying strategy resuts ( *.json)." << endl;
            exit(-1);
        }
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
        double value, double parameter, string label){
    float fvalue, fparameter, fres;
    double dres;

    fvalue = (float)value;
    fparameter = (float)parameter;
#ifndef USE_LABEL
    vector<void*> btVec = __getContextHashBacktrace();
#else
    vector<void*> btVec;
#endif
    fres = (double) sp_func(fvalue, fparameter);
    dres = func(value, parameter);
    return PrecisionTuner::__overloading_function(btVec, s,fres,dres, value, label);
}

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float), double (*func)(double),
        double value, string label){
    double dres;
    float fvalue, fres;
    //float fres;
    UNUSED(sp_func);
    UNUSED(func);

    fvalue = (float)value;

#ifndef USE_LABEL
    vector<void*> btVec = __getContextHashBacktrace();
#else
    UNUSED(label);
    vector<void*> btVec;
#endif
    //TODO: generic wrapper, not just exp (add argument with handler from gotcha?)
    //fres = (double) sp_func(fvalue);
    //dres = func(value);
    double (*wrappee_expf) (double) = gotcha_get_wrappee(wrappee_expf_handle); // get my wrappee from Gotcha
    exp_ptr wrappee_exp = (exp_ptr) gotcha_get_wrappee(wrappee_exp_handle); // get my wrappee from Gotcha
    dres = wrappee_exp(value);
    fres = wrappee_expf(value);
    
    return PrecisionTuner::__overloading_function(btVec, s,fres,dres, value, label);
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

double PrecisionTuner::__overloading_function(vector<void*> &btVec, string s, float fres, double dres,
        double value, string label){
    bool singlePrecision;
    double res;
#ifdef NDEBUG
    UNUSED(s);
    UNUSED(value);
#endif
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);

    singlePrecision = false;
    switch(__mode){
        case APPLYING_STRAT:
            singlePrecision = __profile->applyStrategy(btVec, label);
            break;
        case APPLYING_PROF:
            __profile->applyProfiling(btVec, label);
            break;
        default:
            cerr << "PrecisionTuner ERROR: no __mode chosen" << endl;
    }
    res = singlePrecision ? (double) fres : dres;

    DEBUG("fperrorplus", cerr << std::setprecision(16) ; double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " dres=" << dres << " fres=" << fres << " AbsError: " << fabs(fres - dres)<<" RelError: " << relErr << " value=" << value <<endl; else cerr << s << " dres=" << dres<< " value=" << value << endl;);
    DEBUG("fperror", cerr << std::setprecision(16) ; double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " RelError: " << relErr  <<endl; else cerr << s << " in double precision." << endl;);
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return res;
}
