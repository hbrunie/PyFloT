cmake_minimum_required (VERSION 3.13)
project (pyflot
    VERSION 0.0.1
    LANGUAGES CXX
    )

set (CMAKE_CXX_STANDARD 11)
set (CMAKE_CXX_STANDARD_REQUIRED ON)

message (STATUS "CMAKE_BUILD_TYPE is ${CMAKE_BUILD_TYPE}")

# add compiler flags we always want to use
add_compile_options ("-Wall" "-Wextra" "-Wpedantic" "-O3" "-g" "-rdynamic" "-fPIC")

# set up possible commandline input variable defaults (override with -D)
option (PYFLOT_BUILD_TESTS "Build tests for PyFloT" ON)
option (BUILD_SHARED_LIBS "Build PyFloT as a shared Library" ON)

set(EXTERNAL_LIB_HEADERS external-deps/jsoncpp/include external-deps/GOTCHA/include)

#include (${CMAKE_SOURCE_DIR}/external-deps/gotcha.cmake)
#include (${CMAKE_SOURCE_DIR}/external-deps/jsoncpp.cmake)

###############################################################################
## Building PyFloT
#
# KEEP EVERYTHING LISTED IN ALPHABETICAL ORDER
#
# to add a component:
# 1) define the component in the components list
# 2) define any link dependencies if needed
###############################################################################
add_library (pyflot internal/src/Backtrace.cpp
    internal/src/Debug.cpp
    internal/src/DynFuncCall.cpp
    internal/src/Labels.cpp
    internal/src/PrecisionTuner.cpp
    internal/src/Profile.cpp
    internal/src/ShadowValue.cpp
    internal/src/Utils.cpp
    internal/src/overloading.cpp)
target_include_directories (pyflot PUBLIC public/include/ internal/include/ ${EXTERNAL_LIB_HEADERS})

###############################################################################
## Testing PyFloT
#
###############################################################################
if (PYFLOT_BUILD_TESTS)
    enable_testing ()

    # Define ctest tests and their executables
    #add_library (tests_general tests/tests_general.cpp)
    #target_link_libraries (tests_general PUBLIC Catch PRIVATE pyflot)
    #target_include_directories(tests_general PRIVATE ${CMAKE_BINARY_DIR})
    add_executable (test1Call tests/systematic/test1Call.cpp)
    target_include_directories (test1Call PRIVATE ${CMAKE_SOURCE_DIR}/public/include/)
    #target_include_directories (${component}-tests PRIVATE ${CMAKE_BINARY_DIR})
    target_link_libraries (test1Call PRIVATE pyflot)
    target_link_libraries (test1Call PRIVATE ${CMAKE_SOURCE_DIR}/external-deps/jsoncpp/build/src/lib_json/libjsoncpp.a)
    target_link_libraries (test1Call PRIVATE ${CMAKE_SOURCE_DIR}/external-deps/GOTCHA/build/src/libgotcha.so)


    add_test (NAME test1Call
        COMMAND test1Call
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR} )

else ()
    message (WARNING "warning: tests will not be built.")
endif ()
