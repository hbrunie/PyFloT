#include <cstdlib>
#include <cstdio>

#include "Debug.hpp"

int main(){
#ifndef NDEBUG
    debugtypeOption(getenv("DEBUG"));
    DEBUG("warning", printf("toto"););
    DEBUG("info", printf("blabla"););
#endif
    return 0;
}
