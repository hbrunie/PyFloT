#include <cstdlib>
#include <iostream>
#include "PT_math.h"
//#include "math.h"
#define LOOP 1000000
using namespace std;

double g(double a, int c){
    if(c/2==0)
#ifdef USE_LABEL
        a = a * cos(-a,"cosg");
#else
        a = a * cos(-a);
#endif
    else
#ifdef USE_LABEL
        a = a *log(a,"log");
#else
        a = a *log(a);
#endif
    return a;
}

double f(double a, int c){
    double b =10.;
    if(c%2==1)
#ifdef USE_LABEL
        b = a*cos(a,"cosf")*b;
#else
        b = a*cos(a)*b;
#endif
    else
#ifdef USE_LABEL
        b = g(b,c)*sin(a,"sin")*b;
#else
        b = g(b,c)*sin(a)*b;
#endif
#ifdef USE_LABEL
    b = fabs(b,"fabs");
#else
    b = fabs(b);
#endif
    return b;
}

double refvalue = 905.7020870020163557;
#ifdef V1
const double EPSILON = 1E0;
#elif V2
const double EPSILON = 5E-1;
#elif V3
const double EPSILON = 1E-1;
#elif V4
const double EPSILON = 5E-2;
#elif V5
const double EPSILON = 1E-2;
#endif

int main(){
    double a = 0.00001;
#ifdef USE_LABEL
    a = a * exp(a+0.0005,"main");
#else
    a = a * exp(a+0.0005);
#endif
    a = f(a,0);
    for(int i = 0;i<LOOP;i++)
        a = f(a,i);
    double err = refvalue - a;
    double absErr = err > 0 ? err : -err;
    double relError= absErr / refvalue;
    fprintf(stderr, "EPSILON=%f, reference=%.16f a=%.16f\n",
            EPSILON, refvalue, a);
    if(relError < EPSILON)
        fprintf(stderr, "SUCCESS(%f)\n",relError);
    else
        fprintf(stderr, "FAILURE(%f)\n",relError);
}
