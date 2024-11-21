cmake_minimum_required(VERSION 3.5)

project(rix)

set(CMAKE_CXX_STANDARD 20)

add_library(rix_msg INTERFACE)
target_include_directories(rix_msg INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)

### INSTALL ###
install(TARGETS rix_msg
    EXPORT rix_msgTargets
    ARCHIVE DESTINATION /usr/local/lib/rix)

install(FILES rix_msgConfig.cmake DESTINATION /usr/local/lib/cmake/rix_msg)

install(EXPORT rix_msgTargets
    FILE rix_msgTargets.cmake
    DESTINATION /usr/local/lib/cmake/rix_msg)
