cmake_minimum_required(VERSION 3.14)
project(freecad_adaptive_clearing LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

if(NOT pybind11_DIR)
    execute_process(
        COMMAND python3 -c "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE _pybind11_cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    if(_pybind11_cmake_dir)
        set(pybind11_DIR "${_pybind11_cmake_dir}" CACHE PATH "pybind11 CMake directory")
    endif()
endif()

# scikit-build-core integration
if(DEFINED SKBUILD)
    set(PYTHON_PACKAGE_DIR "${SKBUILD_PLATLIB_DIR}/freecad_adaptive_clearing")
else()
    set(PYTHON_PACKAGE_DIR ".")
endif()

# Paths to FreeCAD source files (relative to this CMakeLists.txt)
set(FREECAD_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/..")
set(LIBAREA_DIR  "${FREECAD_ROOT}/src/Mod/CAM/libarea")
set(CLIPPER2_DIR "${FREECAD_ROOT}/src/3rdParty/Clipper2")

# Generate the Clipper2 version header that FreeCAD normally creates while
# configuring its full build. Keep it in this standalone build tree so users do
# not need to build FreeCAD first and the source checkout remains untouched.
file(STRINGS "${CLIPPER2_DIR}/CMakeLists.txt" CLIPPER2_PROJECT_LINE
    REGEX "^project\\(Clipper2 VERSION [0-9]+\\.[0-9]+\\.[0-9]+"
)
string(REGEX REPLACE ".*VERSION[ \\t]+([^ )]+).*" "\\1" CLIPPER2_VERSION "${CLIPPER2_PROJECT_LINE}")
if(NOT CLIPPER2_VERSION)
    message(FATAL_ERROR "Could not determine Clipper2 version from ${CLIPPER2_DIR}/CMakeLists.txt")
endif()

set(CLIPPER2_GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated/Clipper2Lib/include")
set(_freecad_adaptive_clearing_project_version "${PROJECT_VERSION}")
set(PROJECT_VERSION "${CLIPPER2_VERSION}")
configure_file(
    "${CLIPPER2_DIR}/clipper.version.in"
    "${CLIPPER2_GENERATED_INCLUDE_DIR}/clipper2/clipper.version.h"
    @ONLY
    NEWLINE_STYLE UNIX
)
set(PROJECT_VERSION "${_freecad_adaptive_clearing_project_version}")

# Clipper1
add_library(clipper1 STATIC ${LIBAREA_DIR}/clipper.cpp)
target_include_directories(clipper1 PUBLIC ${LIBAREA_DIR})

# Clipper2 (FreeCAD's bundled copy, with USINGZ)
set(CLIPPER2_SRC
    ${CLIPPER2_DIR}/Clipper2Lib/src/clipper.engine.cpp
    ${CLIPPER2_DIR}/Clipper2Lib/src/clipper.offset.cpp
    ${CLIPPER2_DIR}/Clipper2Lib/src/clipper.rectclip.cpp
    ${CLIPPER2_DIR}/Clipper2Lib/src/clipper.triangulation.cpp
)
add_library(clipper2z STATIC ${CLIPPER2_SRC})
target_include_directories(clipper2z PUBLIC
    ${CLIPPER2_GENERATED_INCLUDE_DIR}
    ${CLIPPER2_DIR}/Clipper2Lib/include
)
target_compile_definitions(clipper2z PUBLIC USINGZ)

# Adaptive clearing
add_library(freecad_adaptive_clearing STATIC ${LIBAREA_DIR}/Adaptive.cpp)
target_include_directories(freecad_adaptive_clearing PUBLIC ${LIBAREA_DIR})
target_link_libraries(freecad_adaptive_clearing PUBLIC clipper1 clipper2z)

# Python bindings
find_package(pybind11 REQUIRED)
pybind11_add_module(_freecad_adaptive_clearing bindings.cpp)
target_link_libraries(_freecad_adaptive_clearing PRIVATE freecad_adaptive_clearing)

# Install the .so — when building via pip this goes to site-packages,
# when building manually this goes to build/ where __init__.py finds it.
install(TARGETS _freecad_adaptive_clearing DESTINATION "${PYTHON_PACKAGE_DIR}")

# Install Python sources and typing metadata alongside the .so (for pip install)
install(FILES __init__.py _freecad_adaptive_clearing.pyi py.typed DESTINATION "${PYTHON_PACKAGE_DIR}")
