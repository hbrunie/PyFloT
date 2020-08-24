###############################################################################
## GOTCHA
#
###############################################################################
if (PYFLOT_USE_GOTCHA)
    # grab gprof2dot (we don't store it in the repo or distribute)
    set (gotcha_PATH ${CMAKE_SOURCE_DIR}/external-deps/GOTCHA)
    if (NOT EXISTS ${gprof2dot_PATH}/lib/libgotcha.so)
      message (STATUS "gotcha not found. downloading")
      include (ExternalProject)
      ExternalProject_Add (gotcha-ext
        UPDATE_COMMAND ""
        SOURCE_DIR ${flamegraph_PATH}
        GIT_REPOSITORY https://github.com/LLNL/GOTCHA.git
        GIT_PROGRESS 1
        GIT_SHALLOW 1
        UPDATE_COMMAND ""
        CONFIGURE_COMMAND ""
        BUILD_COMMAND ""
        INSTALL_COMMAND ""
      )
    else ()
      message (STATUS "using gotcha found at ${gotcha_PATH}")
    endif ()
endif ()
