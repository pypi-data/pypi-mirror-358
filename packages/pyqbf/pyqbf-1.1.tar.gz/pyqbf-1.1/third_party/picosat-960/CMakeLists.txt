set(PICOSAT_VERSION_VAR 960)

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/version.c.in
    ${CMAKE_CURRENT_BINARY_DIR}/version.c
    @ONLY)

add_library(picosat STATIC 
    ${CMAKE_CURRENT_SOURCE_DIR}/picosat.c
    ${CMAKE_CURRENT_BINARY_DIR}/version.c
)

target_include_directories(picosat PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

set_property(TARGET picosat PROPERTY POSITION_INDEPENDENT_CODE ON)