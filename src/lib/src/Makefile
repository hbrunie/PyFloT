include ../../make.def
SOURCES=PrecisionTuner.cpp overloading.cpp Profile.cpp DynFuncCall.cpp Labels.cpp Utils.cpp ShadowValue.cpp
OBJECTS=Backtrace.o Profile.o PrecisionTuner.o DynFuncCall.o overloading.o Labels.o Utils.o ShadowValue.o ../utils/Debug.o
GOTCHAWARNING=-fpermissive

libprecisiontuning.so: $(OBJECTS)
	make -C ../utils/
	$(CXX) $(CXXPTFLAGS) -o $@ $^ -g $(LIB) $(DEBUG) $(DYNLIB)
	mkdir -p $(PTHOME)/public/lib/
	mv $@ $(PTHOME)/public/lib/

%.o:%.cpp
	$(CXX) $(CXXPTFLAGS) -c $^ -g $(DEBUG) -I. $(INCDIR) $(GCCDYNLIB) $(GOTCHAWARNING)

../utils/Debug.o:
	make all -C ../utils/

cleanutils:
	make clean -C ../utils/

clean: cleanutils
	rm -f *.o
