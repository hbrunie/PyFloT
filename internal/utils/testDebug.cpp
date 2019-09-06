#include <cstdlib>
#include <cstdio>

#include "Debug.hpp"

int main(int argc, char * argv []){
    debugtypeOption(getenv("DEBUG"));
    DEBUG("warning", printf("toto"););
    DEBUG("info", printf("blabla"););
    return 0;
}
