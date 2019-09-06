all: libprecisiontuning.so

include ../../make.def

libprecisiontuning.so:
	$(CXX) -c PrecisionTuner.cpp DynFuncCall.cpp overloading.cpp -g $(DEBUG) -I. $(INCDIR)
	$(CXX) -o $@ PrecisionTuner.o DynFuncCall.o overloading.o -g $(LIB) $(DEBUG) $(DYNLIB)
	mv $@ $(PUBLICLIB)

clean:
	rm -f *.o
