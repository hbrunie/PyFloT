#include <alloca.h>
#include <assert.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <limits.h>
#include <math.h>
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

static PrecisionTuner ptuner;

/******** Function definitions **********/


/* *** Overloading functions *** */

// TODO: use templated function, change the PT_math.h accordingly
/* exponential function */
double __overloaded_exp(double var) {
    string label = "noLabel";
    return ptuner.overloading_function("exp",expf,exp,var, label);
}
double __overloaded_exp(double var, string label) {
    return ptuner.overloading_function("exp",expf,exp,var, label);
}

/* logarithm function */
double __overloaded_log(double var) {
    string label = "noLabel";
    return ptuner.overloading_function("log",logf, log,var, label);
}
double __overloaded_log(double var, string label) {
    return ptuner.overloading_function("log",logf, log,var, label);
}

/* logarithm function */
double __overloaded_log10(double var) {
    string label = "noLabel";
    return ptuner.overloading_function("log10", log10f, log10,var, label);
}
double __overloaded_log10(double var, string label) {
    return ptuner.overloading_function("log10", log10f, log10,var, label);
}

/* cosinus function */
double __overloaded_cos(double var) {
    string label = "noLabel";
    return ptuner.overloading_function("cos", cosf,cos,var, label);
}
double __overloaded_cos(double var, string label) {
    return ptuner.overloading_function("cos", cosf,cos,var, label);
}

/* sinus function */
double __overloaded_sin(double var) {
    string label = "noLabel";
    return ptuner.overloading_function("sin", sinf,sin,var, label);
}
double __overloaded_sin(double var, string label) {
    return ptuner.overloading_function("sin", sinf,sin,var, label);
}

/* sqrt function */
double __overloaded_sqrt(double var) {
    string label = "noLabel";
    return ptuner.overloading_function("sqrt",sqrtf,sqrt,var, label);
}
double __overloaded_sqrt(double var, string label) {
    return ptuner.overloading_function("sqrt",sqrtf,sqrt,var, label);
}

/* fabs function */
double __overloaded_fabs(double var) {
    string label = "noLabel";
    return ptuner.overloading_function("Fabs", fabs,fabs,var, label);
}
double __overloaded_fabs(double var, string label) {
    return ptuner.overloading_function("Fabs", fabs,fabs,var, label);
}

/* power function */
double __overloaded_pow(double var, double p) {
    string label = "noLabel";
    return ptuner.overloading_function("Pow",powf,pow,var,p, label);
}
double __overloaded_pow(double var, double p, string label) {
    return ptuner.overloading_function("Pow",powf,pow,var,p, label);
}
