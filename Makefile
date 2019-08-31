all: unittest

include make.def

execinfo:
	$(CXX) -c PrecisionTuner.cpp -g $(DEBUG) -I.
	$(CXX) -c main.cpp -DUSE_EXECINFO -g $(DEBUG) -I.
	$(CXX) -o nounwind main.o PrecisionTuner.o -g -lm $(DEBUG) -I.

unittest:
	$(CXX) -c PrecisionTuner.cpp -g $(DEBUG) -I. $(INCLUDEDIR)
	$(CXX) -c testJson.cpp -g $(DEBUG) -I.
	$(CXX) -o $@ testJson.o PrecisionTuner.o -g $(DEBUG) -I. $(LIB)

test:
	$(CXX) main.cpp -lm $(DEBUG) 

clean:
	rm -f *.o

cleanall: clean
	rm -f test unittest execinfo

.PHONY: unittest
