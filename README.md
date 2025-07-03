# HD Lane-Level Topology

A toolset for processing and visualizing high-definition lane-level road topology data using OpenStreetMap (OSM) inputs and raster tile images. This project includes both C++ and Python components to parse, verify, and reproject tile-based map data.

---

## Building & Running the Project

### 1. Create a clean build directory
rm -rf build
mkdir build
cd build

### 2. Run CMake to configure
cmake ..

### 3. Build the target
make

### 4. Running
Run the C++ executable with ./pathtoexecutable e.g ./build/osmReader
Run the python executables normally

(Future commits will automate all the building and running)
