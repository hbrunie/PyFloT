all: testManyCallsExp testManyCalls test1CallSiteMultipleDynCalls test1Call test2Calls

testManyCallsExp:
	$(CXX) $(CXXFLAGS) -o $@_$(DEBUG)_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) $(CXXFLAGS) -o $@_$(DEBUG)_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV2
	$(CXX) $(CXXFLAGS) -o $@_$(DEBUG)_v3 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV3
	$(CXX) $(CXXFLAGS) -o $@_$(DEBUG)_v4 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV4
	$(CXX) $(CXXFLAGS) -o $@_$(DEBUG)_v5 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV5

testManyCalls:
	$(CXX) $(CXXFLAGS) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) $(CXXFLAGS) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV2
	$(CXX) $(CXXFLAGS) -o $@_v3 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV3
	$(CXX) $(CXXFLAGS) -o $@_v4 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV4
	$(CXX) $(CXXFLAGS) -o $@_v5 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV5

test1Call:
	$(CXX) $(CXXFLAGS) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) $(CXXFLAGS) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR)

test2Calls:
	$(CXX) $(CXXFLAGS) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) $(CXXFLAGS) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV2
	$(CXX) $(CXXFLAGS) -o $@_v3 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV3
	$(CXX) $(CXXFLAGS) -o $@_v4 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV4

test1CallSiteMultipleDynCalls:
	$(CXX) $(CXXFLAGS) -o $@_v1 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV1
	$(CXX) $(CXXFLAGS) -o $@_v2 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV2
	$(CXX) $(CXXFLAGS) -o $@_v3 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV3
	$(CXX) $(CXXFLAGS) -o $@_v4 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV4
	$(CXX) $(CXXFLAGS) -o $@_v5 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR) -DV5
	$(CXX) -o $@_v6 $@.cpp -g $(PTLIB) $(DEBUG) $(PTINCDIR)

test2StaticCalls:
	$(CXX) $(CXXFLAGS) -c $@.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) $(CXXFLAGS) -o $@ $@.o -g $(PTLIB) $(DEBUG)

test2DynamicCalls:
	$(CXX) $(CXXFLAGS) -c $@.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) $(CXXFLAGS) -o $@ $@.o -g $(PTLIB) $(DEBUG)

test4Calls2Static2Dynamic:
	$(CXX) $(CXXFLAGS) -c $@.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) $(CXXFLAGS) -o $@ $@.o -g $(PTLIB) $(DEBUG)

clean:
	rm -f *.o

cleanall: clean
	rm -rf test1Call_* test2Calls_* test1CallSiteMultipleDynCalls_* testManyCalls_* testManyCallsExp_*
