import cv2
import csv
import sys
import numpy as np
import rasterio
from rasterio.transform import Affine
import matplotlib.pyplot as plt

# --- Dynamic Input Handling ---
if len(sys.argv) < 2:
    print("Usage: python laneDetection-cv.py <tif_path>")
    sys.exit(1)

tif_path = sys.argv[1]
csv_path = "../data/roads.csv"
output_color = "../data/output/output_with_lanes.png"
output_mask = "../data/output/lane_mask.png"

# --- Load GeoTIFF ---
with rasterio.open(tif_path) as src:
    img = src.read([1, 2, 3])  # RGB
    transform: Affine = src.transform
    width, height = src.width, src.height

# Convert image to H x W x 3 format (OpenCV-style)
image_rgb = np.transpose(img, (1, 2, 0)).astype(np.uint8)
image_copy = image_rgb.copy()
mask = np.zeros((height, width), dtype=np.uint8)

# --- Color mapping ---
type_color_map = {
    "motorway": (0, 0, 255),
    "trunk": (0, 0, 255),
    "primary": (0, 128, 255),
    "secondary": (0, 128, 255),
    "tertiary": (0, 128, 255),
    "residential": (0, 255, 0),
    "living_street": (0, 255, 0),
    "service": (0, 255, 0),
    "cycleway": (255, 0, 0),
    "footway": (255, 0, 0),
    "path": (255, 0, 0),
    "track": (255, 0, 0),
}

# --- Read CSV and group points ---
grouped = {}
with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["highway_type"] in ["construction", "steps"]:
            continue
        way_id = row["way_id"]
        road_type = row["highway_type"]
        key = (way_id, road_type)

        try:
            lon = float(row["lon"])
            lat = float(row["lat"])
        except ValueError:
            continue

        # Convert lon/lat to pixel
        col, row_ = ~transform * (lon, lat)
        px, py = int(col), int(row_)
        if 0 <= px < width and 0 <= py < height:
            grouped.setdefault(key, []).append((px, py))

# --- Draw on image and mask ---
for (way_id, road_type), points in grouped.items():
    if len(points) < 2:
        continue

    pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
    color = type_color_map.get(road_type, (150, 150, 150))

    # Draw on colored overlay
    cv2.polylines(image_copy, [pts], isClosed=False, color=color, thickness=4)

    # Draw on binary mask
    cv2.polylines(mask, [pts], isClosed=False, color=255, thickness=4)

# --- Save and display ---
cv2.imwrite(output_color, image_copy)
cv2.imwrite(output_mask, mask)

cv2.imshow("Detected Lanes", image_copy)
cv2.waitKey(0)
cv2.destroyAllWindows()
