message(STATUS "Installing jsoncpp via submodule")
execute_process(COMMAND git submodule update --init -- external-deps/jsoncpp
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
add_subdirectory(external-deps/jsoncpp EXCLUDE_FROM_ALL)
message(STATUS "Installing gotcha via submodule")
execute_process(COMMAND git submodule update --init -- external-deps/GOTCHA
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
add_subdirectory(external-deps/GOTCHA EXCLUDE_FROM_ALL)
