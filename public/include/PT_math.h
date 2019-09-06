#ifndef MYMATH_H
#define MYMATH_H

#ifdef __cplusplus
#include <cmath>
#else
#include <math.h>
#endif
#include<math.h>

double __overloaded_exp(double var);
double __overloaded_log(double var);
double __overloaded_log10(double var);
double __overloaded_cos(double var);
double __overloaded_sin(double var);
double __overloaded_sqrt(double var);
double __overloaded_fabs(double var);
double __overloaded_pow(double var, double p);

// FLOAT exponential function
#ifdef expf
#undef expf
#endif
#define expf __overloaded_expf

// exponential function
#ifdef exp
#undef exp
#endif
#define exp __overloaded_exp

// logarithm function
#ifdef log
#undef log
#endif
#define log __overloaded_log

// logarithm function
#ifdef log10
#undef log10
#endif
#define log10 __overloaded_log10

// cosinus function
#ifdef cos
#undef cos
#endif
#define cos __overloaded_cos

// sinus function
#ifdef sin
#undef sin
#endif
#define sin __overloaded_sin

// power function
#ifdef pow
#undef pow
#endif
#define pow __overloaded_pow

// sqrt function
#ifdef sqrt
#undef sqrt
#endif
#define sqrt __overloaded_sqrt

// fabs function
#ifdef fabs
#undef fabs
#endif
#define fabs __overloaded_fabs
#endif
