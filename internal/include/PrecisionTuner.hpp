#ifndef PrecisionTuner_H
#define PrecisionTuner_H
#include "Profile.hpp"
using namespace std;

#define CHECK_NULL(X, Y, Z) 				\
  do {if(NULL == (X)) {cerr << "Error: " << Y << " == NULL" << endl; Z = false;} \
  } while (0)

enum MODE{APPLYING_PROF, APPLYING_STRAT};


class PrecisionTuner
{
    private:
        enum MODE __mode;
        /* Profiling */
        Profile * __profile;
        double __overloading_function(vector<void*> &btVec, string s, float fres, double dres, double value, string label);
        vector<void*> __getContextHashBacktrace();

        static const unsigned int MAXSTACKSIZE;
        /* JSON values and sections keys */
        // Number of independant call stacks
        static const string JSON_TOTALCALLSTACKS_KEY;
        static const string PRECISION_TUNER_MODE;
        // JSON FILE ENV VARS
        static const string DUMP_JSON_PROFILING_FILE;
        static const string DUMP_JSON_STRATSRESULTS_FILE;
        static const string READ_JSON_PROFILE_STRAT_FILE;

    public:
        PrecisionTuner();
        ~PrecisionTuner();
        double overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
                double value, double parameter, string label);
        double overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value, string label);
};
#endif // PrecisionTuner_H
