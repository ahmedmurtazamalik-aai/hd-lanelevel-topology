# HD Lane-Level Topology

A python pipeline for generating .xodr maps for any selected orthophoto for high-definition lane-level road topology, using OpenStreetMap (OSM) inputs and orthophotos. The project consists of Python source files, and processes 2 streams of data: .osm.pbf and .tif files.
There are 2 versions of the project, one uses OpenCV detection as well as OSM data, while the other uses OSM data only. Both have their own directories. The internal directory structure is the same for both.

---

## Building & Running the Project

### 1. Copy desired orthophoto path (must be from reprojected-tiles folder)  
This would be something like "../data/reprojected-tiles/2019/tile_5_11_2019.tif" with the .. because the project would be run from src directory.

### 2. Navigate to the src directory of the version you want to run

### 3. Run the pipeline
Execute the runPipeline.py file with the orthophoto path as argument e.g "python runPipeline.py ../data/reprojected-tiles/2019/tile_5_11_2019.tif" for Windows or "python3 runPipeline.py ../data/reprojected-tiles/2019/tile_5_11_2019.tif" for Linux systems.

#### Note
Please note that the automated pipeline does not include data downloading.
