#include <cstdlib>
#include <iostream>
#include "PT_math.h"
#define LOOP 10
using namespace std;
int main(){
    double a=0.0;
    for (int i = 0; i<LOOP;i++) {
        a += exp(3.141592);
    }
    double refA =231.406775082637;
    double err = refA - a;
    double absErr = err > 0 ? err : -err;
    cerr << absErr << endl;
    bool success = true;
#ifdef V1 // Can lower precision 
    // can lower both
    cerr << "Can lower precision of all calls " << endl;
#elif V2
    // can not lower any 
    const double EPSILON = 1E-10;
    cerr << "Can not lower any calls " << endl;
    if(absErr > EPSILON)
        success = false;
#elif V3
    // can lower some
    const double EPSILON=5E-6;
    cerr << "Can lower some calls? "<< EPSILON << endl;
    if(absErr > EPSILON)
        success = false;
#elif V4
    // can lower some
    cerr << "Can lower some calls? "<< 4E-6 << endl;
    if(absErr > 4E-6)
        success = false;
#elif V5
    // can lower some
    const double EPSILON=3E-6;
    cerr << "Can lower some calls? "<< EPSILON << endl;
    if(absErr > EPSILON)
        success = false;
#else
    // can lower some
    const double EPSILON=1E-6;
    cerr << "Can lower some calls? "<< EPSILON << endl;
    if(absErr > EPSILON)
        success = false;
#endif
    if(success)
        cout << "SUCCESS" << endl;
    else
        cout << "FAILURE" << endl;
    return 0;
}
