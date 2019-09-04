#include <alloca.h>
#include <assert.h>
//#include <bits/stdc++.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits.h>
#include <sstream>

#include <dlfcn.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>

#include "PrecisionTuner.hpp"

using namespace std;

static string JSONFILE = "Users/hbrunie/Codes/output.json";

/******** Globals variables **********/

static unsigned long int TOTAL_CALL_STACKS = 0;
static PrecisionTuner ptuner;

/******** Function definitions **********/


/* *** Overloading functions *** */

// TODO: use templated function, change the PT_math.h accordingly
/* exponential function */
double __overloaded_exp(double var) {
    return ptuner.overloading_function("exp",expf,exp,var);
}

/* logarithm function */
double __overloaded_log(double var) {
    return ptuner.overloading_function("log",logf, log,var);
}

/* logarithm function */
double __overloaded_log10(double var) {
    return ptuner.overloading_function("log10", log10f, log10,var);
}

/* cosinus function */
double __overloaded_cos(double var) {
    return ptuner.overloading_function("cos", cosf,cos,var);
}

/* sinus function */
double __overloaded_sin(double var) {
    return ptuner.overloading_function("sin", sinf,sin,var);
}

/* sqrt function */
double __overloaded_sqrt(double var) {
    return ptuner.overloading_function("sqrt",sqrtf,sqrt,var);
}

/* fabs function */
double __overloaded_fabs(double var) {
    return ptuner.overloading_function("Fabs", fabs,fabs,var);
}

/* power function */
double __overloaded_pow(double var, double p) {
    return ptuner.overloading_function("Pow",powf,pow,var,p);
}
