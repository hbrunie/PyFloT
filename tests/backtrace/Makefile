all: test_addr2line test_backtrace

test_addr2line: test_addr2line.cpp
	g++ -g -rdynamic $^ ../../internal/src/Backtrace.cpp -o $@ -I ../../internal/include/

test_backtrace: test_backtrace.cpp
	g++ -g -rdynamic $^ -o $@ -I ../../external-deps/libbacktrace/build/include/ -L ../../external-deps/libbacktrace/build/lib/ -lbacktrace

clean:
	rm -f test_addr2line
.PHONY: test
