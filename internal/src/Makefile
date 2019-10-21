all: libprecisiontuning.so

include ../../make.def

libprecisiontuning.so: ../utils/Debug.o
	make -C ../utils/
	$(CXX) $(CXXPTFLAGS) -c PrecisionTuner.cpp Profile.cpp DynFuncCall.cpp overloading.cpp -g $(DEBUG) -I. $(INCDIR) $(GCCDYNLIB)
	$(CXX) $(CXXPTFLAGS) -o $@ ../utils/Debug.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o -g $(LIB) $(DEBUG) $(DYNLIB)
	mkdir -p $(PTHOME)/public/lib/
	mv $@ $(PTHOME)/public/lib/

../utils/Debug.o:
	make all -C ../utils/

clean:
	rm -f *.o
