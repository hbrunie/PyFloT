#ifndef Strategy_H
#define Strategy_H

#include "Profile.hpp"    

using namespace std;
using namespace Json;
class Strategy 
{
    private:
        unsigned long __dyncount;
        unsigned long __loweredCount;
        string __dumpStratResultsJson;
        void __buildStrategyFromJsonFile(string);
    public:
        Strategy();
        Strategy(string, string);
        bool singlePrecision(Profile&);
        void dumpJson();
        friend ostream& operator<<(ostream& os, const Strategy& strat);
};
#endif // Strategy_H
