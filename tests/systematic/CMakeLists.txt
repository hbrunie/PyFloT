# Define ctest tests and their executables
#add_library (tests_general tests/tests_general.cpp)
#target_link_libraries (tests_general PUBLIC Catch PRIVATE pyflot)
#target_include_directories(tests_general PRIVATE ${CMAKE_BINARY_DIR})
add_executable (test1Call test1Call.cpp)
target_link_libraries (test1Call PRIVATE pyflot)


add_test (NAME test1Call
    COMMAND test1Call
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR} )

