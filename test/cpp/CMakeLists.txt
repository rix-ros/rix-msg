cmake_minimum_required(VERSION 3.10)

project(msgs_test)

set(CMAKE_CXX_STANDARD 20)

add_executable(test_header test_header.cpp)
target_include_directories(test_header PRIVATE "~/.rix/include")

add_executable(test_example test_example.cpp)
target_include_directories(test_example PRIVATE "~/.rix/include")