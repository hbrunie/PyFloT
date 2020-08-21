#ifndef SHADOW_VALUE
#define SHADOW_VALUE
#include <json/json.h>
#include <fstream>

#include "Debug.hpp"

using namespace std;
using namespace Json;
class ShadowValue{
    private:
        static Debug degug;
        double __doubleP;
        double __singleP;
        double __argument;
        bool   __spBoolean;
        unsigned long __index;
        static unsigned long __globalCounter;
        double __timeStamp;
    public:
        ShadowValue(double, float, double, bool);
        ShadowValue(double, float, double, bool, double);
        Value getJsonValue();
        string getCSVformat();
        friend ostream& operator<<(ostream& os, const ShadowValue& sv);
        friend ostream& operator<<(ostream& os, const vector<ShadowValue>& sv);
};
#endif
