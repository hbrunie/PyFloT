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

Strategy::Strategy(string fname, string dumpStratResultsJson){
    __dyncount = 0;
    __loweredCount = 0;
    __dumpStratResultsJson = dumpStratResultsJson;
    __buildStrategyFromJsonFile(fname);
}

Strategy::Strategy(){
    __dyncount = 0;
    __loweredCount = 0;
}
bool Strategy::singlePrecision(Profile& profile){
    profile.getCurrentDynCount();
    return true;
}

void Strategy::__buildStrategyFromJsonFile(string){
}

void Strategy::dumpJson(){

}

ostream& operator<<(ostream& os, const Strategy& strat){
    os << "Strategy: Dyncount("<< strat.__dyncount
        << ") loweredCount("
        << strat.__loweredCount << endl; 
    //<< ") btVec (size="<< strat.__btVec.size()<< ")" << endl;
    //for(auto it = strat.__btVec.begin() ; it != strat.__btVec.end() ; it++){
    //    os << *it << endl;
    //}
    return os;
}
