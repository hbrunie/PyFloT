#ifndef DEBUG_H
#define DEBUG_H
#include <iostream>
#include <vector>

#ifndef NDEBUG
#define DEBUG(TYPE, X)					\
  do {if (debug.DebugFlag && debug.isCurrentDebugType(TYPE)) { X; }	\
  } while (0)
#define DEBUGG(TYPE, X) DEBUG(TYPE,std::cerr << __FUNCTION__<< ": " << X << endl;);
#define DEBUGINFO(X) DEBUGG("info",X);

class Debug
{

    private:
        std::vector<std::string> CurrentDebugType;
        void setCurrentDebugType(const char *type);
    public:
        Debug();
        void debugtypeOption(char *env);
        bool DebugFlag = false;
        bool isCurrentDebugType(const char *type);
};

#else

#define DEBUG(TYPE, X) do { } while (0)
#define DEBUGG(TYPE, X) do { } while (0)
#define DEBUGINFO(X) do { } while (0)

#endif /* NDEBUG */
#define UNUSED(expr) do { (void)(expr); } while (0)
#define ATTRIBUTE_UNUSED __attribute__((unused))

#endif /* DEBUG_H */
