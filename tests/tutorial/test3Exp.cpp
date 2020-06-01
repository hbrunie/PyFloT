#include <cstdlib>
#include <iostream>
#include <math.h>
#define LOOP 3
using namespace std;
double f(double b){
    return 10+ exp(b);
}
double g(double b){
    return 10+f(b)+ exp(b);
}
int main(int ac, char *av[]){
    /* Dummy example accepting to do single precision for all exp calls */
    double a;
    for (int i = 0 ; i < LOOP+1 ; i++)
    a += exp(i%4);
    for (int i = 0 ; i < LOOP-1 ; i++)
    a += f(i%4);
    for (int i = 0 ; i < LOOP ; i++)
    a += g(i%4);
    cout << "SUCCESS: "<< a << endl;
    return 0;
}
