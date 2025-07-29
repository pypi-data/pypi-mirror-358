cmake_minimum_required(VERSION 3.13)

project(qfun)

#SET(CMAKE_EXE_LINKER_FLAGS "-static")

file(GLOB SRCS ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)

add_library(qfun STATIC)
target_sources(qfun PRIVATE ${SRCS})
target_link_libraries(qfun PRIVATE minisat)
target_include_directories(qfun PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

set_property(TARGET qfun PROPERTY POSITION_INDEPENDENT_CODE ON)

list(REMOVE_ITEM ${SRCS} ${CMAKE_CURRENT_SOURCE_DIR}/pyqbf_int.cpp)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../executables)
add_executable(qfun_exe ${SRCS} main.cc)
target_link_libraries(qfun_exe PRIVATE minisat)
target_include_directories(qfun_exe PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
set_property(TARGET qfun_exe PROPERTY POSITION_INDEPENDENT_CODE ON)
set_property(TARGET qfun_exe PROPERTY OUTPUT_NAME "pyqbf_qfun")
