#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <cmath>
#define EPSILON 1e-8
#define FACT1 1./1.
#define FACT2 1./2./FACT1
#define FACT3 1./3./FACT2
#define FACT4 1./4./FACT3
#define FACT5 1./5./FACT4
#define FACT6 1./6./FACT5
#define FACT7 1./7./FACT6
#define FACT8 1./8./FACT7
#define FACT9 1./9./FACT8
#define FACT10 1./10./FACT9

#define TWO seed*seed
#define THREE seed*TWO
#define FOUR TWO*TWO
#define FIVE TWO*THREE
#define SIX THREE*THREE
#define SEVEN THREE*FOUR
#define HEIGHT FOUR*FOUR
#define NINE FIVE*FOUR
#define TEN FIVE*FIVE
using namespace std;
int main(int ac, char * av[]){
    srand((unsigned int )NULL);
    double seed = (double)(rand())/(double)RAND_MAX;
    double expApprox = 1+seed + TWO/FACT2 + THREE/FACT3 + FOUR/FACT4 + FIVE/FACT5 + SIX/FACT6 + SEVEN/FACT7 + HEIGHT/FACT8 + NINE/FACT9 + TEN/FACT10;
    //float printedResult = exp((float)seed);
    //double printedResult = exp((float)seed);
    double printedResult = exp(seed);
    cerr << setprecision(16) ;
    cerr <<"seed: "<< seed << endl;
    cerr <<"expApprox: "<< expApprox << endl;
    cerr <<"printedResult: "<< printedResult << endl;
    //if result not correct enough, take a new path
    double diff = abs(expApprox-printedResult) ;
    double relDiff = diff/expApprox ;
    cerr << "Diff: " << diff <<endl;
    cerr << "RelDiff: " << relDiff <<endl;
    cerr << "epsilon: " << EPSILON <<endl;
    if(relDiff < EPSILON)
        cout << "SUCCESS" << endl;
    else{
        printedResult += exp(seed+seed);
        cout << "FAILURE: "<< printedResult << endl;
    }
    return 0;
}
