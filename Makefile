all: lib unittest 

include make.def

lib:
	make -C external-deps
	make -C internal/src/

unittest:
	make -C ./tests

clean:
	make clean -C ./tests
	make clean -C ./internal/src
	make clean -C ./internal/utils

cleanall: clean
	rm -f ./public/lib/libprecisiontuning.so
	make cleanall -C ./tests
