#include <cstdlib>
#include <iostream>
#include "PT_math.h"
#define EPSILON 0.0000000001
using namespace std;
int main(int argc, char * argv[]){
    double a = exp(3.141592);
    double refA =23.1406775082637;
    bool success = true;
#ifdef V1 // Can lower precision 
    // can lower both
    cerr << "Can lower precision of all calls " << endl;
#else
    // can not lower any
    cerr << "Can not lower any calls " << endl;
    double err = refA - a;
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
