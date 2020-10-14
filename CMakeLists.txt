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

include(external-deps/external.cmake)

# set up possible commandline input variable defaults (override with -D)
option (PYFLOT_BUILD_TESTS "Build tests for PyFloT" ON)
option (BUILD_SHARED_LIBS "Build PyFloT as a shared Library" ON)

set(JSON_INC_PATH external-deps/jsoncpp/include)
set(GOTCHA_INC_PATH external-deps/GOTCHA/include)
get_target_property(JSON_INC_PATH jsoncpp_lib INTERFACE_INCLUDE_DIRECTORIES)
#include_directories(${JSON_INC_PATH})

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
add_library (pyflot SHARED internal/src/Backtrace.cpp
    internal/src/Debug.cpp
    internal/src/DynFuncCall.cpp
    internal/src/Labels.cpp
    internal/src/PrecisionTuner.cpp
    internal/src/Profile.cpp
    internal/src/ShadowValue.cpp
    internal/src/Utils.cpp
    internal/src/overloading.cpp)
target_include_directories (pyflot PUBLIC public/include/ internal/include/ ${GOTCHA_INC_PATH} ${JSON_INC_PATH})
target_link_libraries (pyflot jsoncpp_lib gotcha)
target_compile_definitions(pyflot PRIVATE -DDUMP)

###############################################################################
## Testing PyFloT
#
###############################################################################
if (PYFLOT_BUILD_TESTS)
    enable_testing ()
    add_subdirectory(tests)

else ()
    message (WARNING "warning: tests will not be built.")
endif ()
