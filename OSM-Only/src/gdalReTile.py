import os
import subprocess

# --- CONFIGURATION ---
input_root = "../data/reprojected-tiles"
output_root = "../data/final-tiles"
tile_width = 200     # Change as needed
tile_height = 200    # Change as needed

# --- Ensure output root exists ---
os.makedirs(output_root, exist_ok=True)

# --- Loop through all years ---
for year in os.listdir(input_root):
    year_input_dir = os.path.join(input_root, year)
    if not os.path.isdir(year_input_dir):
        continue

    year_output_dir = os.path.join(output_root, year)
    os.makedirs(year_output_dir, exist_ok=True)

    # Process each TIF in the year directory
    for fname in os.listdir(year_input_dir):
        if fname.endswith(".tif"):
            input_path = os.path.join(year_input_dir, fname)
            # Output prefix without extension
            output_prefix = os.path.join(year_output_dir, os.path.splitext(fname)[0])

            # GDAL command
            cmd = [
                "gdal_retile.py",
                "-targetDir", year_output_dir,
                "-ps", str(tile_width), str(tile_height),
                "-co", "TILED=YES",
                "-co", "COMPRESS=LZW",
                "-co", "BIGTIFF=IF_SAFER",
                "-of", "GTiff",
                input_path
            ]

            print("Tiling:", input_path)
            subprocess.run(cmd, check=True)
