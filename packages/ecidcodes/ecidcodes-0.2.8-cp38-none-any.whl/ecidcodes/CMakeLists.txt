cmake_minimum_required(VERSION 3.18)
project(ecidcodes LANGUAGES CXX)

# Enforce modern behavior
if(POLICY CMP0148)
  cmake_policy(SET CMP0148 NEW)
endif()

include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.12.0
)
FetchContent_MakeAvailable(pybind11)


set(CMAKE_INSTALL_RPATH "$ORIGIN")
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
#find_package(pybind11 REQUIRED)
# Define Python modules with absolute paths
pybind11_add_module(idcodes             ${CMAKE_CURRENT_SOURCE_DIR}/pybind_idcodes.cpp)
pybind11_add_module(idcodes_gf          ${CMAKE_CURRENT_SOURCE_DIR}/encoder/gf/gf.cpp)
pybind11_add_module(idcodes_rmid        ${CMAKE_CURRENT_SOURCE_DIR}/encoder/rmid/rmid.cpp)
pybind11_add_module(idcodes_rs2id       ${CMAKE_CURRENT_SOURCE_DIR}/encoder/rs2id/rs2id.cpp)
pybind11_add_module(idcodes_rsid        ${CMAKE_CURRENT_SOURCE_DIR}/encoder/rsid/rsid.cpp)
pybind11_add_module(idcodes_sha256id    ${CMAKE_CURRENT_SOURCE_DIR}/encoder/sha256id/sha256id.cpp)
pybind11_add_module(idcodes_sha1id      ${CMAKE_CURRENT_SOURCE_DIR}/encoder/sha1id/sha1id.cpp)
pybind11_add_module(idcodes_pmhid       ${CMAKE_CURRENT_SOURCE_DIR}/encoder/pmhid/pmhid.cpp)

# Include directories
set(ALL_MODULES idcodes
        idcodes_gf
        idcodes_rmid
        idcodes_rs2id
        idcodes_rsid idcodes_sha1id
        idcodes_sha256id
        idcodes_pmhid)
foreach(target IN LISTS ALL_MODULES)
    target_include_directories(${target} PRIVATE ${PROJECT_SOURCE_DIR}/../include)
    target_link_libraries(${target} PRIVATE ssl crypto boost_program_options IdcodesLibrary)
    set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}")
endforeach()

    # Check if VIRTUAL_ENV is set
    if(DEFINED ENV{VIRTUAL_ENV})
        set(PYTHON_EXECUTABLE "$ENV{VIRTUAL_ENV}/bin/python")
        message(STATUS "Using Python from activated virtual environment: ${PYTHON_EXECUTABLE}")
    else()
        # Try common virtual environment locations
        if(EXISTS "${CMAKE_SOURCE_DIR}/.venv/bin/python")
            set(PYTHON_EXECUTABLE "${CMAKE_SOURCE_DIR}/.venv/bin/python")
            message(STATUS "Using Python from .venv directory: ${PYTHON_EXECUTABLE}")
        elseif(EXISTS "${CMAKE_SOURCE_DIR}/.venv/bin/python")
            set(PYTHON_EXECUTABLE "${CMAKE_SOURCE_DIR}/.venv/bin/python")
            message(STATUS "Using Python from venv directory: ${PYTHON_EXECUTABLE}")
        else()
            # Fall back to system Python
            set(PYTHON_EXECUTABLE "${Python_EXECUTABLE}")
            message(STATUS "Using system Python: ${PYTHON_EXECUTABLE}")
        endif()
    endif()

# Detect Python site-packages directory
message(STATUS "Python executable found in inner cmakelists.txt: ${PYTHON_EXECUTABLE}")
execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "import site; print(site.getsitepackages()[0])"
    OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Python site-packages directory: ${PYTHON_SITE_PACKAGES}")


# Fallback for PYTHON_SITE_PACKAGES if detection fails

# Install all modules into a subdirectory named 'ecidcodes' inside site-packages
install(TARGETS ${ALL_MODULES}
    LIBRARY DESTINATION ecidcodes
    ARCHIVE DESTINATION ecidcodes
    RUNTIME DESTINATION ecidcodes
)

# Install empty __init__.py to make 'ecidcodes' a valid Python package
#file(WRITE ${CMAKE_BINARY_DIR}/__init__.py "")

#install(FILES ${CMAKE_BINARY_DIR}/__init__.py DESTINATION ${PYTHON_SITE_PACKAGES}/ecidcodes)
