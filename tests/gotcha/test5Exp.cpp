#include <cstdlib>
#include <iostream>
#include "cmath"

#include <PT_Labels.hpp>

#define LOOP 1

using namespace std;
int main(int ac, char * av[]){
    double a;
    setInRegion("main");
    for (int i = 0 ; i < LOOP ; i++)
#ifdef USE_LABEL
    a = exp(atof(av[1]),"exp1");
#else
    a = exp(atof(av[1]));
#endif
    for (int i = 0 ; i < LOOP ; i++)
#ifdef USE_LABEL
    a = exp(atof(av[1]),"exp1");
#else
    a = exp(atof(av[1]));
#endif
    for (int i = 0 ; i < LOOP ; i++)
#ifdef USE_LABEL
    a = exp(atof(av[1]),"exp1");
#else
    a = exp(atof(av[1]));
#endif
    for (int i = 0 ; i < LOOP ; i++)
#ifdef USE_LABEL
    a = exp(atof(av[1]),"exp1");
#else
    a = exp(atof(av[1]));
#endif
    for (int i = 0 ; i < LOOP ; i++)
#ifdef USE_LABEL
    a = exp(atof(av[1]),"exp1");
#else
    a = exp(atof(av[1]));
#endif
    unSetInRegion("main");
    cout << "FAILURE: "<< a << endl;
    return 0;
}
