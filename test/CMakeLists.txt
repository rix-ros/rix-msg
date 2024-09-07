cmake_minimum_required(VERSION 3.5)

project(msgs_test)

set(CMAKE_CXX_STANDARD 11)

find_package(rix_msg REQUIRED)

add_executable(test test.cpp)
