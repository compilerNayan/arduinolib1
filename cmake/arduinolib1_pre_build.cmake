# Helper CMake file to set up arduinolib1 pre-build script
# Include this file in your CMakeLists.txt after FetchContent_Populate(arduinolib1)
# Usage: include(${arduinolib1_SOURCE_DIR}/cmake/arduinolib1_pre_build.cmake)

if(NOT DEFINED arduinolib1_SOURCE_DIR)
    message(FATAL_ERROR "arduinolib1_SOURCE_DIR must be defined. Make sure to call this after FetchContent_Populate(arduinolib1)")
endif()

find_program(PYTHON_EXECUTABLE python3 python REQUIRED)

# Create the pre-build target
if(NOT TARGET arduinolib1_pre_build)
    add_custom_target(arduinolib1_pre_build
        COMMAND ${PYTHON_EXECUTABLE} 
            "${arduinolib1_SOURCE_DIR}/arduinolib1_scripts/arduinolib1_pre_build.py"
        WORKING_DIRECTORY ${arduinolib1_SOURCE_DIR}
        COMMENT "Running arduinolib1 pre-build script"
        VERBATIM
        ALL
    )
    message(STATUS "arduinolib1_pre_build target created")
endif()

