all: libprecisiontuning.so

include ../../make.def

libprecisiontuning.so: ../utils/Debug.o
	make -C ../utils/
	$(CXX) $(CXXPTFLAGS) -c PrecisionTuner.cpp overloading.cpp Profile.cpp DynFuncCall.cpp -g $(DEBUG) -I. $(INCDIR) $(GCCDYNLIB) -I ../../external-deps/install/include/ -fpermissive
	$(CXX) $(CXXPTFLAGS) -o $@ ../utils/Debug.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o -g $(LIB) $(DEBUG) $(DYNLIB) -L ../../external-deps/install/lib64/ -lgotcha
	mkdir -p $(PTHOME)/public/lib/
	mv $@ $(PTHOME)/public/lib/

../utils/Debug.o:
	make all -C ../utils/

clean:
	rm -f *.o
