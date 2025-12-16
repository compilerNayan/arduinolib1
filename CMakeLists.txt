cmake_minimum_required(VERSION 3.14)
project(arduinolib1 VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Create header-only library (INTERFACE library)
add_library(arduinolib1 INTERFACE)

# Set target properties
set_target_properties(arduinolib1 PROPERTIES
    VERSION ${PROJECT_VERSION}
    INTERFACE_INCLUDE_DIRECTORIES
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<INSTALL_INTERFACE:include>
)

# Add header file to the library
target_sources(arduinolib1 INTERFACE
    FILE_SET HEADERS
    BASE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}
    FILES
        src/NayanMath.h
)

# Optional: Set up installation
include(GNUInstallDirs)

install(TARGETS arduinolib1
    EXPORT arduinolib1Targets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(FILES src/NayanMath.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT arduinolib1Targets
    FILE arduinolib1Targets.cmake
    NAMESPACE arduinolib1::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/arduinolib1
)

# Optional: Create a config file for find_package support
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arduinolib1Config.cmake.in")
    include(CMakePackageConfigHelpers)

    configure_package_config_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arduinolib1Config.cmake.in"
        "${CMAKE_CURRENT_BINARY_DIR}/arduinolib1Config.cmake"
        INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/arduinolib1
    )

    write_basic_package_version_file(
        "${CMAKE_CURRENT_BINARY_DIR}/arduinolib1ConfigVersion.cmake"
        VERSION ${PROJECT_VERSION}
        COMPATIBILITY AnyNewerVersion
    )

    install(FILES
        "${CMAKE_CURRENT_BINARY_DIR}/arduinolib1Config.cmake"
        "${CMAKE_CURRENT_BINARY_DIR}/arduinolib1ConfigVersion.cmake"
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/arduinolib1
    )
endif()

