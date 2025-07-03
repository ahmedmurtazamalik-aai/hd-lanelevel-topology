# HD Lane-Level Topology

A toolset for processing and visualizing high-definition lane-level road topology data using OpenStreetMap (OSM) inputs and raster tile images. This project includes both C++ and Python components to parse, verify, and reproject tile-based map data.

---

## 📁 Project Structure

project-root/
├── build/ # CMake build output (ignored in git)
├── data/
│ ├── berlin-tiles/ # Original raster tiles
│ ├── reprojected-tiles/ # Reprojected tiles
│ └── osm-data/ # Raw OSM inputs
├── include/ # C++ headers
├── src/ # C++/Python source files
│ ├── osmReader.cpp
│ ├── getTIFF.py
│ ├── reprojectTiles.py
│ ├── osmVerify.py
│ └── randomTileIndices.json
├── CMakeLists.txt
└── .gitignore

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
