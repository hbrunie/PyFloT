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

DynFuncCall::DynFuncCall(vector<void*> btVec, bool lowered){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __hashKey = 0; 
    __btVec = btVec;
    __dyncount = 1;
    __loweredCount = lowered ? 1 : 0;
    for(auto it = btVec.begin(); it != btVec.end(); it++){
        void *ip = *it;
        assert(NULL != ip);
        __hashKey += (uint64_t) ip;
        assert( (__hashKey+ (uint64_t) ip) < numeric_limits<uint64_t>::max());
    }
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
}

unsigned long DynFuncCall::getLoweredCount()const{
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    return __loweredCount;
}

uint64_t DynFuncCall::getHashKey()const{
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    return __hashKey;
}

DynFuncCall::DynFuncCall(Value dynFuncCall, Value hashKey){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    Value dynFuncCallAddrList = dynFuncCall[JSON_CALLSTACK_ADDR_LIST_KEY];
    // It is made of CallStack list, CallsCount, HashKey and LowerCount
    __dyncount = dynFuncCall[JSON_CALLSCOUNT_KEY].asUInt64();
    __loweredCount = dynFuncCall[JSON_LOWERCOUNT_KEY].asUInt64();
    for(unsigned int btVecInd = 0; btVecInd < dynFuncCallAddrList.size(); btVecInd++){
        string s = dynFuncCallAddrList[btVecInd].asString();
        unsigned long value;
        istringstream iss(s);
        iss >> hex >> value;
        __btVec.push_back((void*) value);
    }
    string s = hashKey.asString();
    istringstream iss(s);
    iss >> hex >> __hashKey;
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);
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

void DynFuncCall::called(DynFuncCall & dfc){
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    __dyncount     += dfc.__dyncount;
    __loweredCount += dfc.__loweredCount;
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
