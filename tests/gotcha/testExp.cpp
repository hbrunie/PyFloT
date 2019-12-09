#include <cstdlib>
#include <iostream>
#include <cmath>

using namespace std;
int main(int ac, char *av[]){
    double a = exp(atof(av[1]));
    cout << "SUCCESS: "<< a << endl;
    return 0;
}
