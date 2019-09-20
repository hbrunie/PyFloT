all: NBPBenchmarks systematic trivial

NBPBenchmarks:
	make -C NBPBenchmarks

systematic:
	make -C systematic
	
trivial:
	make -C trivial

clean:
	make clean -C systematic
	make clean -C trivial

cleanall: clean
	make cleanall -C systematic
	make cleanall -C trivial

.PHONY: trivial
