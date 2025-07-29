set(SRCS
    ${CMAKE_CURRENT_SOURCE_DIR}/bloqqer.c
    ${CMAKE_CURRENT_SOURCE_DIR}/blqrcfg.c
)

add_library(bloqqer STATIC ${SRCS})

target_include_directories(bloqqer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

set_property(TARGET bloqqer PROPERTY POSITION_INDEPENDENT_CODE ON)

target_compile_definitions(bloqqer PUBLIC NDEBUG=1)
target_compile_definitions(bloqqer PUBLIC LIBBLOQQER=1)
