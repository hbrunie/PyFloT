#include <stdlib.h>
#include <vector>
#define BACKTRACE_MAX 1024

std::vector<std::string> addr2lineBacktraceVec(std::string targetExecutable, std::vector<std::string> bt_syms, size_t bt_size);
std::string addr2lineBacktrace(char * targetExecutable, std::string bt_sym);
