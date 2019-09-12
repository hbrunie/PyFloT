#include <cstdio>
#include <cstdlib>
#include <fstream>

#include <execinfo.h>
#include <json/json.h>

#include "PrecisionTuner.hpp"    
#include "Debug.hpp"    
using namespace std;
using namespace Json;

const string DynFuncCall::JSON_CALLSTACK_ADDR_LIST_KEY = "CallStack";
const string DynFuncCall::JSON_CALLSCOUNT_KEY      = "CallsCount";
const string DynFuncCall::JSON_LOWERCOUNT_KEY      = "LowerCount";

DynFuncCall::DynFuncCall(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __dynHashKey = 0;
    __statHashKey = ""; 
    __dyncount = 0;
    __profiledDyncount = 0;
    __loweredCount = 0;
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
    // It is made of CallStack list, CallsCount, HashKey and LowerCount
    // TODO: STATIC hashKey, create __staticBtVec
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

DynFuncCall::DynFuncCall(vector<void*>  btVec, uint64_t dynHashKey) : DynFuncCall(btVec){
    __dynHashKey = dynHashKey; 
}

DynFuncCall::DynFuncCall(vector<void*> btVec, unsigned long profiledDyncount) : DynFuncCall(btVec){
    __profiledDyncount = profiledDyncount;
}

DynFuncCall::DynFuncCall(vector<void*> btVec, string statHashKey, bool lowered) : 
    DynFuncCall(btVec, statHashKey){
    __loweredCount = lowered ? 1 : 0;
}

DynFuncCall::DynFuncCall(vector<void*> btVec, unsigned long profiledDyncount, bool lowered) :
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
}

bool DynFuncCall::applyStrategy(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    bool lower = false;
    for(auto it = __stratMultiSet.begin() ; it != __stratMultiSet.end(); it++){
        struct FloatSet fs = *it;
        DEBUG("info",cerr << "Comparison: " << __profiledDyncount*fs.low << " < " << __dyncount 
                << " < " <<  __profiledDyncount*fs.high << endl;);
        if(__dyncount >= __profiledDyncount*fs.low && __dyncount < __profiledDyncount*fs.high){
            lower = true;
            break;
        }
    }
    __dyncount ++;
    __loweredCount += lower ? 1 : 0;
    return lower;
}

Value DynFuncCall::getJsonValue(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    Value v;
    Value dyncount((UInt)__dyncount);
    Value loweredCount((UInt)__loweredCount);
    Value btVec;

    v[JSON_CALLSCOUNT_KEY] = dyncount;
    v[JSON_LOWERCOUNT_KEY] = loweredCount;
    for(unsigned int i =0; i< __btVec.size();i++){
        Value addr = (LargestInt)__btVec[i];
        btVec.append(addr); 
    }
    v[JSON_CALLSTACK_ADDR_LIST_KEY] = btVec;
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return v;
}
