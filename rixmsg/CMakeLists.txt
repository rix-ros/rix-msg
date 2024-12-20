cmake_minimum_required(VERSION 3.5)

project(rixmsg)

set(CMAKE_CXX_STANDARD 20)

# Set default install prefix to ~/.rix if not defined
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "~/.rix" CACHE PATH "Default install prefix" FORCE)
endif()

add_library(rixmsg INTERFACE)
target_include_directories(rixmsg INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/>)

### INSTALL ###
install(TARGETS rixmsg
    EXPORT rixmsgTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/rix)

install(FILES rixmsgConfig.cmake DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/cmake/rixmsg)

install(EXPORT rixmsgTargets
    FILE rixmsgTargets.cmake
    DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/cmake/rixmsg)