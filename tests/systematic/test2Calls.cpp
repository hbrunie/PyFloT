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
    double erra = refA - a;
    double errb = refB - b;
    double absErr = 0.;
    double absErra = erra > 0 ? erra : -erra;
    double absErrb = errb > 0 ? errb : -errb;
#ifdef V1 // Can lower precision 
    cerr << "Can lower precision of all calls " << endl;
    absErr = 0.;
#elif V2
    cerr << "Can not lower any calls " << endl;
    absErr = absErra + absErrb;
#elif V3
    cerr << "Can not lower first call " << endl;
    absErr = absErra;
#else
    cerr << "Can not lower second call " << endl;
    absErr = absErrb;
#endif
    if(absErr > EPSILON)
        success = false;
    if(success)
        cout << "SUCCESS" << endl;
    else
        cout << "FAILURE" << endl;
    return 0;
}
