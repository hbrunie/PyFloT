#include <cstdlib>
#include <iostream>
#include "PT_math.h"
using namespace std;
int main(int argc, char * argv[]){
    double a = exp(3.14);
#ifdef V1 // Can lower precision 
    cout << "SUCCESS" << endl;
#else
    cout << "FAILURE" << endl;
#endif
    return 0;
}
