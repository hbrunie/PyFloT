#include <cstdio>
#include <cstdlib>
#include <fstream>

#include <execinfo.h>
#include <json/json.h>

#include "PrecisionTuner.hpp"    
using namespace std;
using namespace Json;

const string DynFuncCall::JSON_CALLSTACK_ADDR_LIST_KEY = "CallStack";
const string DynFuncCall::JSON_CALLSCOUNT_KEY      = "CallsCount";
const string DynFuncCall::JSON_LOWERCOUNT_KEY      = "LowerCount";

DynFuncCall::DynFuncCall(){
}

DynFuncCall::DynFuncCall(Value dynFuncCall, Value hashKey){
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
}
        
DynFuncCall::DynFuncCall(const DynFuncCall & dfc){
    __btVec = dfc.__btVec;
    __dyncount = dfc.__dyncount;
    __loweredCount = dfc.__loweredCount;
}

DynFuncCall::DynFuncCall(vector<void*> btVec, unsigned long dyncount, unsigned long loweredCount){
    __btVec = btVec;
    __dyncount = dyncount;
    __loweredCount = loweredCount;
}

DynFuncCall::DynFuncCall(vector<void*> btVec, bool lowered){
    __btVec = btVec;
    __dyncount = 1;
    __loweredCount = lowered ? 1 : 0;
}

void DynFuncCall::called(bool lowered){
    __dyncount++;
    __loweredCount += lowered ? 1 : 0;
}

ostream& operator<<(ostream& os, const DynFuncCall& dfc)
{
    os << "CallData: Dyncount("<< dfc.__dyncount
        << ") loweredCount("
        << dfc.__loweredCount << ") btVec (size="<< dfc.__btVec.size()<< ")" << endl;
    for(auto it = dfc.__btVec.begin() ; it != dfc.__btVec.end() ; it++){
        os << *it << endl;
    }
    return os;
}

void DynFuncCall::dumpStack() {
    fprintf(stderr, "\n %lu", __btVec.size());
    for(int i = 0; i < __btVec.size(); i++)
        fprintf(stderr, "\t %lx", (unsigned long) __btVec[i]);
}

Value DynFuncCall::getJsonValue(){
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
    return v;
}
