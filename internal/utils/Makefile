all: testDebug
include ../../make.def

testDebug:
	$(CXX) -c Debug.cpp testDebug.cpp -g $(DEBUG) -I. $(INCDIR)
	$(CXX) -o $@ Debug.o testDebug.o -g $(DEBUG) -I. $(INCDIR)

clean:
	rm -f *.o testDebug
