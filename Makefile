all: unittest lib

include make.def

lib:
	make -C internal/src/

unittest:
	make -C ./tests

clean:
	make clean -C ./tests
	make clean -C ./internal/src

cleanall: clean
	rm -f ./public/lib/libprecisiontuning.so
	make cleanall -C ./tests
