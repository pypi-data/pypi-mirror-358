cmake_minimum_required(VERSION 3.13)
project(pyqbf VERSION 1.1)

cmake_policy(SET CMP0079 NEW)

include(GNUInstallDirs)

if(DEBUG_ENABLE_ADDRESS_SANITIZER)
    set (CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address,undefined")
    set (CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address,undefined")
    set (CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address,undefined")
    message(WARNING "When using ASAN, QuAPI may behave unexpectedly!")
endif()

set(CMAKE_CXX_STANDARD 17)

add_subdirectory(src)

add_subdirectory(third_party)

find_package(Python 3.8 COMPONENTS Interpreter Development.Module REQUIRED)

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

nanobind_add_module(pyqbf_cpp ${SRCS})
target_link_libraries(pyqbf_cpp PRIVATE qdpll)
target_link_libraries(pyqbf_cpp PRIVATE qute)
target_link_libraries(pyqbf_cpp PRIVATE rareqs)
target_link_libraries(pyqbf_cpp PRIVATE qfun)
target_link_libraries(pyqbf_cpp PRIVATE quapi)
target_link_libraries(pyqbf_cpp PRIVATE bloqqer)
target_compile_options(pyqbf_cpp PRIVATE -Wall -Wextra)

target_compile_definitions(pyqbf_cpp PUBLIC NDEBUG=1)

set(SCRIPT_TO_BIN_REL_PATH ../../../../bin)
set(SCRIPT_TO_LIB_REL_PATH ../../..)

set(QUAPI_PRELOAD_PATH ${SCRIPT_TO_LIB_REL_PATH}/${CMAKE_SHARED_LIBRARY_PREFIX}pyqbf_quapi_preload${CMAKE_SHARED_LIBRARY_SUFFIX})

message(STATUS "QuAPI Preload Path is ${QUAPI_PRELOAD_PATH}")

target_compile_definitions(pyqbf_cpp PUBLIC QUAPI_PRELOAD_SO_PATH=${QUAPI_PRELOAD_PATH})
target_compile_definitions(pyqbf_cpp PUBLIC QUAPI_CAQE_EXE_PATH=${SCRIPT_TO_BIN_REL_PATH}/pyqbf_caqe)
target_compile_definitions(pyqbf_cpp PUBLIC QUAPI_DEPQBF_EXE_PATH=${SCRIPT_TO_BIN_REL_PATH}/pyqbf_depqbf)
target_compile_definitions(pyqbf_cpp PUBLIC QUAPI_QUTE_EXE_PATH=${SCRIPT_TO_BIN_REL_PATH}/pyqbf_qute)
target_compile_definitions(pyqbf_cpp PUBLIC QUAPI_RAREQS_EXE_PATH=${SCRIPT_TO_BIN_REL_PATH}/pyqbf_rareqs)
target_compile_definitions(pyqbf_cpp PUBLIC QUAPI_QFUN_EXE_PATH=${SCRIPT_TO_BIN_REL_PATH}/pyqbf_qfun)

enable_testing()

# This should work on all major Linux distributions.
set(Python_SITE "lib/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}/site-packages" CACHE STRING "Path to install Python packages to")

message(STATUS "Installing python packages into ${CMAKE_INSTALL_PREFIX}/${Python_SITE}")

message(STATUS "PREFIX is ${CMAKE_INSTALL_PREFIX}")
cmake_path(GET CMAKE_INSTALL_PREFIX PARENT_PATH MY_WHL)
message(STATUS "My_WHL is ${MY_WHL}")
cmake_path(GET MY_WHL PARENT_PATH MY_INSTALL)
message(STATUS "MY_INSTALL is ${MY_INSTALL}")

install(
  TARGETS pyqbf_cpp 
  LIBRARY DESTINATION ${Python_SITE})

install(
  DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/pyqbf 
  DESTINATION ${Python_SITE}
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.py")

# Caqe is already supplied in the installation
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/executables/pyqbf_caqe DESTINATION ${CMAKE_INSTALL_BINDIR} RENAME "pyqbf_caqe" PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)

install(TARGETS depqbf)
install(TARGETS qute_exe)
install(TARGETS rareqs_exe)
install(TARGETS qfun_exe)

if(NOT APPLE)
  set_target_properties(quapi_preload PROPERTIES OUTPUT_NAME "pyqbf_quapi_preload")
  install(TARGETS quapi_preload)
endif()

set(DEPQBF_TEST_EXE ${CMAKE_CURRENT_SOURCE_DIR}/executables/pyqbf_depqbf)
set(RAREQS_TEST_EXE ${CMAKE_CURRENT_SOURCE_DIR}/executables/pyqbf_rareqs)
set(QUTE_TEST_EXE ${CMAKE_CURRENT_SOURCE_DIR}/executables/pyqbf_qute)
set(QFUN_TEST_EXE ${CMAKE_CURRENT_SOURCE_DIR}/executables/pyqbf_qfun)
set(CAQE_TEST_EXE ${CMAKE_CURRENT_SOURCE_DIR}/executables/pyqbf_caqe)
set(QUAPI_PRELOAD_TEST_LIB "${MY_INSTALL}/bld/third_party/QuAPI/${CMAKE_SHARED_LIBRARY_PREFIX}pyqbf_quapi_preload${CMAKE_SHARED_LIBRARY_SUFFIX}")

configure_file(testconfig.sh.in testconfig.sh)

add_test(
    NAME PyQbfUnitTests 
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/testconfig.sh ${CMAKE_CURRENT_SOURCE_DIR}/tests/tests.py
)
