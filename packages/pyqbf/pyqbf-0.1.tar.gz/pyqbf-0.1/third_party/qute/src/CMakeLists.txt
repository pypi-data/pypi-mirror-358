file(GLOB SRCS *.cc)

add_library(qute STATIC ${SRCS})

target_link_libraries(qute ${Boost_LIBRARIES})
target_link_libraries(qute ${CMAKE_THREAD_LIBS_INIT})
# change the following line to enable static linking (also see ../CMakeLists.txt)
#target_link_libraries(qute docopt)
target_link_libraries(qute docopt_s)


add_executable(qute_exe ${SRCS})
target_link_libraries(qute_exe ${Boost_LIBRARIES})
target_link_libraries(qute_exe ${CMAKE_THREAD_LIBS_INIT})
target_link_libraries(qute_exe docopt_s)