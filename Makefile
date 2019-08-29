all: execinfo

include make.def

execinfo:
	$(CXX) -c PrecisionTuner.cpp -g $(DEBUG) -I.
	$(CXX) -c main.cpp -DUSE_EXECINFO -g $(DEBUG) -I.
	$(CXX) -o nounwind main.o PrecisionTuner.o -g -lm $(DEBUG) -I.

test:
	$(CXX) main.cpp -lm $(DEBUG) 

clean:
	rm -f libmybacktrace.so test a.out unwind nounwind *.json trace.txt *.o
