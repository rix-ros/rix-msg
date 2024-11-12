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

install(CODE "
    execute_process(COMMAND sudo rm -rf /usr/local/include/rix/msg)
    execute_process(COMMAND mkdir -p /usr/local/include/rix/msg)
    execute_process(COMMAND cp -r ${CMAKE_CURRENT_SOURCE_DIR}/include/ /usr/local/include/rix/msg/)
    execute_process(COMMAND pyinstaller -p=${CMAKE_CURRENT_SOURCE_DIR}/python/ --onedir --strip --noupx -y --distpath ${CMAKE_CURRENT_BINARY_DIR}/custom_dist ${CMAKE_CURRENT_SOURCE_DIR}/python/rixmsg.py)
    execute_process(COMMAND rm -rf /usr/local/lib/rixmsg_lib)
    execute_process(COMMAND cp -r ${CMAKE_CURRENT_BINARY_DIR}/custom_dist/rixmsg /usr/local/lib/rixmsg_lib)
    execute_process(COMMAND rm -f /usr/local/bin/rixmsg)
    execute_process(COMMAND ln -sf /usr/local/lib/rixmsg_lib/rixmsg /usr/local/bin/rixmsg)
    execute_process(COMMAND mkdir -p $ENV{HOME}/.rix/node_modules/rix-msg)
    execute_process(COMMAND mkdir -p $ENV{HOME}/.rix/python/rixmsg)"
)

option(GEN_MSGS "Generate message headers" ON)
if (GEN_MSGS)
    install(CODE "
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/defs/standard)
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/defs/navigation)
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/defs/geometry)
    execute_process(COMMAND rixmsg create ${CMAKE_CURRENT_SOURCE_DIR}/defs/sensor)
    ")
endif()
