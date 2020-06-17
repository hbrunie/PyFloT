#ifndef PrecisionTuner_H
#define PrecisionTuner_H
#include "Profile.hpp"
using namespace std;

#define CHECK_NULL(X, Y) 				\
  do {if(NULL == (X)) {cerr << "Error: " << Y << " == NULL" << endl; \
      cerr << "Please provide a file for reading strategy and/or for dumping applying strategy resuts ( *.json)." << endl; exit(-1);} \
  } while (0)

#define CHECK_POS(X,Y) \
    do { if((X) < 0){cerr << "Error: "<< Y << " < 0" << endl; exit(-1);}\ } while (0)

enum MODE{APPLYING_PROF, APPLYING_STRAT};

struct dgemm_args_s{
    //const CBLAS_LAYOUT Layout;
    //const CBLAS_TRANSPOSE transa;
    //const CBLAS_TRANSPOSE transb;
    const char * transa;
    const char * transb;
    int *m;
    int *n;
    int *k;
    double *alpha;
    double *A;
    int *lda;
    double *B;
    int *ldb;
    double *beta;
    double *C;
    int *ldc;
};

struct sgemm_args_s{
    //const CBLAS_LAYOUT Layout;
    //const CBLAS_TRANSPOSE transa;
    //const CBLAS_TRANSPOSE transb;
    const char * transa;
    const char * transb;
    int *m;
    int *n;
    int *k;
    float *alpha;
    float *A;
    int *lda;
    float *B;
    int *ldb;
    float *beta;
    float *C;
    int *ldc;
};

class PrecisionTuner
{
    private:
        enum MODE __mode;
        void checkPrecisionTunerMode();
        /* Profiling */
        Profile *     __profile;
        double        __overloading_function(vector<void*> &btVec, string s, float fres,
                                 double dres, double value, string label, double timeStamp);
        vector<void*> __getContextHashBacktrace();
        /* TimeStamp computation */
        double getTimeStamp();
        void   initTSClock();

        static const unsigned int MAXSTACKSIZE;
        /* JSON values and sections keys */
        // Number of independant call stacks
        static const string JSON_TOTALCALLSTACKS_KEY;
        static const string PRECISION_TUNER_MODE;

    public:
        PrecisionTuner();
        ~PrecisionTuner();
        void overloading_function(string s, float (*sp_func) (float), double (*func)(double),
                struct dgemm_args_s dgemm_args, struct sgemm_args_s sgemm_args, string label);
};
#endif // PrecisionTuner_H
