cmake_minimum_required(VERSION 3.13)

project(rareqs)

file(GLOB SRCS ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cc)

add_library(rareqs STATIC ${SRCS})
target_link_libraries(rareqs PRIVATE minisat)

target_include_directories(rareqs PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_include_directories(rareqs PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

set_property(TARGET rareqs PROPERTY POSITION_INDEPENDENT_CODE ON)
target_compile_definitions(rareqs PUBLIC NDEBUG=1)

add_executable(rareqs_exe ${SRCS})
target_link_libraries(rareqs_exe PUBLIC minisat)
target_include_directories(rareqs_exe PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_include_directories(rareqs_exe PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(rareqs_exe PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../executables)
set_property(TARGET rareqs_exe PROPERTY OUTPUT_NAME rareqs)

set_target_properties(rareqs_exe PROPERTIES OUTPUT_NAME "pyqbf_rareqs")
