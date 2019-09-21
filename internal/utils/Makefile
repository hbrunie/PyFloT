all: testDebug
include ../../make.def

testDebug:
	$(CXX) $(OPTIM) -c Debug.cpp testDebug.cpp -g $(DEBUG) -I. $(INCDIR) $(GCCDYNLIB)
	$(CXX) $(OPTIM) -o $@ Debug.o testDebug.o -g $(DEBUG) -I. $(INCDIR) $(DYNLIB)

clean:
	rm -f *.o testDebug
