cmake_minimum_required(VERSION 3.10)
project(hd_lane_topology)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)
find_package(Boost REQUIRED)
find_package(GDAL REQUIRED)

include_directories(
    ${Boost_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
    ${GDAL_INCLUDE_DIRS}
)

add_executable(osmReader src/osmReader.cpp)
target_link_libraries(osmReader
    ${Boost_LIBRARIES}
    ${GDAL_LIBRARIES}
    bz2 z expat  # Required for libosmium
)