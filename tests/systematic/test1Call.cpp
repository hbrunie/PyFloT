#include <cstdlib>
#include <iostream>
#include <cmath>
#ifdef USE_LABEL
#include "PT_math.h"
#endif
using namespace std;
int main(){
#ifdef USE_LABEL
    double a = exp(3.141592,"uniaue");
#else
    double a = exp(3.141592);
#endif
    double refA =23.1406775082637;
    bool success = true;
    double err = refA - a;
    double absErr = err > 0 ? err : -err;
    double relErr = absErr/refA;
#ifdef V1 // Can lower precision 
    // can lower both
    cerr << "Can lower precision of all calls " << endl;
    const double EPSILON = 0.1;
#else
    // can not lower any
    cerr << "Can not lower any calls " << endl;
    const double EPSILON = 1E-17;
#endif
    if(relErr> EPSILON)
        success = false;
    if(success)
        cout << "SUCCESS" << endl;
    else
        cout << "FAILURE" << endl;
    return 0;
}
