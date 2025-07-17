import os
import subprocess

input_root = "../data/berlin-tiles"
output_root = "../data/reprojected-tiles"
target_srs = "EPSG:4326"

os.makedirs(output_root, exist_ok=True)

for year in os.listdir(input_root):
    year_input_dir = os.path.join(input_root, year)
    year_output_dir = os.path.join(output_root, year)
    os.makedirs(year_output_dir, exist_ok=True)

    for fname in os.listdir(year_input_dir):
        if fname.endswith(".tif"):
            input_path = os.path.join(year_input_dir, fname)
            output_path = os.path.join(year_output_dir, fname)
            cmd = ["gdalwarp", "-t_srs", target_srs, input_path, output_path]
            print("Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)
