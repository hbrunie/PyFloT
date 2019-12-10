#include <cstdlib>
#include <iostream>
#include <iomanip>
#include "cmath"

#include <PT_Labels.hpp>

#define LOOP 1
#define EPSILON 0.000000001

using namespace std;
int main(int ac, char * av[]){
    double a;
    double refa = atof(av[1]);
    setInRegion("main");
#ifdef USE_LABEL
    a = exp(refa,"exp1");
#else
    a = exp(refa);
#endif
    a = log(a);
    for (int i = 0 ; i < LOOP ; i++){
#ifdef USE_LABEL
        a = exp(a,"exp1");
#else
        a = exp(a);
#endif
        a = log(a);
    }

    for (int i = 0 ; i < LOOP ; i++){
#ifdef USE_LABEL
        a = exp(a,"exp1");
#else
        a = exp(a);
#endif
        a = log(a);
    }
    for (int i = 0 ; i < LOOP ; i++){
#ifdef USE_LABEL
        a = exp(a,"exp1");
#else
        a = exp(a);
#endif
        a = log(a);
    }
    for (int i = 0 ; i < LOOP ; i++){
#ifdef USE_LABEL
        a = exp(a,"exp1");
#else
        a = exp(a);
#endif
        a = log(a);
    }
    for (int i = 0 ; i < LOOP ; i++){
#ifdef USE_LABEL
        a = exp(a,"exp1");
#else
        a = exp(a);
#endif
        a = log(a);
    }
    unSetInRegion("main");
    cout << setprecision(16);
    if(abs(a - refa) < EPSILON)
        cout << "SUCCESS: "<< a << " ref: "<< refa << endl;
    else
        cout << "FAILURE: "<< a << " ref: "<< refa << endl;
    return 0;
}
