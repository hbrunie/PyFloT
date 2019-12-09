all: testExp test5Exp

include ../../make.def

testExp:
	$(CXX) -c testExp.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ testExp.o -g $(DEBUG) $(PTLIB) -rdynamic

test5Exp:
	$(CXX) -c test5Exp.cpp -g $(DEBUG) $(PTINCDIR)
	$(CXX) -o $@ test5Exp.o -g $(DEBUG) $(PTLIB) -rdynamic

clean:
	rm -f *.o

cleanall: clean
	rm -f testExp test5Exp
