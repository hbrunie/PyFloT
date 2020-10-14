#include <cassert>
#include <chrono>
#include <cstdlib>
#include <execinfo.h>
#include <iomanip>
#include <iostream>
#include <cmath>
#ifdef USE_INTEL_COMPILER
#include <mkl.h>
#else
//Use Cray compiler on Cori
#include <cblas.h>
#endif

using namespace std;
using namespace chrono;

#include "Debug.hpp"
#include "PrecisionTuner.hpp"
#include "ShadowValue.hpp"
#include "Utils.hpp"

#ifdef USE_GOTCHA
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
#endif

typedef void (*dgemm_ptr) (char const *transa, char const *transb, int* m, int* n, int* k,
                        double* alpha, double *A, int* lda, double *B, int* ldb,
                        double* beta, double *C, int* ldc);
typedef void (*sgemm_ptr) (char const *transa, char const *transb, int* m, int* n, int* k,
                        float* alpha, float *A, int* lda, float *B, int* ldb,
                        float* beta, float *C, int* ldc);

extern "C"{
  double dnrm2_(size_t,double*, int);
  void dgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
              double *alpha, double *A, int *lda, double *B, int *ldb,
              double *beta, double *C, int *ldc);
  void sgemm_(char const *transa, char const *transb, int *m, int *n, int *k,
              float *alpha, float *A, int *lda, float *B, int *ldb, float *beta,
              float *C, int *ldc);

}

const unsigned int PrecisionTuner::MAXSTACKSIZE   = 1024;
const string PrecisionTuner::PRECISION_TUNER_MODE = "PRECISION_TUNER_MODE";

void PrecisionTuner::checkPrecisionTunerMode(){
    char * envVarString = getenv(PRECISION_TUNER_MODE.c_str());
    __mode = APPLYING_PROF;
    if((NULL != envVarString)
            && (strcmp("APPLYING_STRAT",envVarString) == 0))
        __mode = APPLYING_STRAT;
    DEBUG("info",cerr << "ENDING" << __FUNCTION__ << endl;);
}

PrecisionTuner::PrecisionTuner(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    initTSClock();
    checkPrecisionTunerMode();
    __profile  = new Profile(__mode == APPLYING_STRAT);
}

PrecisionTuner::~PrecisionTuner(){
#ifndef NDEBUG
    // Otherwise segfault in Debug.cpp because CurrentDebugType is no longer in memory.
    Debug debug;
#endif
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    DEBUG("infoplus",cerr << __FUNCTION__ << __mode << endl;);
#ifdef DUMP
    __profile->dumpJsonPlusCSV();
#endif
    delete(__profile);
}

/* Timeserie builder function(s) */
steady_clock::time_point __startTS;
void PrecisionTuner::initTSClock(){
     __startTS = steady_clock::now();
}

/* Returns timeStamp (double) in milliseconds */
double PrecisionTuner::getTimeStamp(){
    double r;
    long int dur;
    steady_clock::time_point stop = steady_clock::now();
    dur = duration_cast<nanoseconds> (stop - __startTS).count();
    r = ((double) dur) / 1000.;
    return r;
}

#ifndef NDEBUG
static bool once = true;
#endif

#ifdef USE_GOTCHA
/* Intercept math function with 1 arguments math library function calls */
double PrecisionTuner::overloading_function(string s, float (*sp_func) (float), double (*func)(double),
        double value, string label){
#ifndef NDEBUG
    if (once)
        debugtypeOption(getenv("DEBUG"));
    once = false;
#endif
    double dres;
    float fvalue, fres;
    UNUSED(sp_func);
    UNUSED(fvalue);
    UNUSED(func);

    fvalue = (float)value;
#ifndef USE_TIMESTAMP
    double timeStamp = 0.0;
#else
    double timeStamp = getTimeStamp();
#endif

#ifndef USE_LABEL
    vector<void*> btVec = __getContextHashBacktrace();
#else
    UNUSED(label);
    vector<void*> btVec;
#endif
    //CBLAS_LAYOUT Layout = args.Layout;
    //const CBLAS_TRANSPOSE transa = args.transa;
    //const CBLAS_TRANSPOSE transb = args.transb;
    const char *transa = args.transa;
    const char *transb = args.transb;
    int*m = args.m;
    int*n = args.n;
    int*k = args.k;
    double *alpha = args.alpha;
    double *A = args.A;
    int *lda = args.lda;
    double *B = args.B;
    int *ldb = args.ldb;
    double *beta = args.beta;
    double *C = args.C;
    int *ldc = args.ldc;
    dgemm_(transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc);//return void

    int sizeA = (*m) * (*k);
    int sizeB = (*k) * (*n);
    int sizeC = (*m) * (*n);

    float alphaf = (float)*alpha;
    float betaf  = (float)*beta;
    float *alphaf_p = &alphaf;
    float *betaf_p  = &betaf;
    float *Af     = (float*) malloc(sizeof(float) * sizeA);
    float *Bf     = (float*) malloc(sizeof(float) * sizeB);
    float *Cf     = (float*) malloc(sizeof(float) * sizeC);
    double *Cf_dp     = (double*) malloc(sizeof(double) * sizeC);


    for(int i = 0; i < sizeA; i++)
        Af[i] = (float) A[i];
    for(int i = 0; i < sizeB; i++)
        Bf[i] = (float) B[i];
    for(int i = 0; i < sizeC; i++)
        Cf[i] = (float) 0.;

    sgemm_(transa, transb, m, n, k, alphaf_p, Af, lda, Bf, ldb, betaf_p, Cf, ldc);//return void
    for(int i = 0; i < sizeC; i++)
        Cf_dp[i] = (double) Cf[i];

    double dres =0.,fres=0.; // Norm of matrices
    dres = cblas_dnrm2(sizeC, C, 1);
    for(int i=0; i<sizeC ; i++)
        cerr << C[i] << " ";
    fres = cblas_dnrm2(sizeC, Cf_dp, 1);
    for(int i=0; i<sizeC ; i++)
        cerr << Cf_dp[i] << " ";
    free(Af);
    free(Bf);
    free(Cf);
    free(Cf_dp);

    DEBUG("debug", cerr << __FUNCTION__
            <<": dgemm " << dres
            <<" sgemm " << fres
            << " s(" <<s << ") "
            << "label (" << label << ")"
            <<endl;);
    PrecisionTuner::__overloading_function(btVec, s,fres,dres, 0.0, label, timeStamp);
}

#else
/* Intercept math function with 1 arguments */
void PrecisionTuner::overloading_function(string s, struct dgemm_args_s args,
                                             struct sgemm_args_s args_s, string label){
#ifndef USE_TIMESTAMP
    double timeStamp = 0.0;
#else
    double timeStamp = getTimeStamp();
#endif

#ifndef USE_LABEL
    vector<void*> btVec = __getContextHashBacktrace();
#else
    UNUSED(label);
    vector<void*> btVec;
#endif
    const char *transa = args.transa;
    const char *transb = args.transb;
    int*m = args.m;
    int*n = args.n;
    int*k = args.k;
    double *alpha = args.alpha;
    double *A = args.A;
    int *lda = args.lda;
    double *B = args.B;
    int *ldb = args.ldb;
    double *beta = args.beta;
    double *C = args.C;
    int *ldc = args.ldc;

    for(int i=0;i<*m * *n;i++)
        C[i]=0.;
    // Column MAJOR
    dgemm_(transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc);//return void
    double dres = cblas_dnrm2(*m * *n, C, 1);
    int sizeA = (*m) * (*k);
    int sizeB = (*k) * (*n);
    int sizeC = (*m) * (*n);

    float alphaf = (float)*alpha;
    float betaf  = (float)*beta;
    float *alphaf_p = &alphaf;
    float *betaf_p  = &betaf;
    //TODO: DEBUG
    float *Af     = (float*)  aligned_alloc(64, sizeof(float) * sizeA);
    float *Bf     = (float*)  aligned_alloc(64, sizeof(float) * sizeB);
    float *Cf     = (float*)  aligned_alloc(64, sizeof(float) * sizeC);
    double *Cf_dp = (double*) aligned_alloc(64, sizeof(double) * sizeC);


    for(int i = 0; i < sizeA; i++)
        Af[i] = (float) A[i];
    for(int i = 0; i < sizeB; i++)
        Bf[i] =  (float)B[i];
    for(int i = 0; i < sizeC; i++)
        Cf[i] =  0.;

    // Column MAJOR
    int sgemm_lda = *m;
    int sgemm_ldb = *k;
    int sgemm_ldc = *m;
    if((*transa) == 't'
            || (*transa) ==  CblasTrans
            || (*transa) == CblasConjTrans)
            sgemm_lda = *k;
    if((*transb) == 't'
            || (*transb) ==  CblasTrans
            || (*transb) ==CblasConjTrans)
            sgemm_ldb = *n;
    sgemm_(transa, transb, m, n, k, alphaf_p, Af, &sgemm_lda, Bf, &sgemm_ldb, betaf_p, Cf, &sgemm_ldc);//return void
    for(int i = 0; i < sizeC; i++)
        Cf_dp[i] = (double) Cf[i];

    double fres = cblas_dnrm2(*m * *n, Cf_dp, 1);
    double relErr = fabs(fres-dres)/dres;
    for(int i = 0; i < sizeC; i++)
        C[i] = Cf[i];
    free(Af);
    free(Bf);
    free(Cf);
    free(Cf_dp);

    DEBUG("debug", cerr << __FUNCTION__
            <<": dgemm " << dres
            <<" sgemm " << fres
            << " s(" <<s << ") "
            << "label (" << label << ")"
            <<endl;);
    PrecisionTuner::__overloading_function(btVec, s,fres,dres, 0.0, label, timeStamp);
}
#endif

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

double PrecisionTuner::__overloading_function(vector<void*> &btVec, string s,
        float fres, double dres, double value, string label, double timeStamp){
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
            {
                ShadowValue shadowValue(fres, dres, 0.0, singlePrecisionProfiling, timeStamp);
                __profile->applyProfiling(btVec, label, shadowValue);
            }
            break;
        default:
            {
                cerr << "PrecisionTuner ERROR: no __mode chosen" << endl;
                exit(-1);
            }
            break;
    }
    res = singlePrecision ? (double) fres : dres;
    DEBUG("fperror", cerr << "SINGLE precision? " << singlePrecision << endl; );
    DEBUG("fperrorplus", cerr << std::setprecision(16) ; double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " dres=" << dres << " fres=" << fres << " AbsError: " << fabs(fres - dres)<<" RelError: " << relErr << " value=" << value <<endl; else cerr << s << " dres=" << dres<< " value=" << value << endl;);
    DEBUG("fperror", cerr << std::setprecision(16) ; double relErr = fabs(fres - dres) / fabs(dres); if(singlePrecision)  cerr << s << " RelError: " << relErr  <<endl; else cerr << s << " in double precision." << endl;);
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return res;
}
