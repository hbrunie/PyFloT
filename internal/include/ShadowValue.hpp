#ifndef SHADOW_VALUE
#define SHADOW_VALUE
#include <json/json.h>
#include <fstream>

#include "Debug.hpp"

using namespace std;
using namespace Json;

struct MatrixSummary{
    double dnorm2;
    float  snorm2;
    double dmean;
    double variance;
};

/*
 * Math Library call Shadow values contain:
 * Argument(s) (one or two, exp or pow)
 * result (scalar): single precision and double precision
 * double timestamp
 * boolean (single or double precision?)
 *
 * GEMM Shadow value contain:
 * full matrix? --> not realistic, get a matrix summary
 * result full matrix? same, get a summary
 * Summary can be more than just norm2
 * double timestamp
 * boolean (single or double precision?)
 *
 * TODO: inheritance ShadowValue
 *                      /    \
 *          ShadowValueGEMM ShadowValueML
 */
class ShadowValue{
    private:
        static Debug degug;
        struct MatrixSummary __ms;
        double __doubleP;
        double __singleP;
        double __argument;
        bool   __spBoolean;
        unsigned long __index;
        static unsigned long __globalCounter;
        double __timeStamp;
    public:
        ShadowValue(bool, double);
        ShadowValue(MatrixSummary, bool, double);
        ShadowValue(double, float, double, bool);
        ShadowValue(double, float, double, bool, double);
        Value getJsonValue();
        string getCSVformat();
        friend ostream& operator<<(ostream& os, const ShadowValue& sv);
        friend ostream& operator<<(ostream& os, const vector<ShadowValue>& sv);
};
#endif
