# This file runs automatically when CMake processes this directory
# It ensures the pre-build script runs even if the main CMakeLists.txt isn't used

# Only run once per CMake run
if(NOT DEFINED ARDUINOLIB1_PRE_BUILD_RUN)
    set(ARDUINOLIB1_PRE_BUILD_RUN TRUE CACHE INTERNAL "")
    
    find_program(PYTHON_EXECUTABLE python3 python)
    if(PYTHON_EXECUTABLE AND EXISTS "${CMAKE_CURRENT_LIST_DIR}/arduinolib1_scripts/arduinolib1_pre_build.py")
        execute_process(
            COMMAND ${PYTHON_EXECUTABLE} 
                "${CMAKE_CURRENT_LIST_DIR}/arduinolib1_scripts/arduinolib1_pre_build.py"
            WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
            RESULT_VARIABLE PRE_BUILD_RESULT
            OUTPUT_VARIABLE PRE_BUILD_OUTPUT
            ERROR_VARIABLE PRE_BUILD_ERROR
            ERROR_QUIET
        )
        if(PRE_BUILD_OUTPUT)
            message(STATUS "arduinolib1 pre-build: ${PRE_BUILD_OUTPUT}")
        endif()
    endif()
endif()

