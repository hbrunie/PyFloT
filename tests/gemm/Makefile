all: gemm gemm-pyflot

include ../../make.def
CXX=CC
gemm:
	$(CXX) -c testDGEMM.cpp -g $(DEBUG)
	$(CXX) -o $@  testDGEMM.o -g  $(DEBUG) -lopenblas

gemm-pyflot:
	$(CXX) -O0 -c testDGEMM.cpp -g $(DEBUG) $(PTINCDIR) -rdynamic
	$(CXX) -o $@  testDGEMM.o -g $(PTLIB) $(DEBUG)  -rdynamic -lopenblas

clean:
	rm -f *.o

cleanall: clean
	rm -f gemm gemm-pyflot

.PHONY: unittest
