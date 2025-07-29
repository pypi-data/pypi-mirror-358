cmake_minimum_required(VERSION 3.31)
project(graph_simulator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(PYBIND11_FINDPYTHON ON)

# Add pybind11 path explicitly
include_directories(venv/lib/python3.13/site-packages/pybind11/include)

# Add yaml-cpp paths explicitly
include_directories(/opt/homebrew/include)
link_directories(/opt/homebrew/lib)

find_package(pybind11 CONFIG REQUIRED)
find_package(yaml-cpp REQUIRED)

# Add the Python extension module
pybind11_add_module(graph_simulator src/graph_simulator/dag_simulator.cpp)
target_link_libraries(graph_simulator PRIVATE yaml-cpp)

install(TARGETS graph_simulator DESTINATION .)

# mkdir build; cd build; cmake ..; make; ./test_simulator