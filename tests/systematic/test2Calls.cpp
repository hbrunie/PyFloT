#include <cstdlib>
#include <iostream>
#include <iomanip>
#include "PT_math.h"
using namespace std;
int main(){
    bool success = true;
    double relErr = 0.;
    double b = exp(0.0000014);
    double refB =1.00000140000098;
    double errb = refB - b;
    double absErrb = errb > 0 ? errb : -errb;
    double relErrorB = absErrb / refB;
    double a = exp(3.141592);
    double refA =23.1406775082637;
    double erra = refA - a;
    double absErra = erra > 0 ? erra : -erra;
    double relErrorA = absErra / refA;

#ifdef V1 // Can lower precision 
    cerr << "Can lower precision of all calls " << endl;
    relErr = relErrorA + relErrorB;
    const double EPSILON = 1.;
#elif V2
    cerr << "Can not lower any calls " << endl;
    relErr = relErrorA + relErrorB;
    const double EPSILON = 0.0000000001;
#elif V3
    cerr << "Can not lower first call (no use of " << relErrorB << ")" << endl;
    relErr = relErrorA;
    const double EPSILON = 0.000000001;
#elif V4
    cerr << "Can not lower second call (no use of " << relErrorA << ")" << endl;
    relErr = relErrorB;
    const double EPSILON = 0.0000000001;
#endif
    cerr << "RelError: " << relErr  << endl;
    cerr << "EPSILON: " << EPSILON << endl;
    if(relErr > EPSILON)
        success = false;
    if(success)
        cout << "SUCCESS" << endl;
    else
        cout << "FAILURE" << endl;
    return 0;
}
