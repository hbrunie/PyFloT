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

ofstream writeFile(string envName, string defaultFile, int csvIndex);

ofstream writeJSONFile(string envName, string defaultFile){
    return writeFile(envName, defaultFile, -1);
}

ofstream writeCSVFile(string envName, string defaultFile, int index){
    return writeFile(envName, defaultFile, index);
}

ofstream writeFile(string envName, string defaultFile, int csvIndex){
    try{
        char * envVarString = getenv(envName.c_str());
        string file;
        if(NULL == envVarString)
            file = defaultFile;
        else
            file = string(envVarString);
        DEBUGINFO("File2write: " << file);
        if(csvIndex > -1)//dumpCSV
            file = file + string("-") + to_string(csvIndex) + string(".csv");

        ofstream f(file, ios_base::app | ios_base::out);
        if(!f){
            std::cerr << "ERROR: Cannot open "<< file << " !" << std::endl;
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
    //std::ifstream infile(fileAbsPath, std::ifstream::binary);
    //if(!stream_check(infile)){
    //    cerr << __FUNCTION__ << " wrong path for file: " << fileAbsPath << endl;
    //    exit(-1);
    //}
        if(NULL == envVarString)
            file = defaultFile;
        else
            file = string(envVarString);
        DEBUGINFO("File2read: " << file);
        ifstream f(file);
        if(!f){
            std::cerr << "ERROR: Cannot open "<< file << " !" << std::endl;
            exit(1);
        }
        return f;
    }
    catch(const std::exception& ex){
        std::cerr << "Exception: '" << ex.what() << "'!" << std::endl;
        exit(1);
    }
}
