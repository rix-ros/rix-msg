cmake_minimum_required(VERSION 3.10)

project(msgs_test)

set(CMAKE_CXX_STANDARD 20)

list(APPEND CMAKE_PREFIX_PATH "~/.rix")

find_package(rixmsg REQUIRED)

add_executable(test test.cpp)
