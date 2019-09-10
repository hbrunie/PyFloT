#ifndef Strategy_H
#define Strategy_H

#include "Profile.hpp"    

using namespace std;
using namespace Json;
class Strategy 
{
    private:
        unsigned long __dyncount;
        unsigned long __totalLoweredCount;
        string __dumpJsonStratResultsFile;
        // List of all the call stack dictionnaries
        static const string JSON_MAIN_LIST;
        static const string JSON_HASHKEY_KEY;
        static const string JSON_TOLOWER_LIST_KEY;
        static const string JSON_TOTALLOWEREDCOUNT_KEY;
        // private functions
        void __buildStrategyFromJsonFile(string);
    public:
        Strategy();
        Strategy(string, string);
        bool singlePrecision(DynFuncCall &);
        void updateResults(DynFuncCall&);
        void dumpJson();
        friend ostream& operator<<(ostream& os, const Strategy& strat);
};
#endif // Strategy_H
