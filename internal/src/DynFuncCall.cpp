#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <math.h>
#include <vector>

#include <execinfo.h>
#include <json/json.h>

#include <PT_Labels.hpp>

#include "Debug.hpp"
#include "PrecisionTuner.hpp"
#include "Utils.hpp"

using namespace std;
using namespace Json;

const string DynFuncCall::JSON_CALLSTACK_ADDR_LIST_KEY = "CallStack";
const string DynFuncCall::JSON_CALLSCOUNT_KEY          = "CallsCount";
const string DynFuncCall::JSON_LABELS_KEY              = "Labels";
const string DynFuncCall::JSON_LOWERCOUNT_KEY          = "LowerCount";
const string DynFuncCall::JSON_LOWERBOUND_KEY          = "LowerBound";
const string DynFuncCall::JSON_UPPERBOUND_KEY          = "UpperBound";

int setInRegion(string label){
    Labels labels;
    return labels.setInRegion(label);
}
int unSetInRegion(string label){
    Labels labels;
    return labels.unSetInRegion(label);
}

int setInRegion(const char * label){
    Labels labels;
    return labels.setInRegion(label);
}
int unSetInRegion(const char * label){
    Labels labels;
    return labels.unSetInRegion(label);
}

set<string> DynFuncCall::backtraceToLower = set<string>();

DynFuncCall::DynFuncCall(){
    DEBUGINFO("STARTING");
    __dynHashKey       = 0;
    __backtraceStrat   = false;
    __statHashKey      = "";
    __dyncount         = 0;
    __profiledDyncount = 0;
    __loweredCount     = 0;
    __lowerBound       = numeric_limits<unsigned int>::max();
    __upperBound       = 0;
}

static bool onceForAll = true;
DynFuncCall::DynFuncCall(Value dynFuncCall, string statHashKey) : DynFuncCall(){
    DEBUGINFO("STARTING");
    __profiledDyncount = dynFuncCall[JSON_CALLSCOUNT_KEY].asUInt64();
    __loweredCount = dynFuncCall[JSON_LOWERCOUNT_KEY].asUInt64();
    if(onceForAll)
        updateStrategyBacktraceList();
    onceForAll = false;
    Value stratSet = dynFuncCall["Strategy"];
    for(unsigned int multiSetInd = 0; multiSetInd < stratSet.size(); multiSetInd++){
        Value s = stratSet[multiSetInd];
        struct FloatSet fset;
        for(unsigned int i = 0; i < 2; i++){
            Value ss = s[i];
            if(i==0)
                fset.low = atof((ss.asString()).c_str());
            else
                fset.high = atof((ss.asString()).c_str());
        }
        __stratMultiSet.push_back(fset);
    }
    // TODO: STATIC hashKey, create __staticBtVec. Do we really need staticBtVec?
    Value dynFuncCallAddrList = dynFuncCall[JSON_CALLSTACK_ADDR_LIST_KEY];
    for(unsigned int btVecInd = 0; btVecInd < dynFuncCallAddrList.size(); btVecInd++){
        string s = dynFuncCallAddrList[btVecInd].asString();
        unsigned long value;
        istringstream iss(s);
        iss >> hex >> value;
        __staticBtVec.push_back((void*) value);
    }
    __statHashKey = statHashKey;
    DEBUGINFO("ENDING");
}

DynFuncCall::DynFuncCall(vector<void*> btVec) : DynFuncCall(){
    __btVec = btVec;
}

DynFuncCall::DynFuncCall(vector<void*>  btVec, string statHashKey) : DynFuncCall(btVec){
    __statHashKey = statHashKey;
}

DynFuncCall::DynFuncCall(vector<void*>  btVec, uintptr_t dynHashKey) : DynFuncCall(btVec){
    __dynHashKey = dynHashKey;
}

DynFuncCall::DynFuncCall(vector<void*>  btVec, uintptr_t dynHashKey, ShadowValue &sv) : DynFuncCall(btVec, dynHashKey){
    DEBUGG("sv","Pushing Back: " << sv);
    __shadowValues.push_back(sv);
    DEBUGG("sv",string("Vector: ") << __shadowValues);
}

DynFuncCall::DynFuncCall(vector<void*> btVec, uint32_t profiledDyncount) : DynFuncCall(btVec){
    __profiledDyncount = profiledDyncount;
}

DynFuncCall::DynFuncCall(vector<void*> btVec, string statHashKey, bool lowered) :
    DynFuncCall(btVec, statHashKey){
    __loweredCount = lowered ? 1 : 0;
}

DynFuncCall::DynFuncCall(vector<void*> btVec, uint32_t profiledDyncount, bool lowered) :
    DynFuncCall(btVec, profiledDyncount){
    __loweredCount = lowered ? 1 : 0;
}

ostream& operator<<(ostream& os, const set<string>& s){
    for (auto it=s.begin(); it != s.end(); ++it)
                os << ' ' << *it << endl;
    return os;
}

ostream& operator<<(ostream& os, const DynFuncCall& dfc){
    os << "CallData: Dyncount("<< dfc.__dyncount
        << ") __profiledDyncount(" << dfc.__profiledDyncount
        << ") loweredCount("
        << dfc.__loweredCount << ") btVec (size="<< dfc.__btVec.size()<< ")"
        " dynHashKey: " << dfc.__dynHashKey <<
        " statHashKey: " << dfc.__statHashKey << endl;
    for(auto it = dfc.__btVec.begin() ; it != dfc.__btVec.end() ; it++){
        os << *it << endl;
    }
    return os;
}

vector<void*> DynFuncCall::getBtVector(){return __btVec;}

void DynFuncCall::applyProfiling(ShadowValue &sv){
    __dyncount ++;
    DEBUGG("sv","Pushing Back: " << sv);
    __shadowValues.push_back(sv);
    DEBUGG("sv",string("Vector: ") << __shadowValues);
    labels.update();
}

//TODO: factorize with writeBacktraceKeyFile in Profile.cpp (io.cpp?)
void DynFuncCall::updateStrategyBacktraceList(){
    //read file
    ifstream f = readFile(string("BACKTRACE_LIST"),string("BackraceList.txt"));

    string line;
    while (getline(f,line)){
        backtraceToLower.insert(line);
    }
    DEBUG("backstrat",cerr << backtraceToLower << endl;);
}
void DynFuncCall::updateStrategyBacktrace(){
    DEBUGINFO("backtraceToLower " << backtraceToLower);
    auto ite = backtraceToLower.find(__statHashKey);
    // Look for backtrace in strategy to lower
    if(ite == backtraceToLower.end())
        __backtraceStrat = false;
    else
        __backtraceStrat = true;
    DEBUGINFO("toLower?"<< __backtraceStrat);
}

bool DynFuncCall::applyStrategyBacktrace(){
    DEBUGINFO("backtraceStrat?(" << __backtraceStrat << ")");
    this->__dyncount ++;
    if(__backtraceStrat){
        this->__loweredCount++;
        return true;
    }
    return false;
}

bool DynFuncCall::applyStrategyDynCount(){
    DEBUGINFO("STARTING");
    this->__dyncount ++;
    for(auto it = __stratMultiSet.begin() ; it != __stratMultiSet.end(); it++){
        struct FloatSet fs = *it;
        unsigned int lowerBound = round(__profiledDyncount*fs.low);
        __lowerBound = min(lowerBound, __lowerBound);
        unsigned int upperBound = round(__profiledDyncount*fs.high);
        __upperBound = max(upperBound, __upperBound);
        bool comparison = lowerBound < this->__dyncount && this->__dyncount <= upperBound;
        DEBUGINFO("Comparison: " << lowerBound << " < " << __dyncount
                << " <= " <<  upperBound << " "<< (comparison ? "TRUE" : "FALSE"));
        if(comparison){
            this->__loweredCount++;
            return true;
        }
    }
    return false;
}

string DynFuncCall::getCSVformat(){
    /* For each ShadowValue: index arg double single absErr relErr singlePrecBool */
    string result = "";
    for(unsigned int i=0; i<__shadowValues.size(); i++)
        result +=  __shadowValues[i].getCSVformat() + "\n";
    return result;
}

Value DynFuncCall::getReducedJsonValue(){
    return getJsonValue(true);
}

Value DynFuncCall::getFullJsonValue(){
    return getJsonValue(false);
}

Value DynFuncCall::getJsonValue(bool dumpReduced){
    DEBUGINFO("STARTING");
    Value v;
    Value dyncount((UInt)__dyncount);
    Value loweredCount((UInt)__loweredCount);
    Value lowerBound((UInt)__lowerBound);
    Value upperBound((UInt)__upperBound);
    Value btVec;
    Value shadowValues;

    v[JSON_LABELS_KEY] = labels.getJsonValue();

    v[JSON_CALLSCOUNT_KEY] = dyncount;
    v[JSON_LOWERCOUNT_KEY] = loweredCount;
    v[JSON_LOWERBOUND_KEY] = lowerBound;
    v[JSON_UPPERBOUND_KEY] = upperBound;

    if(!dumpReduced){
        for(unsigned int i=0; i<__shadowValues.size(); i++)
            shadowValues.append(__shadowValues[i].getJsonValue());
        v["ShadowValues"] = shadowValues;
    }

    void** sym_array = (void**) malloc(sizeof(void*)*__btVec.size());
    for(unsigned int i =0; i< __btVec.size();i++){
        sym_array[i] = __btVec[i];
    }
    char ** char_array = backtrace_symbols((void* const*)sym_array, __btVec.size());
    free(sym_array);
    for(unsigned int i =0; i< __btVec.size();i++){
        String s(char_array[i]);
        Value sym = s;
        btVec.append(sym);
    }
    v[JSON_CALLSTACK_ADDR_LIST_KEY] = btVec;
    DEBUGINFO("ENDING");
    return v;
}
