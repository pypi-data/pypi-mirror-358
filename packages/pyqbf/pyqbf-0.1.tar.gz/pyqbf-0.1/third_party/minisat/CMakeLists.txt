cmake_minimum_required(VERSION 3.13)
project(minisat)

#--------------------------------------------------------------------------------------------------
# Configurable options:

option(STATIC_BINARIES "Link binaries statically." ON)
option(USE_SORELEASE   "Use SORELEASE in shared library filename." ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

#--------------------------------------------------------------------------------------------------
# Library version:

set(MINISAT_SOMAJOR   2)
set(MINISAT_SOMINOR   1)
set(MINISAT_SORELEASE 0)

# Compute VERSION and SOVERSION:
if (USE_SORELEASE)
  set(MINISAT_VERSION ${MINISAT_SOMAJOR}.${MINISAT_SOMINOR}.${MINISAT_SORELEASE})
else()
  set(MINISAT_VERSION ${MINISAT_SOMAJOR}.${MINISAT_SOMINOR})
endif()
set(MINISAT_SOVERSION ${MINISAT_SOMAJOR})

#--------------------------------------------------------------------------------------------------
# Dependencies:

find_package(ZLIB)
include_directories(${ZLIB_INCLUDE_DIR})
include_directories(${minisat_SOURCE_DIR})

#--------------------------------------------------------------------------------------------------
# Compile flags:

add_definitions(-D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS)

#--------------------------------------------------------------------------------------------------
# Build Targets:

set(MINISAT_LIB_SOURCES
    utils/Options.cc
    utils/System.cc
    core/Solver.cc
    simp/SimpSolver.cc)

add_library(minisat STATIC ${MINISAT_LIB_SOURCES})
target_link_libraries(minisat ${ZLIB_LIBRARY})
target_include_directories(minisat PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

#--------------------------------------------------------------------------------------------------
# Installation targets:

# Do not install!

# install(TARGETS minisat
#         RUNTIME DESTINATION bin
#         LIBRARY DESTINATION lib
#         ARCHIVE DESTINATION lib)

# install(DIRECTORY include/minisat
#         DESTINATION include/minisat
#         FILES_MATCHING PATTERN "*.h")
