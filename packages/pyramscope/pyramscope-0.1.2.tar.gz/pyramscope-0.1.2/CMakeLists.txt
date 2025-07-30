cmake_minimum_required(VERSION 3.15)
project(pyramscope LANGUAGES CXX)

find_package(pybind11 REQUIRED)

pybind11_add_module(_pyramscope pyramscope/core.cpp)

set_target_properties(_pyramscope PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/pyramscope
)
