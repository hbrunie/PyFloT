#include <cstdlib>
#include <iostream>
#include <iomanip>
#include "PT_math.h"
#define EPSILON 0.0000000001
using namespace std;
int main(int argc, char * argv[]){
    double a = exp(3.141592);
    double b = exp(0.0000014);
    double refA =23.1406775082637;
    double refB =1.00000140000098;
    bool success = true;
#ifdef V1 // Can lower precision 
    // can lower both
    cerr << "Can lower precision of all calls " << endl;
#elif V2
    // can not lower any
    cerr << "Can not lower any calls " << endl;
    double err = refA - a;
    double absErr = err > 0 ? err : -err;
    if(absErr > EPSILON)
        success = false;
    // can not lower second
    err = refB - b;
    absErr = err > 0 ? err : -err;
    if(absErr > EPSILON)
        success = false;
#elif V3
    // can not lower first
    cerr << "Can not lower first call " << endl;
    double err = refA - a;
    double absErr = err > 0 ? err : -err;
    if(absErr > EPSILON)
        success = false;
#else
    // can not lower second
    cerr << "Can not lower second call " << endl;
    double err = refB - b;
    double absErr = err > 0 ? err : -err;
    if(absErr > EPSILON)
        success = false;
#endif
    if(success)
        cout << "SUCCESS" << endl;
    else
        cout << "FAILURE" << endl;
    return 0;
}
