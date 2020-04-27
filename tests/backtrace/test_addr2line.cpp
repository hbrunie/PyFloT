#include <chrono>
#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <execinfo.h>
#include <iostream>

#include "Backtrace.hpp"
#define MAXITE 10

using namespace std;
using namespace chrono;

void testBacktrace(char *exe){
    void * buffer[BACKTRACE_MAX];
    const int size = backtrace(buffer, BACKTRACE_MAX);
    char ** symbols = backtrace_symbols(buffer, size);

    steady_clock::time_point start = steady_clock::now();
    for (int j = 0; j < MAXITE; j++){
        for (int i = 0; i < size; i++){
            cerr << addr2lineBacktrace(exe,string(symbols[i])) << endl;
        }
    }
    steady_clock::time_point stop = steady_clock::now();
    cout << "loop1: " << MAXITE << "; loop2: " << size <<endl;
    cout << "addr2line." << endl;
    cout << "total time: "<<
        duration_cast<milliseconds> (stop-start).count()<<endl;
    cout << "avg time: "<<
       ((double)duration_cast<milliseconds> (stop-start).count())/ ((double)MAXITE) << endl;

    start = steady_clock::now();
    for(int j = 0 ; j < MAXITE ; j++){
        vector<string> symbolsVec;
        for (int i = 0; i < size; i++){
            symbolsVec.push_back(symbols[i]);
        }
        vector<string> strVec = addr2lineBacktraceVec(exe, symbolsVec, size);
        for (auto it = strVec.begin() ; it != strVec.end() ; it++)
            cerr << *it << endl;
    }
    stop = steady_clock::now();
    cout << "loop1: " << MAXITE << "; loop2: " << size << "; symbolsVec.push_back" << endl;
    cout << MAXITE << " addr2line." << endl;
    cout << "total time: "<<
        duration_cast<milliseconds> (stop-start).count()<<endl;
    cout << "avg time: "<<
       ((double)duration_cast<milliseconds> (stop-start).count())/ ((double)MAXITE) << endl;

    start = steady_clock::now();
    for (int k=0 ; k< MAXITE; k++){
        vector<string> longsymbolsVec;
        for(int j = 0 ; j < MAXITE ; j++){
            for (int i = 0; i < size; i++){
                longsymbolsVec.push_back(symbols[i]);
            }
        }
        vector<string> longstrVec = addr2lineBacktraceVec(exe, longsymbolsVec, size*MAXITE);
        for (auto it = longstrVec.begin() ; it != longstrVec.end() ; it++)
            cerr << *it << endl;
    }
    stop = steady_clock::now();
    cout << "loop1: " << MAXITE << "; loop2: " << size << "; longsymbolsVec.push_back"<< endl;
    cout << "1 unique addr2line on long vector."<< MAXITE << " times." << endl;
    cout << "total time: "<<
        duration_cast<milliseconds> (stop-start).count()<<endl;
    cout << "avg time: "<<
       ((double)duration_cast<milliseconds> (stop-start).count())/ ((double)MAXITE) << endl;
}

int main(int ac, char * av[]){
    testBacktrace(av[0]);
    cout << "CONCLUSION: addr2line execution time is constant with size of argument vector. Always aroun ~9ms.--> do all the conversion in one call if possible."<<endl;
}
