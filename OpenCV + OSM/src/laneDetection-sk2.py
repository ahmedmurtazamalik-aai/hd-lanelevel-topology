import numpy as np
import rasterio
from rasterio.transform import Affine
from skimage.draw import line as sk_line
import matplotlib.pyplot as plt
import csv
import cv2

# === CONFIG ===
tif_path = "../data/reprojected-tiles/2019/tile_5_11_2019.tif"
csv_path = "../data/roads.csv"
output_mask = "../data/output/lane_mask_osm_guided.png"
output_overlay = "../data/output/lanes_osm_guided.png"

# --- Load GeoTIFF ---
with rasterio.open(tif_path) as src:
    img = src.read([1, 2, 3])  # RGB
    transform: Affine = src.transform
    width, height = src.width, src.height

# Convert to H x W x 3 OpenCV-style image
image = np.transpose(img, (1, 2, 0)).astype(np.uint8)
overlay = image.copy()
mask = np.zeros((height, width), dtype=np.uint8)

# --- Road color coding ---
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

# --- Read and group OSM data ---
grouped = {}
with open(csv_path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["highway_type"] in ("construction", "steps"):
            continue
        key = (row["way_id"], row["highway_type"])
        try:
            lon = float(row["lon"])
            lat = float(row["lat"])
            col, row_ = ~transform * (lon, lat)
            px, py = int(col), int(row_)
            if 0 <= px < width and 0 <= py < height:
                grouped.setdefault(key, []).append((px, py))
        except:
            continue

# --- Draw polylines on overlay and mask ---
for (way_id, highway_type), pts in grouped.items():
    if len(pts) < 2:
        continue
    color = type_color_map.get(highway_type, (150, 150, 150))
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        rr, cc = sk_line(y0, x0, y1, x1)
        mask[rr, cc] = 255
        overlay[rr, cc] = color

# --- Save results ---
cv2.imwrite(output_mask, mask)
cv2.imwrite(output_overlay, overlay)
cv2.imshow("OSM Guided Lanes", overlay)
cv2.waitKey(0)
cv2.destroyAllWindows()
