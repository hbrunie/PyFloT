all: libprecisiontuning.so

include ../../make.def
SOURCES=PrecisionTuner.cpp overloading.cpp Profile.cpp DynFuncCall.cpp Labels.cpp
OBJECTS=../utils/Debug.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o Labels.o
GOTCHALIB=-L ../../external-deps/install/lib64/ -lgotcha -Wl,-rpath, /global/cscratch1/sd/hbrunie/tools/precisiontuning/external-deps/install/lib64/
GOTCHAINC=-I ../../external-deps/install/include/
PTLabels= -I ../../public/include/
GOTCHAWARNING=-fpermissive

libprecisiontuning.so:
	make -C ../utils/
	$(CXX) $(CXXPTFLAGS) -c  -g $(DEBUG) $(SOURCES) -I. $(INCDIR) $(GCCDYNLIB) $(GOTCHAINC) $(GOTCHAWARNING) $(PTLabels)
	$(CXX) $(CXXPTFLAGS) -o $@ $(OBJECTS) -g $(LIB) $(DEBUG) $(DYNLIB) $(GOTCHALIB)
	mkdir -p $(PTHOME)/public/lib/
	mv $@ $(PTHOME)/public/lib/

../utils/Debug.o:
	make all -C ../utils/

clean:
	rm -f *.o
