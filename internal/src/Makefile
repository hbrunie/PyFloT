all: libprecisiontuning.so

include ../../make.def

libprecisiontuning.so: ../utils/Debug.o
	make -C ../utils/
	$(CXX) -O3 -c PrecisionTuner.cpp Profile.cpp DynFuncCall.cpp overloading.cpp -g $(DEBUG) -I. $(INCDIR)
	$(CXX) -O3 -o $@ ../utils/Debug.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o -g $(LIB) $(DEBUG) $(DYNLIB)
	mv $@ $(PUBLICLIB)

../utils/Debug.o:
	make all -C ../utils/

clean:
	rm -f *.o
