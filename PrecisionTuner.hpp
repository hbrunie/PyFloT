#include <bits/stdc++.h>
#include <vector>

using namespace std;
struct CallData{
    vector<void*> btVec;
    unsigned long int dyncount;
    unsigned long int loweredCount;
};

class PrecisionTuner
{
    private:
    unordered_map<uint64_t, struct CallData> __backtraceMap;
    unsigned long __loweredCount = 0;
    unsigned long __dyncount = 0;
    unsigned long __minbound = 0;
    unsigned long __maxbound = 0;
    unsigned long __totalCallStacks = 0;

    void __display();
    void __dump_json();
    double __overloading_function(string s, float fres, double dres, double value);
    void __dump_stack(uint64_t key);

    public:
    PrecisionTuner();
    ~PrecisionTuner();
    uint64_t get_context_hash_backtrace();
    double overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
            double value, double parameter);
    double overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value);
};
