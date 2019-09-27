#ifndef DEBUG_H
#define DEBUG_H

#ifndef NDEBUG

  extern bool DebugFlag;

  void debugtypeOption(char *env);
  bool isCurrentDebugType(const char *type);

  void setCurrentDebugType(const char *type);

#define DEBUG(TYPE, X)					\
  do {if (DebugFlag && isCurrentDebugType(TYPE)) { X; }	\
  } while (0)

#else
//#define isCurrentDebugType(X) (false)
//#define setCurrentDebugType(X)
#define DEBUG(TYPE, X) do { } while (0)

#endif /* NDEBUG */
#define UNUSED(expr) do { (void)(expr); } while (0)

#endif /* DEBUG_H */
