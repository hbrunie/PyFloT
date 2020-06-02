#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <limits>
#include <math.h>
#include <vector>

#include <execinfo.h>
#include <json/json.h>

#include "Backtrace.hpp"
#include "Debug.hpp"
#include "PrecisionTuner.hpp"
#include "Utils.hpp"

using namespace std;
using namespace Json;

const string DynFuncCall::JSON_CALLSTACK_ADDR_LIST_KEY       = "CallStack";
const string DynFuncCall::JSON_CALLSTACK_FILELINENO_LIST_KEY = "Addr2lineCallStack";
const string DynFuncCall::JSON_CALLSCOUNT_KEY                = "CallsCount";
const string DynFuncCall::JSON_INDEX_KEY                     = "Index";
const string DynFuncCall::JSON_LABELS_KEY                    = "Labels";
const string DynFuncCall::JSON_LOWERCOUNT_KEY                = "LowerCount";
const string DynFuncCall::JSON_LOWERBOUND_KEY                = "LowerBound";
const string DynFuncCall::JSON_UPPERBOUND_KEY                = "UpperBound";

list<string> DynFuncCall::backtraceToLower = list<string>();

unsigned long DynFuncCall::__globalCounter = 0;
DynFuncCall::DynFuncCall(){
    DEBUGINFO("STARTING");
    __dynHashKey       = 0;
    __backtraceStrat   = false;
    __index            = __globalCounter++;
    __statHashKey      = "";
    __dyncount         = 0;
    __profiledDyncount = 0;
    __loweredCount     = 0;
    __lowerBound       = numeric_limits<unsigned int>::max();
    __upperBound       = 0;
}

unsigned long DynFuncCall::getIndex(){
    return __index;
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
    //TODO: NEVER CALLED ?????
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

ostream& operator<<(ostream& os, const list<string>& s){
    os << "List: " << endl;
    for (auto it=s.begin(); it != s.end(); ++it)
                os << ' ' << *it << endl;
    return os;
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
        //backtraceToLower.insert(line);
        backtraceToLower.push_back(line);
    }
    DEBUG("backstrat",cerr << backtraceToLower << endl;);
}

bool findString(list<string> strList, string s){
    bool found = false;
    for (auto it=strList.begin(); it != strList.end(); ++it){
        if (s.find(*it) != string::npos)
            return true;
    }
    return found;
}

// Check if this Dynamic Call is inside Hashmap
// containing all dynamic calls which MUST be executed in single precision.
// Do this once: when building Profile (for strategy).
// For next executions: use bool __bactraceStrat.
void DynFuncCall::updateStrategyBacktrace(){
    bool found = findString(backtraceToLower, __statHashKey);//.find(__statHashKey);
    // Look for backtrace in strategy to lower
    if(found)
        __backtraceStrat = true;
    else
        __backtraceStrat = false;
}

void DynFuncCall::updateBtSymbols(struct statHashKey_t &shk){
    char ** symbols = shk.sym;
    int size = shk.size;
    __statHashKey = shk.hashKey;
    // Starting at 3 because backtrace inside PyFloT is not useful.
    for(int i=3; i<size; i++){
        __btSymbolsVec.push_back(string(symbols[i]));
    }
}

vector<string> DynFuncCall::getAddr2lineBacktraceVec(string targetExe){
    return addr2lineBacktraceVec(targetExe, __btSymbolsVec, (size_t) __btSymbolsVec.size());
}

bool DynFuncCall::applyStrategyBacktrace(){
    DEBUGINFO("backtraceStrat?(" << __backtraceStrat << ")");
    this->__dyncount ++;
    // Check if this dynamic call MUST be done in reduced precision
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

string DynFuncCall::getCSVformat(int callSiteIndex){
    /* For each ShadowValue: index arg double single absErr relErr singlePrecBool */
    string result = "";
    for(unsigned int i=0; i<__shadowValues.size(); i++)
        result +=  __shadowValues[i].getCSVformat() + " " + to_string(callSiteIndex) + "\n";
    return result;
}

Value DynFuncCall::getReducedJsonValue(char * targetExe){
    return getJsonValue(targetExe);
}

inline bool exists_test0 (const std::string& name) {
        ifstream f(name.c_str());
            return f.good();
}

Value DynFuncCall::getJsonValue(char * targetExe){
    DEBUGINFO("STARTING");
    string stargetExe = string(targetExe);
    if(!exists_test0(stargetExe)){
        cerr << "ERROR executable does not exist " << stargetExe << endl;
        exit(-1);
    }
    Value v;
    Value index((UInt)__index);
    Value dyncount((UInt)__dyncount);
    Value loweredCount((UInt)__loweredCount);
    Value lowerBound((UInt)__lowerBound);
    Value upperBound((UInt)__upperBound);
    Value btVec;
    Value btVecFileLineno;
    Value shadowValues;

    v[JSON_LABELS_KEY] = labels.getJsonValue();

    v[JSON_INDEX_KEY]      = index;
    v[JSON_CALLSCOUNT_KEY] = dyncount;
    v[JSON_LOWERCOUNT_KEY] = loweredCount;
    v[JSON_LOWERBOUND_KEY] = lowerBound;
    v[JSON_UPPERBOUND_KEY] = upperBound;
    vector<string> addr2lineVector;
    if(__btSymbolsVec.size()>0){
        addr2lineVector = addr2lineBacktraceVec(targetExe, __btSymbolsVec,
                __btSymbolsVec.size());
        assert(addr2lineVector.size() == __btSymbolsVec.size());
        for(long unsigned i = 0; i < addr2lineVector.size(); i++){
            Value sym = __btSymbolsVec[i];
            Value addr2lineSym = addr2lineVector[i];
            btVec.append(sym);
            btVecFileLineno.append(addr2lineSym);
        }
        v[JSON_CALLSTACK_ADDR_LIST_KEY] = btVec;
        v[JSON_CALLSTACK_FILELINENO_LIST_KEY] = btVecFileLineno;
    }
    DEBUGINFO("ENDING");
    return v;
}
