#include <cstdlib>
#include <iostream>
#include "cmath"

#define LOOP 100000

using namespace std;
int main(int ac, char * av[]){
    double a;
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
    cout << "FAILURE: "<< a << endl;
    return 0;
}
