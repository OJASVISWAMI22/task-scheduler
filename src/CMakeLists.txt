cmake_minimum_required(VERSION 3.14)
project(TaskScheduler)

set(CMAKE_CXX_STANDARD 17)

# OpenSSL
find_package(OpenSSL REQUIRED)

# httplib 
include(FetchContent)
FetchContent_Declare(
    httplib
    GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
    GIT_TAG v0.14.1
)
FetchContent_MakeAvailable(httplib)

# nlohmann/json
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(nlohmann_json)

# main executable
add_executable(task_scheduler
    main.cpp
    processor.cpp
)
# including libraries
target_link_libraries(task_scheduler
    OpenSSL::SSL
    OpenSSL::Crypto
    httplib::httplib
    nlohmann_json::nlohmann_json
)

# GoogleTest
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

# test executable
add_executable(processor_test
    processor_test.cpp
    processor.cpp
)
target_link_libraries(processor_test
    GTest::gtest_main
    OpenSSL::SSL
    OpenSSL::Crypto
)