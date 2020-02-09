#include <cstdlib>
#include <iomanip>
#include <iostream>
//#include "PT_math.h"
#include "math.h"
#include <omp.h>
#define LOOP 1000000
using namespace std;

double g(double a, int c){
    if(c%2==0)
        return a * cos(-a)*log10(2*c);
    else
        return a *log(a)*log10(c);
}

double f(double a, int c){
    double b =10.;
    if(c%2==0)
        return fabs(a*cos(a)*b)+c;
    else
        return fabs(g(b,c)*sin(a)*b-c);
}
double refvalue =499999493644.5330200195312500;
#ifdef V1
const double EPSILON = 1E0;
#elif V2
const double EPSILON = 5E-1;
#elif V3
const double EPSILON = 1E-1;
#elif V4
const double EPSILON = 5E-2;
#elif V5
const double EPSILON = 1E-2;
#endif

int main(){
    double * A= new double[LOOP];
    #pragma omp parallel for
    for(int i = 0;i<LOOP;i++)
        A[i] = 0.00001;

    #pragma omp parallel for 
    for(int i = 0;i<LOOP;i++)
        A[i] = f(A[i],i);

    double sum = 0.;
    #pragma omp parallel for shared(A) reduction(+: sum)
    for(int i = 0;i<LOOP;i++)
        sum += A[i];

    double err = refvalue - sum;
    double absErr = err > 0 ? err : -err;
    double relError= absErr / refvalue;
    fprintf(stderr, "EPSILON=%f, reference=%.16f a=%.16f\n",
            EPSILON, refvalue, sum);
    cerr << setprecision(16);
    if(relError < EPSILON)
        cerr << "SUCCESS("<< relError << ")" << endl;
    else
        cerr << "FAILURE("<< relError << ")" << endl;
    delete[] A;
}
