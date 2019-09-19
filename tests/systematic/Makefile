all: testManyCalls test1CallSiteMultipleDynCalls test1Call test2Calls

include ../../make.def

testManyCalls:
	$(CXX) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV2
	$(CXX) -o $@_v3 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV3
	$(CXX) -o $@_v4 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV4
	$(CXX) -o $@_v5 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV5

test1Call:
	$(CXX) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR)

test2Calls:
	$(CXX) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV2
	$(CXX) -o $@_v3 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV3
	$(CXX) -o $@_v4 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV4

test1CallSiteMultipleDynCalls:
	$(CXX) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV2
	$(CXX) -o $@_v3 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV3
	$(CXX) -o $@_v4 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV4 
	$(CXX) -o $@_v5 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV5
	$(CXX) -o $@_v6 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR)

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
	rm -rf test1Call_* test2Calls_* test1CallSiteMultipleDynCalls_* testManyCalls_*
