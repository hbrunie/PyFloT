all: libprecisiontuning.so

include ../../make.def

libprecisiontuning.so: ../utils/Debug.o
	make -C ../utils/
	$(CXX) $(OPTIM) -c PrecisionTuner.cpp Profile.cpp DynFuncCall.cpp overloading.cpp -g $(DEBUG) -I. $(INCDIR)
	$(CXX) $(OPTIM) -o $@ ../utils/Debug.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o -g $(LIB) $(DEBUG) $(DYNLIB)
	mv $@ $(PUBLICLIB)

../utils/Debug.o:
	make all -C ../utils/

clean:
	rm -f *.o
