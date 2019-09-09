all: testExp testMathFunctions testConstructor testHeader

include ../make.def

testMathFunctions:
	$(CXX) -c testMathFunctions.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@  testMathFunctions.o -g $(PTLIB) $(DEBUG)

testExp:
	$(CXX) -c testExp.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ testExp.o -g $(PTLIB) $(DEBUG)

testHeader:
	$(CXX) -c testHeader.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ testHeader.o -g $(PTLIB) $(DEBUG)

testConstructor:
	$(CXX) -c testConstructor.cpp -g $(DEBUG) $(INCDIR)
	$(CXX) -o $@ testConstructor.o -g $(PTLIB) $(DEBUG)

clean:
	rm -f *.o

cleanall: clean
	rm -f testConstructor testHeader testMathFunctions testExp

.PHONY: unittest
