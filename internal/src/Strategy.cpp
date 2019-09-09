#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>

#include <execinfo.h>
#include <json/json.h>

#include "Debug.hpp"
#include "Strategy.hpp"    
using namespace std;
using namespace Json;

const string Strategy::JSON_TOTALLOWEREDCOUNT_KEY = "LowerCount";
//From list to Set.
const string Strategy::JSON_TOLOWER_LIST_KEY      = "ToLowerList";
//TODO: Factorize with Profile
const string Strategy::JSON_MAIN_LIST             = "IndependantCallStacks";
const string Strategy::JSON_HASHKEY_KEY           = "HashKey";

Strategy::Strategy(){
    __dyncount = 0;
    __totalLoweredCount = 0;
}

Strategy::Strategy(string readStratFromJsonFile, string  dumpJsonStratResultsFile){
    __dyncount = 0;
    __totalLoweredCount = 0;
    __dumpJsonStratResultsFile = dumpJsonStratResultsFile;
    __buildStrategyFromJsonFile(readStratFromJsonFile);
}

bool Strategy::singlePrecision(DynFuncCall & dfc){
    /* Compare dfc current dyn Call Count with the Set of toLower DynCallCount
     * For this particular DynCallSite
     */
    unsigned long curDynCount = dfc.getCurrentDynCount();
    uint64_t hashKey = dfc.getHashKey();
    unordered_map<uint64_t, unordered_set<unsigned long>>::iterator hashKeyIte = __toLower.find(hashKey);
    if(hashKeyIte == __toLower.end())
        cerr << "Invalid DynCallSite hash key << " << hashKey << endl;
    else{
    if(__toLower[hashKey].contains(curDynCount))
        return true;
    else
        return false;
}

void Strategy::updateResults(DynFuncCall& dfc){
    __totalLoweredCount = dfc.getLoweredCount();
}

void Strategy::dumpJson(){
    /* Dumping strategy results */
    DEBUG("info",cerr << "STARTING " << __FUNCTION__ << endl;);
    bool useCout = true;
    ofstream fb;
    fb.open(__dumpJsonStratResultsFile,ios::out);
    if(!fb.is_open()){
        cerr << "Profile: Wrong jsonfile abspath: " 
            << __dumpJsonStratResultsFile << endl 
            << "Dumping on stdout " << endl;
    }else
        useCout = false;

    Value jsonDictionary;
    Value jsonDynFuncCallsList;
    Value jsonTotalCallStacks = (UInt)__totalCallStacks;
    jsonDictionary[JSON_TOTALLOWEREDCOUNT_KEY] = __totalLoweredCount;
    for (auto it = hashMap.begin(); it != hashMap.end(); ++it){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        Value hashkey((UInt)key);
        Value jsonDynFuncCall = value.getJsonValue();
        jsonDynFuncCall[JSON_HASHKEY_KEY] = hashkey; 
        jsonDynFuncCallsList.append(jsonDynFuncCall);
    }
    jsonDictionary[JSON_MAIN_LIST] = jsonDynFuncCallsList;
    DEBUG("infoplus",cerr << __FUNCTION__ << jsonDictionary<< endl;);
    DEBUG("infoplus",cerr << __FUNCTION__ << useCout << __dumpJsonStratResultsFile  << endl;);
    if (useCout)
        cout <<jsonDictionary << endl; 
    else{
        fb << jsonDictionary << endl;; 
    }
    DEBUG("info",cerr << "ENDING " << __FUNCTION__ << endl;);

}

ostream& operator<<(ostream& os, const Strategy& strat){
    os << "Strategy: Dyncount("<< strat.__dyncount
        << ") loweredCount("
        << strat.__totalLoweredCount << endl; 
    //<< ") btVec (size="<< strat.__btVec.size()<< ")" << endl;
    //for(auto it = strat.__btVec.begin() ; it != strat.__btVec.end() ; it++){
    //    os << *it << endl;
    //}
    return os;
}

/*** PRIVATE FUNCTIONS ***/

static bool stream_check(ifstream& s){
    if(s.bad() || s.fail()){
        cerr << "Bad or failed "<< endl;
    }
    if(s.good() && s.is_open())
        return true;
    return false;
}

void Strategy::__buildStrategyFromJsonFile(string fileAbsPath){
    /* For each DynCallSite defined by the profiling
     * fill the set of toLower unsigned long ids.
     * --> Fill the toLower unordered hash map of unordered set.
     */
    std::ifstream infile(fileAbsPath, std::ifstream::binary);
    if(!stream_check(infile))
        exit(-1);
    Value jsonDictionary;
    infile >>  jsonDictionary;
    DEBUG("info",cerr << "READING JSON __build_callstacks_map_from_json_file" << endl;);
    DEBUG("infoplus",cerr << jsonDictionary << endl;);

    //TODO Factorize DynFuncCallSitesList
    Value callStacksList = jsonDictionary[JSON_MAIN_LIST];
    /* Fill the backtraceMap with JSON values */
    cerr << callStacksList.size() << endl;
    for(unsigned int callStackIndex = 0; callStackIndex < callStacksList.size(); callStackIndex++){
        // Get the callStack dictionary
        Value callStack = callStacksList[callStackIndex];
        Value hashKey = callStack[JSON_HASHKEY_KEY];
        DynFuncCall data(callStack, hashKey);
        // TODO: factorize this and the same code in DynFuncCall constructor
        // into JsonUtils.cpp
        uint64_t UIntHashKey;
        string s = hashKey.asString();
        istringstream iss(s);
        iss >> hex >> UIntHashKey;
        //TODO: end of factorization
        __backtraceDynamicMap[UIntHashKey] = data;
    }

}
