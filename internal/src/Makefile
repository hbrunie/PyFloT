all: libprecisiontuning.so

include ../../make.def

libprecisiontuning.so: ../utils/Debug.o
	make -C ../utils/
	$(CXX) -c Strategy.cpp PrecisionTuner.cpp Profile.cpp DynFuncCall.cpp overloading.cpp -g $(DEBUG) -I. $(INCDIR)
	$(CXX) -o $@ ../utils/Debug.o Strategy.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o -g $(LIB) $(DEBUG) $(DYNLIB)
	mv $@ $(PUBLICLIB)

../utils/Debug.o:
	make all -C ../utils/

clean:
	rm -f *.o
