#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <math.h>
#include <vector>

#include <execinfo.h>
#include <json/json.h>

#include "PrecisionTuner.hpp"
#include "Debug.hpp"
using namespace std;
using namespace Json;

const string DynFuncCall::JSON_CALLSTACK_ADDR_LIST_KEY = "CallStack";
const string DynFuncCall::JSON_CALLSCOUNT_KEY      = "CallsCount";
const string DynFuncCall::JSON_INREGION0_KEY      = "InRegion0";
const string DynFuncCall::JSON_INREGION1_KEY      = "InRegion1";
const string DynFuncCall::JSON_INREGION2_KEY      = "InRegion2";
const string DynFuncCall::JSON_LOWERCOUNT_KEY      = "LowerCount";
const string DynFuncCall::JSON_LOWERBOUND_KEY      = "LowerBound";
const string DynFuncCall::JSON_UPPERBOUND_KEY      = "UpperBound";

static volatile bool GLOBAL_IN_REGION0 = false;
static volatile bool GLOBAL_IN_REGION1 = false;
static volatile bool GLOBAL_IN_REGION2 = false;
void setInRegion(int reg){
    if(reg==0)
        GLOBAL_IN_REGION0 = true;
    if(reg==1)
        GLOBAL_IN_REGION1 = true;
    if(reg==2)
        GLOBAL_IN_REGION2 = true;
}

void unSetInRegion(int reg){
    if(reg==0)
        GLOBAL_IN_REGION0 = false;
    if(reg==1)
        GLOBAL_IN_REGION1 = false;
    if(reg==2)
        GLOBAL_IN_REGION2 = false;
}

DynFuncCall::DynFuncCall(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __dynHashKey = 0;
    __statHashKey = "";
    __dyncount = 0;
    __inRegion0 = 0;
    __inRegion1 = 0;
    __inRegion2 = 0;
    __inRegionBool0 = GLOBAL_IN_REGION0;
    __inRegionBool1 = GLOBAL_IN_REGION1;
    __inRegionBool2 = GLOBAL_IN_REGION2;
    __profiledDyncount = 0;
    __loweredCount = 0;
    __lowerBound   = numeric_limits<unsigned int>::max();
    __upperBound   = 0;
}

DynFuncCall::DynFuncCall(Value dynFuncCall, string statHashKey) : DynFuncCall(){
    DEBUG("info",cerr << __FUNCTION__<< ":" << __LINE__ << endl;);
    __profiledDyncount = dynFuncCall[JSON_CALLSCOUNT_KEY].asUInt64();
    DEBUG("dfc",cerr << __FUNCTION__<< ":" << __LINE__ <<
           "call count:" << __profiledDyncount<< endl;);
    __loweredCount = dynFuncCall[JSON_LOWERCOUNT_KEY].asUInt64();
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
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
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

ostream& operator<<(ostream& os, const DynFuncCall& dfc){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    os << "CallData: Dyncount("<< dfc.__dyncount
        << ") __profiledDyncount(" << dfc.__profiledDyncount
        << ") loweredCount("
        << dfc.__loweredCount << ") btVec (size="<< dfc.__btVec.size()<< ")"
        " dynHashKey: " << dfc.__dynHashKey <<
        " statHashKey: " << dfc.__statHashKey << endl;
    for(auto it = dfc.__btVec.begin() ; it != dfc.__btVec.end() ; it++){
        os << *it << endl;
    }
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return os;
}

vector<void*> DynFuncCall::getBtVector(){return __btVec;}

void DynFuncCall::applyProfiling(){
    __dyncount ++;
    if(__inRegionBool0)
        __inRegion0++;
    if(__inRegionBool1)
        __inRegion1++;
    if(__inRegionBool2)
        __inRegion2++;
}

bool DynFuncCall::applyStrategy(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    this->__dyncount ++;
    for(auto it = __stratMultiSet.begin() ; it != __stratMultiSet.end(); it++){
        struct FloatSet fs = *it;
        unsigned int lowerBound = round(__profiledDyncount*fs.low);
        __lowerBound = min(lowerBound, __lowerBound);
        unsigned int upperBound = round(__profiledDyncount*fs.high);
        __upperBound = max(upperBound, __upperBound);
        bool comparison = lowerBound < this->__dyncount && this->__dyncount <= upperBound;
        DEBUG("comparison",cerr << "Comparison: " << lowerBound << " < " << __dyncount
                << " <= " <<  upperBound << " "<< (comparison ? "TRUE" : "FALSE") << endl;);
        //TODO: with python script, display the non normalized interval
        //TODO: with only one call (number 0) it belongs to any [0,x], but to no [x,1], is this wanted?
        // it should appear in some documentation
        if(comparison){
            this->__loweredCount++;
            return true;
        }
    }
    return false;
}

Value DynFuncCall::getJsonValue(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    Value v;
    Value dyncount((UInt)__dyncount);
    Value loweredCount((UInt)__loweredCount);
    Value inRegion0((UInt)__inRegion0);
    Value inRegion1((UInt)__inRegion1);
    Value inRegion2((UInt)__inRegion2);
    Value lowerBound((UInt)__lowerBound);
    Value upperBound((UInt)__upperBound);
    Value btVec;

    v[JSON_CALLSCOUNT_KEY] = dyncount;
    v[JSON_LOWERCOUNT_KEY] = loweredCount;
    v[JSON_INREGION0_KEY]   = inRegion0;
    v[JSON_INREGION1_KEY]   = inRegion1;
    v[JSON_INREGION2_KEY]   = inRegion2;
    v[JSON_LOWERBOUND_KEY] = lowerBound;
    v[JSON_UPPERBOUND_KEY] = upperBound;
    void** sym_array = (void**) malloc(sizeof(void*)*__btVec.size());
    for(unsigned int i =0; i< __btVec.size();i++){
        sym_array[i] = __btVec[i];
    }
    //copy(__btVec.begin(), __btVec.end(), sym_array);
    char ** char_array = backtrace_symbols((void* const*)sym_array, __btVec.size());
    free(sym_array);
    for(unsigned int i =0; i< __btVec.size();i++){
        String s(char_array[i]);
        Value sym = s;
        btVec.append(sym);
    }
    v[JSON_CALLSTACK_ADDR_LIST_KEY] = btVec;
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return v;
}
