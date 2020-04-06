#include <execinfo.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <iostream>
#include <zconf.h>
#include "regex"
#include "vector"

#include "Backtrace.hpp"
using namespace std;

string sh(string cmd) {
    array<char, 128> buffer;
    string result;
    shared_ptr<FILE> pipe(popen(cmd.c_str(), "r"), pclose);
    if (!pipe) throw runtime_error("popen() failed!");
    while (!feof(pipe.get())) {
        if (fgets(buffer.data(), 128, pipe.get()) != nullptr) {
            result += buffer.data();
        }
    }
    return result;
}

string addr2lineBacktrace(char * targetExecutable, string bt_sym) {
    regex re("\\[(.+)\\]");
    string execPath = string(targetExecutable);
    string addr;
    string res;
    smatch ms;
    if (regex_search(bt_sym, ms, re)) {
        string m = ms[1];
        addr = m;
    }
    string r = sh("addr2line -e " + execPath + " " + addr);
    return r;
}

vector<string> addr2lineBacktraceVec(char * targetExecutable, char ** bt_syms, size_t bt_size) {
    regex re("\\[(.+)\\]");
    string execPath = string(targetExecutable);
    string addrs = "";
    vector<string> strVec;
    for (size_t i = 1; i < bt_size; i++) {
        std::string sym = bt_syms[i];
        std::smatch ms;
        if (std::regex_search(sym, ms, re)) {
            std::string m = ms[1];
            addrs += " " + m;
        }
    }
    //string r = sh("addr2line -e " + execPath + " -f -C " + addrs);
    string r = sh("addr2line -e " + execPath + " " + addrs);
    stringstream ss(r);
    string token;
    while (getline(ss, token, '\n')) {
        strVec.push_back(token);
    }
    free(bt_syms);
    return strVec;
}
