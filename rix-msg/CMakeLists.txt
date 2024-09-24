cmake_minimum_required(VERSION 3.5)

project(rix)

set(CMAKE_CXX_STANDARD 11)

add_library(rix_msg INTERFACE)
target_include_directories(rix_msg INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)

### INSTALL ###

# Install libraries
install(TARGETS rix_msg
    EXPORT rix_msgTargets
    ARCHIVE DESTINATION /usr/local/lib/rix)

# Install header files while preserving directory structure
install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/rix
    DESTINATION /usr/local/include
    FILES_MATCHING PATTERN "*.hpp")

install(FILES rix_msgConfig.cmake DESTINATION /usr/local/lib/cmake/rix_msg)

install(EXPORT rix_msgTargets
    FILE rix_msgTargets.cmake
    DESTINATION /usr/local/lib/cmake/rix_msg)

install(CODE "
    execute_process(COMMAND chmod +x ${CMAKE_CURRENT_SOURCE_DIR}/rixmsg-gen.py)
    execute_process(COMMAND chmod +x ${CMAKE_CURRENT_SOURCE_DIR}/rixmsg)
    execute_process(COMMAND touch /usr/local/bin/rixmsg-gen)
    execute_process(COMMAND touch /usr/local/bin/rixmsg)
    execute_process(COMMAND cp -p ${CMAKE_CURRENT_SOURCE_DIR}/rixmsg-gen.py /usr/local/bin/rixmsg-gen)
    execute_process(COMMAND cp -p ${CMAKE_CURRENT_SOURCE_DIR}/rixmsg /usr/local/bin/rixmsg)")

option(GEN_MSGS "Generate message headers" ON)
if (GEN_MSGS)
    install(CODE "
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/include/rix/msg/defs/standard)
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/include/rix/msg/defs/core)
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/include/rix/msg/defs/geometry)
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/include/rix/msg/defs/sensor)
    ")
endif()
