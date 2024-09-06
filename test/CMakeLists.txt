cmake_minimum_required(VERSION 3.5)

project(msgs_test)

set(CMAKE_CXX_STANDARD 11)

add_executable(test test.cpp)
target_include_directories(test PRIVATE /usr/local/include/)
