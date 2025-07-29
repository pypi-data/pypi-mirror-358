cmake_minimum_required(VERSION 3.13)

project(qute)
set(Tutorial_VERSION_MAJOR 1)
set(Tutorial_VERSION_MINOR 0)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# uncomment the following 3 lines to enable static linking (also check CMakeLists.txt in src/)
SET(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
SET(BUILD_SHARED_LIBS OFF)
# SET(CMAKE_EXE_LINKER_FLAGS "-static")

include_directories("docopt.cpp")

add_subdirectory("docopt.cpp")
add_subdirectory("src")

target_include_directories(qute PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
set_property(TARGET qute PROPERTY POSITION_INDEPENDENT_CODE ON)

target_link_libraries(qute minisat)

set_property(TARGET qute_exe PROPERTY POSITION_INDEPENDENT_CODE ON)
target_include_directories(qute_exe PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(qute_exe minisat)
set_target_properties(qute_exe PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../executables)
set_property(TARGET qute_exe PROPERTY OUTPUT_NAME qute)

set_target_properties(qute_exe PROPERTIES OUTPUT_NAME "pyqbf_qute")
