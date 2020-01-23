#include <cassert>
#include <cstdlib>
#include <iomanip>
#include <execinfo.h>
#include <math.h>

#include "Debug.hpp"
#include "PrecisionTuner.hpp"
#include "ShadowValue.hpp"
#include "Utils.hpp"

#include <gotcha/gotcha.h>
typedef double (*exp_ptr) (double);
typedef float (*expf_ptr) (float);

double __overloaded_exp(double var);

gotcha_wrappee_handle_t wrappee_exp_handle;
gotcha_wrappee_handle_t wrappee_expf_handle;

struct gotcha_binding_t wrap_actions [] = {
    { "exp", (void*)__overloaded_exp, &wrappee_exp_handle },
    { "expf", (void*)__overloaded_exp, &wrappee_expf_handle }
};

using namespace std;

const unsigned int PrecisionTuner::MAXSTACKSIZE   = 500;
const string PrecisionTuner::PRECISION_TUNER_MODE = "PRECISION_TUNER_MODE";

void PrecisionTuner::checkPrecisionTunerMode(){
    char * envVarString = getenv(PRECISION_TUNER_MODE.c_str());
    __mode = APPLYING_PROF;
    if((NULL != envVarString)
       && (strcmp("APPLYING_STRAT",envVarString) == 0))
        __mode = APPLYING_STRAT;
}

PrecisionTuner::PrecisionTuner(){
#ifndef NDEBUG
    debugtypeOption(getenv("DEBUG"));
#endif
    CHECK_POS(gotcha_wrap(wrap_actions, 2, "PrecisionTuner"), "gotcha_wrap");
    checkPrecisionTunerMode();
    __profile  = new Profile(__mode == APPLYING_STRAT);
}

static long long __totalReduced = 0;
static long long total = 0;
PrecisionTuner::~PrecisionTuner(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    DEBUG("infoplus",cerr << __FUNCTION__ << __mode << endl;);
    cerr << "RATIO REDUCED: " << (double)__totalReduced / (double)total << endl;
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

bool __specificRegion = false;
void PTunerEnterSpecificRegion(){
    __specificRegion=true;
}

void unsetNO(){
    __specificRegion = false;
}

double PrecisionTuner::overloading_function(string s, float (*sp_func) (float), double (*func)(double),
        double value, string label){
    double dres;
    float fvalue, fres;
    UNUSED(sp_func);
    UNUSED(fvalue);
    UNUSED(func);

    fvalue = (float)value;

#ifndef USE_LABEL
    vector<void*> btVec = __getContextHashBacktrace();
#else
    UNUSED(label);
    vector<void*> btVec;
#endif
    //TODO: generic wrapper, not just exp (add argument with handler from gotcha?)
    total ++;
    exp_ptr wrappee_exp = (exp_ptr) gotcha_get_wrappee(wrappee_exp_handle); // get my wrappee from Gotcha
    dres = wrappee_exp(value);

    expf_ptr wrappee_expf = (expf_ptr) gotcha_get_wrappee(wrappee_expf_handle); // get my wrappee from Gotcha
    fres = wrappee_expf(value);
    DEBUG("debug", cerr << __FUNCTION__
            <<": exp " << dres
            <<" expf " << fres
            << " s(" <<s << ") "
            << "label (" << label << ")"
            <<endl;);
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
    DEBUGINFO("ENDING");
    return btVec;
}

double PrecisionTuner::__overloading_function(vector<void*> &btVec, string s, float fres, double dres,
        double value, string label){
    bool singlePrecision, singlePrecisionProfiling;
    double res;
#ifdef NDEBUG
    UNUSED(s);
    UNUSED(value);
#endif
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    singlePrecisionProfiling = false;
    singlePrecision = false;
    switch(__mode){
        case APPLYING_STRAT:
            singlePrecision = __profile->applyStrategy(btVec, label);
            break;
        case APPLYING_PROF:
            // TODO: make it more generic
            // PeleC everything in lower but specific region (compKc)
            singlePrecisionProfiling = __specificRegion ? false : true;
            if(singlePrecisionProfiling)
                __totalReduced += 1;
            ShadowValue shadowValue(fres, dres, value, singlePrecisionProfiling);
            __profile->applyProfiling(btVec, label, shadowValue);
            break;
        default:
            cerr << "PrecisionTuner ERROR: no __mode chosen" << endl;
    }
    res = singlePrecision ? (double) fres : dres;
    DEBUG("fperror", cerr << "SINGLE precision? " << singlePrecision << endl; );
    DEBUG("fperrorplus", cerr << std::setprecision(16) ; double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " dres=" << dres << " fres=" << fres << " AbsError: " << fabs(fres - dres)<<" RelError: " << relErr << " value=" << value <<endl; else cerr << s << " dres=" << dres<< " value=" << value << endl;);
    DEBUG("fperror", cerr << std::setprecision(16) ; double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " RelError: " << relErr  <<endl; else cerr << s << " in double precision." << endl;);
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return res;
}
