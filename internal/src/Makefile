include ../../make.def
SOURCES=PrecisionTuner.cpp overloading_dgemm.cpp Profile.cpp DynFuncCall.cpp Labels.cpp Utils.cpp ShadowValue.cpp
OBJECTS=Backtrace.o Profile.o PrecisionTuner.o DynFuncCall.o overloading_dgemm.o Labels.o Utils.o ShadowValue.o Debug.o
GOTCHAWARNING=-fpermissive

libprecisiontuning.so: $(OBJECTS)
	$(CXX) $(CXXPTFLAGS) -o $@ $^ -g $(LIB) $(DEBUG) $(DYNLIB)  -L/usr/lib64/ -lopenblas
	mkdir -p $(PTHOME)/public/lib/
	mv $@ $(PTHOME)/public/lib/

%.o:%.cpp
	$(CXX) $(CXXPTFLAGS) -c $^ -g $(DEBUG) -I. $(INCDIR) $(GCCDYNLIB) $(GOTCHAWARNING)

clean:
	rm -f *.o
