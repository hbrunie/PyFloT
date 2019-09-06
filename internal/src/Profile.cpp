#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>

#include <execinfo.h>
#include <json/json.h>

#include "Debug.hpp"
#include "Profile.hpp"
//#include "DynFuncCall.hpp"    
using namespace std;
using namespace Json;

const string Profile::JSON_TOTALCALLSTACKS_KEY   = "TotalCallStacks";
const string Profile::JSON_HASHKEY_KEY           = "HashKey";
const string Profile::JSON_MAIN_LIST             = "IndependantCallStacks";

Profile::Profile(){
}

Profile::Profile(string fname){
    __buildProfiledDataFromJsonFile(fname);
}

void Profile::__buildProfiledDataFromJsonFile(string fname){
    Value jsonDictionnary;
    std::ifstream infile(fname, std::ifstream::binary);
    infile >> jsonDictionnary;
}

void Profile::dumpJson(){
    //TODO: factorize this code
    const char* jsonFile;
    bool useCout;
    filebuf fb;
    Value jsonDictionnary;
    Value jsonTotalCallStacks;
    Value jsonDynFuncCallsList;
    ostream outfile(NULL);

    jsonFile = getenv(jsonFile);
    useCout = true;
    if(NULL == jsonFile) {
            fprintf(stderr, "Wrong jsonfile abspath: %s\n", jsonFile);
            fprintf(stderr, "Dumping on stdout\n");
            
    }else{
        fb.open(jsonFile,ios::out);
        if(!fb.is_open()){
            fprintf(stderr, "Wrong jsonfile abspath: %s\n",jsonFile);
            fprintf(stderr, "Dumping on stdout\n");
        }else
            useCout = false;
    }
    if (!useCout)
        ostream outfile(&fb);
    jsonTotalCallStacks = (UInt)__totalCallStacks;
    jsonDictionnary[JSON_TOTALCALLSTACKS_KEY] = jsonTotalCallStacks;

}

void Profile::__dumpHashMapJson(ostream &os, unordered_map<uint64_t, DynFuncCall> &hashMap){
    Value jsonDictionnary;
    Value jsonDynFuncCallsList;
    for (auto it = hashMap.begin(); it != hashMap.end(); ++it){
        unsigned long key = it->first;
        DynFuncCall value = it->second;
        Value hashkey((UInt)key);
        Value jsonDynFuncCall = value.getJsonValue();
        jsonDynFuncCall[JSON_HASHKEY_KEY] = hashkey; 
        jsonDynFuncCallsList.append(jsonDynFuncCall);
    }
    DEBUG("infoplus",cerr <<jsonDynFuncCallsList<< endl;);
    jsonDictionnary[JSON_MAIN_LIST] = jsonDynFuncCallsList;
    os << jsonDictionnary << endl;
    //if (useCout)
    //    cout <<jsonDictionnary; 
    //else
    //    outfile << jsonDictionnary; 
    //TODO: find proper C++ way to do this fopen with defaut == cout
    // close the file
}
