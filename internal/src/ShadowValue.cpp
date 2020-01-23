#include <ShadowValue.hpp>
unsigned long ShadowValue::__index = 0;
ShadowValue::ShadowValue(double dp, float sp, double argument, bool spBoolean) :
    __doubleP(dp), __singleP((double)sp), __argument(argument),__spBoolean(spBoolean){}
Value ShadowValue::getJsonValue(){
    Value v;
    double dp = __doubleP;
    double sp = __singleP;
    bool spBoolean = __spBoolean;
    double argument = __argument;
    v["arg"] = argument;
    v["index"] = __index++;
    v["singlePrecision"] = spBoolean;
    v["double"] = dp;
    v["single"] = sp;
    v["absErr"] = abs(dp-sp);
    v["relErr"] = abs(dp-sp)/dp;
    return v;
}

ostream& operator<<(ostream& os, const ShadowValue& sv){
    os << " Double Precision: "<< sv.__doubleP
        << " Argument: "<< sv.__argument
        << " Single Precision: "<< sv.__singleP
        << " Single(true)OrDouble(false)? " << sv.__spBoolean
        << endl;
    return os;
}

ostream& operator<<(ostream& os, const vector<ShadowValue>& v){
    for (auto it=v.begin(); it != v.end(); ++it)
                os << ' ' << *it << endl;
    return os;
}
