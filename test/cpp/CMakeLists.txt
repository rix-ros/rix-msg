cmake_minimum_required(VERSION 3.10)

project(msgs_test)

set(CMAKE_CXX_STANDARD 20)

# Find Google Test
find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

# Serialization unit tests with Google Test
add_executable(test_serialization test_serialization.cpp)
target_include_directories(test_serialization PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../..")
target_link_libraries(test_serialization ${GTEST_LIBRARIES} pthread)

# Enable testing
enable_testing()
add_test(NAME SerializationTests COMMAND test_serialization)