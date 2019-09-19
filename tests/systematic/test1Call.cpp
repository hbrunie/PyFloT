#include <cstdlib>
#include <iostream>
#include "PT_math.h"
using namespace std;
int main(){
    double a = exp(3.141592);
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
    const double EPSILON = 0.0000000001;
#endif
    if(relErr> EPSILON)
        success = false;
    if(success)
        cout << "SUCCESS" << endl;
    else
        cout << "FAILURE" << endl;
    return 0;
}
