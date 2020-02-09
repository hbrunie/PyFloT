#ifndef UTILS_H
#define UTILS_H

#include <cstdio>
#include <cstdlib>
#include <fstream>

using namespace std;

ifstream readFile(string envName, string defaultFile);
ofstream writeCSVFile(string envName, string defaultFile, int index);
ofstream writeJSONFile(string envName, string defaultFile);
#endif
