set(LIBQDPLL_SRCS
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_pqueue.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_mem.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_dep_man_qdag.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_dynamic_nenofex.c
    ${CMAKE_CURRENT_SOURCE_DIR}/pysat_qdpll_interface.c
    )

add_library(qdpll STATIC ${LIBQDPLL_SRCS})
target_include_directories(qdpll PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(qdpll PRIVATE picosat nenofex)

set_property(TARGET qdpll PROPERTY POSITION_INDEPENDENT_CODE ON)


set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../executables)
set(EXEQDPLL_SRCS
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_pqueue.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_mem.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_dep_man_qdag.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_dynamic_nenofex.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_main.c
    ${CMAKE_CURRENT_SOURCE_DIR}/qdpll_app.c
    )

add_executable(depqbf ${EXEQDPLL_SRCS})
target_include_directories(depqbf PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(depqbf PRIVATE picosat nenofex)

set_target_properties(depqbf PROPERTIES OUTPUT_NAME "pyqbf_depqbf")
