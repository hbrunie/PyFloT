#include <unordered_map>
#include <string>
#include <iostream>
#include <vector>

using namespace std;
class CallData
{
    public:
    vector<void*> btVec;
    unsigned long dyncount;
    unsigned long loweredCount;
    friend ostream& operator<<(ostream& os, const struct CallData& cd);
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
    /* Profiling */
    bool __profiling;
    char * __jsonFileFromProfiling;

    void __display();
    void __dump_json();
    double __overloading_function(string s, float fres, double dres, double value);
    void __dump_stack(uint64_t key);
    unordered_map<uint64_t, struct CallData> __build_callstacks_map_from_json_file(char * jsonFile);

    static const unsigned int MAXSTACKSIZE;
    /* JSON values and sections keys */
    // Number of independant call stacks
    static const string JSON_TOTALCALLSTACKS_KEY;
    // List of all the call stack dictionnaries
    static const string JSON_MAIN_LIST;
    /* Inside each independant call stack dictionnary */
    // List of Hexadecimal virtual addresses
    static const string JSON_CALLSTACK_LIST;
    // Dynamic calls total count
    static const string JSON_CALLSCOUNT_KEY;
    // LOWERED Dynamic calls count
    static const string JSON_LOWERCOUNT_KEY;
    static const string JSON_HASHKEY_KEY;

    public:
    PrecisionTuner();
    ~PrecisionTuner();
    uint64_t get_context_hash_backtrace(bool lowered);
    double overloading_function(string s, float (*sp_func) (float, float), double (*func)(double, double), 
            double value, double parameter);
    double overloading_function(string s, float (*sp_func) (float), double (*func)(double), double value);
    /* Test functions */
    void testJson(string jsonFile);
};
