#include <cstdlib>
#include <cstdio>

#include "Debug.hpp"

int main(){
    debugtypeOption(getenv("DEBUG"));
    DEBUG("warning", printf("toto"););
    DEBUG("info", printf("blabla"););
    return 0;
}
