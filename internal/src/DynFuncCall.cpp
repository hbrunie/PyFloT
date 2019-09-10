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
}

DynFuncCall::DynFuncCall(vector<void*>  btVec, uint64_t hashKey, bool lowered){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __hashKey = hashKey; 
    __btVec = btVec;
    __dyncount = 1;
    __loweredCount = lowered ? 1 : 0;
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
}

DynFuncCall::DynFuncCall(vector<void*>  btVec, uint64_t hashKey) : DynFuncCall(btVec, hashKey, false) {}

DynFuncCall::DynFuncCall(Value dynFuncCall, uint64_t hashKey){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __dyncount = dynFuncCall[JSON_CALLSCOUNT_KEY].asUInt64();
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
    Value dynFuncCallAddrList = dynFuncCall[JSON_CALLSTACK_ADDR_LIST_KEY];
    for(unsigned int btVecInd = 0; btVecInd < dynFuncCallAddrList.size(); btVecInd++){
        string s = dynFuncCallAddrList[btVecInd].asString();
        unsigned long value;
        istringstream iss(s);
        iss >> hex >> value;
        __btVec.push_back((void*) value);
    }
    __hashKey = hashKey;
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
}

unsigned long DynFuncCall::getLoweredCount(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    return __loweredCount;
}

void DynFuncCall::called(DynFuncCall & dfc){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __dyncount     += dfc.__dyncount;
    __loweredCount += dfc.__loweredCount;
}

uint64_t DynFuncCall::getHashKey(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    return __hashKey;
}

DynFuncCall::DynFuncCall(const DynFuncCall & dfc){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __btVec = dfc.__btVec;
    __dyncount = dfc.__dyncount;
    __loweredCount = dfc.__loweredCount;
}

DynFuncCall::DynFuncCall(vector<void*> btVec, unsigned long dyncount, unsigned long loweredCount){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __btVec = btVec;
    __dyncount = dyncount;
    __loweredCount = loweredCount;
}

ostream& operator<<(ostream& os, const DynFuncCall& dfc){
    DEBUG("infoplus",cerr << "STARTING " << __FUNCTION__ << endl;);
    os << "CallData: Dyncount("<< dfc.__dyncount
        << ") loweredCount("
        << dfc.__loweredCount << ") btVec (size="<< dfc.__btVec.size()<< ")" << endl;
    for(auto it = dfc.__btVec.begin() ; it != dfc.__btVec.end() ; it++){
        os << *it << endl;
    }
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
    return os;
}

vector<void*> DynFuncCall::getBtVector(){return __btVec;}

void DynFuncCall::updateLowerCount(bool lower){
    __loweredCount += lower ? 1 : 0;
}

bool DynFuncCall::applyStrategy(){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    for(auto it = __stratMultiSet.begin() ; it != __stratMultiSet.end(); it++){
        struct FloatSet fs = *it;
        DEBUG("info",cerr << "Comparison: " << __dyncount*fs.low << " < " << __dyncount << " < " << __dyncount*fs.high << endl;);
        if(__dyncount > __dyncount*fs.low && __dyncount < __dyncount*fs.high)
            return true;
    }
    return false;
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
