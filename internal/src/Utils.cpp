#include <Utils.hpp>
#include <Debug.hpp>
#include <iostream>
//static bool stream_check(ifstream& s){
//    if(s.bad() || s.fail()){
//        cerr << __FUNCTION__ << ":" << __LINE__<< "Bad or failed "<< endl;
//    }
//    if(s.good() && s.is_open())
//        return true;
//    return false;
//}
using namespace std;

ofstream writeFile(string envName, string defaultFile, string dumpDir,string defaultDir, int csvIndex);

ofstream writeJSONFile(string envName, string defaultFile, string dumpDir,string defaultDir){
    return writeFile(envName, defaultFile, dumpDir, defaultDir, -1);
}

ofstream writeCSVFile(string envName, string defaultFile,string dumpDir,string defaultDir, int index){
    return writeFile(envName, defaultFile, dumpDir, defaultDir, index);
}

ofstream writeFile(string envName, string defaultFile,string dumpDir, string defaultDir, int csvIndex){
    try{
        char * envVarString = getenv(envName.c_str());
        string file = "";
        if(NULL == envVarString)
            file = defaultFile;
        else
            file = string(envVarString);
        DEBUGINFO("File2write: " << file);
        if(csvIndex > -1){//dumpCSV
            file = file + string("-") + to_string(csvIndex) + string(".csv");
            char * dumpDirectory = getenv(dumpDir.c_str());
            if(NULL != dumpDirectory){
                file = string(dumpDirectory)+string("/")+file;
            }else{
                file = defaultDir+file;
            }
        }
        ofstream f(file, ios_base::app | ios_base::out);
        if(!f){
            std::cerr << "WRITE ERROR: Cannot open "<< file << " !" << std::endl;
            exit(1);
        }
        return f;
    }
    catch(const std::exception& ex){
        std::cerr << "Exception: '" << ex.what() << "'!" << std::endl;
        exit(1);
    }
}

ifstream readFile(string envName, string defaultFile){
    try{
        char * envVarString = getenv(envName.c_str());
        string file;
        if(NULL == envVarString)
            file = defaultFile;
        else
            file = string(envVarString);
        DEBUGINFO("File2read: " << file);
        ifstream f(file);
        if(!f){
            std::cerr << "READ ERROR: Cannot open "<< file << " !"
                <<" envName: "<< envName << std::endl;
            exit(1);
        }
        return f;
    }
    catch(const std::exception& ex){
        std::cerr << "Exception: '" << ex.what() << "'!" << std::endl;
        exit(1);
    }
}
