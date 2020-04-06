#include <execinfo.h>
#include <string.h>
#include <stdlib.h>
#include <iostream>

#include "Backtrace.hpp"
using namespace std;

void testBacktrace(char *exe){
    void * buffer[BACKTRACE_MAX];
    const int size = backtrace(buffer, BACKTRACE_MAX);
    char ** symbols = backtrace_symbols(buffer, size);

    for (int i = 0; i < size; i++){
        cerr << symbols[i] << endl;
        cerr << addr2lineBacktrace(exe,string(symbols[i])) << endl;
    }
    vector<string> strVec = addr2lineBacktraceVec(exe, symbols, size);
    for (auto it = strVec.begin() ; it != strVec.end() ; it++)
        cerr << *it << endl;
}

int main(int ac, char * av[]){
    testBacktrace(av[0]);
}
