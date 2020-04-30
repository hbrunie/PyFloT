all: test_backtrace

test_addr2line: test_addr2line.cpp
	g++ -g -rdynamic $^ ../../internal/src/Backtrace.cpp -o $@ -I ../../internal/include/

test_backtrace: test_backtrace.cpp ../../internal/src/Backtrace.cpp
	g++ -g -rdynamic $^ -o $@ -I ../../external-deps/libunwind/include/ -L ../../external-deps/libunwind/lib/ -lunwind  -I ../../internal/include/ -L ../../external-deps/libunwind/lib/ -lunwind-x86_64

clean:
	rm -f test_addr2line test_backtrace
.PHONY: test
