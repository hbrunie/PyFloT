all: NBPBenchmarks systematic tutorial

NBPBenchmarks:
	make -C NBPBenchmarks

systematic:
	make -C systematic

tutorial:
	make -C tutorial

clean:
	make clean -C systematic
	make clean -C tutorial

cleanall: clean
	make cleanall -C systematic
	make cleanall -C tutorial

.PHONY: tutorial systematic
