#ifndef DEBUG_H
#define DEBUG_H

#ifndef NDEBUG

#include <iostream>
  extern bool DebugFlag;

  void debugtypeOption(char *env);
  bool isCurrentDebugType(const char *type);

  void setCurrentDebugType(const char *type);

#define DEBUG(TYPE, X)					\
  do {if (DebugFlag && isCurrentDebugType(TYPE)) { X; }	\
  } while (0)

#define DEBUGG(TYPE, X) DEBUG(TYPE,std::cerr << __FUNCTION__<< ": " << X << endl;);
#define DEBUGINFO(X) DEBUGG("info",X);

#else
//#define isCurrentDebugType(X) (false)
//#define setCurrentDebugType(X)
#define DEBUG(TYPE, X) do { } while (0)
#define DEBUGG(TYPE, X) do { } while (0)
#define DEBUGINFO(X) do { } while (0)

#endif /* NDEBUG */
#define UNUSED(expr) do { (void)(expr); } while (0)
#define ATTRIBUTE_UNUSED __attribute__((unused))

#endif /* DEBUG_H */
