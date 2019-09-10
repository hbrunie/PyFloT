all: test1Call

include ../../make.def

test1Call:
	$(CXX) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR)

test2Call:
	$(CXX) -c $@.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ $@.o -g $(PTLIB) $(DEBUG)
	mv $@ $@_v2

test2StaticCalls:
	$(CXX) -c $@.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ $@.o -g $(PTLIB) $(DEBUG)

test2DynamicCalls:
	$(CXX) -c $@.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ $@.o -g $(PTLIB) $(DEBUG)

test4Calls2Static2Dynamic:
	$(CXX) -c $@.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ $@.o -g $(PTLIB) $(DEBUG)

clean:
	rm -f *.o

cleanall: clean
	rm -f test1Call_v1 test1Call_v2 test1Call_v1.dSYM test1Call_v1.dSYM

