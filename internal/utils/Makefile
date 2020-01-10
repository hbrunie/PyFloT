all: testDebug
include ../../make.def

testDebug:
	$(CXX) $(CXXPTFLAGS) -c Debug.cpp testDebug.cpp -g $(DEBUG) -I. $(INCDIR) $(GCCDYNLIB)
	$(CXX) $(CXXPTFLAGS) -o $@ Debug.o testDebug.o -g $(DEBUG) -I. $(INCDIR)

clean:
	rm -f *.o testDebug
