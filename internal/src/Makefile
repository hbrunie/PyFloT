include ../../make.def
SOURCES=PrecisionTuner.cpp overloading.cpp Profile.cpp DynFuncCall.cpp Labels.cpp Utils.cpp ShadowValue.cpp
OBJECTS=Backtrace.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o Labels.o Utils.o ShadowValue.o ../utils/Debug.o
GOTCHALIB=-L ../../external-deps/install/lib64/ -lgotcha -Wl,-rpath, /global/cscratch1/sd/hbrunie/tools/precisiontuning/external-deps/install/lib64/
GOTCHAINC=-I ../../external-deps/install/include/
PTLabels= -I ../../public/include/
GOTCHAWARNING=-fpermissive
OPTION=-DUSE_TIMESTAMP

libprecisiontuning.so: $(OBJECTS)
	make -C ../utils/
	$(CXX) $(CXXPTFLAGS) -o $@ $^ -g $(LIB) $(DEBUG) $(DYNLIB) $(GOTCHALIB)
	mkdir -p $(PTHOME)/public/lib/
	mv $@ $(PTHOME)/public/lib/

%.o:%.cpp
	$(CXX) $(CXXPTFLAGS) -c $^ -g $(DEBUG) -I. $(INCDIR) $(GCCDYNLIB) $(GOTCHAINC) $(GOTCHAWARNING) $(PTLabels) $(OPTION)

#$(CXX) $(CXXPTFLAGS) -c  -g $(DEBUG) $(SOURCES) -I. $(INCDIR) $(GCCDYNLIB) $(GOTCHAINC) $(GOTCHAWARNING) $(PTLabels)

../utils/Debug.o:
	make all -C ../utils/

cleanutils:
	make clean -C ../utils/

clean: cleanutils
	rm -f *.o
