#include <cstdlib>
#include <iostream>
#include <iomanip>
#include "cmath"

#define LOOP 1
#define EPSILON 0.000000001

using namespace std;
int main(int ac, char * av[]){
    double a;
    double refa = atof(av[1]);
    a = expf(refa);
    a = log(a);
    for (int i = 0 ; i < LOOP ; i++){
        a = expf(a);
        a = log(a);
    }

    for (int i = 0 ; i < LOOP ; i++){
        a = expf(a);
        a = log(a);
    }
    for (int i = 0 ; i < LOOP ; i++){
        a = expf(a);
        a = log(a);
    }
    for (int i = 0 ; i < LOOP ; i++){
        a = expf(a);
        a = log(a);
    }
    for (int i = 0 ; i < LOOP ; i++){
        a = expf(a);
        a = log(a);
    }
    cout << setprecision(16);
    if(abs(a - refa) < EPSILON)
        cout << "SUCCESS: "<< a << " ref: "<< refa << endl;
    else
        cout << "FAILURE: "<< a << " ref: "<< refa << endl;
    return 0;
}
