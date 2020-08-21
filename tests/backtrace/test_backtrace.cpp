#include <chrono>
#include <execinfo.h>
#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>

#include "Backtrace.hpp"
#include "libunwind.h"
#define MAXITE 10000

using namespace std;
using namespace chrono;

int mybacktrace_simple_callback(void * data, uintptr_t pc){
    return 0;
}

int main(int ac, char * av[]){
    steady_clock::time_point start = steady_clock::now();
    int a = 0;
    for(int i=0 ; i<MAXITE; i++){
        a += unwind_symbols();
    }
    steady_clock::time_point stop = steady_clock::now();
    cout << "backtrace_simple loop: " << MAXITE << endl;
    cout << a<< "total time: "<<
        duration_cast<milliseconds> (stop-start).count()<<endl;
    cout << "avg time: "<<
       ((double)duration_cast<milliseconds> (stop-start).count())/ ((double)MAXITE) << endl;

    void * buffer[512];
    start = steady_clock::now();
    for(int j = 0 ; j < MAXITE ; j++){
        a += backtrace(buffer, 512);
    }
    stop = steady_clock::now();
    cout << "backtrace loop: " << MAXITE << endl;
    cout << a << "total time: "<<
        duration_cast<milliseconds> (stop-start).count()<<endl;
    cout << "avg time: "<<
       ((double)duration_cast<milliseconds> (stop-start).count())/ ((double)MAXITE) << endl;

}
