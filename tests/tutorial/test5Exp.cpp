#include <cstdlib>
#include <iostream>
#include "PT_math.h"
#define LOOP 100
using namespace std;
int main(){
    double a;
    for (int i = 0 ; i < LOOP ; i++)
    a = exp(3.14,"exp1");
    for (int i = 0 ; i < LOOP ; i++)
    a = exp(3.14,"exp2");
    for (int i = 0 ; i < LOOP ; i++)
    a = exp(3.14,"exp3");
    for (int i = 0 ; i < LOOP ; i++)
    a = exp(3.14,"exp4");
    for (int i = 0 ; i < LOOP ; i++)
    a = exp(3.14,"exp5");
    cout << "FAILURE: "<< a << endl;
    return 0;
}
