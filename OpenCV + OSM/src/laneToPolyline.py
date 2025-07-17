import cv2
import numpy as np
import rasterio
import csv
import os
from shapely.geometry import LineString, box
import sys

if len(sys.argv) < 2:
    print("Usage: python laneToPolyline.py <tif_path>")
    sys.exit(1)

tif_path = sys.argv[1]

lane_mask_path = "../data/output/lane_mask.png"
roads_csv_path = "../data/roads.csv"
output_wkt_path = "../data/output/lanes_hybrid.wkt"

lane_mask = cv2.imread(lane_mask_path, cv2.IMREAD_GRAYSCALE)
if lane_mask is None:
    raise FileNotFoundError(f"Lane mask not found at: {lane_mask_path}")

with rasterio.open(tif_path) as tif:
    transform = tif.transform
    tile_box = box(*tif.bounds)

# Read OSM road segments grouped by (way_id, type, name)
osm_segments = {}
with open(roads_csv_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            key = (row['way_id'], row['highway_type'], row['way_name'])
            lon = float(row['lon'])
            lat = float(row['lat'])
            osm_segments.setdefault(key, []).append((int(row['node_index']), lon, lat))
        except:
            continue

osm_lines = []
for (wid, typ, name), coords in osm_segments.items():
    if len(coords) < 2:
        continue
    coords.sort()
    pts = [(lon, lat) for _, lon, lat in coords]
    osm_lines.append((wid, typ, name, pts))

# Get detected contours and convert to geo
contours, _ = cv2.findContours(lane_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
lane_polylines = []
for contour in contours:
    pts = []
    for pt in contour:
        x, y = pt[0]
        lon, lat = rasterio.transform.xy(transform, y, x)
        pts.append((lon, lat))
    poly = LineString(pts)
    if poly.length > 1e-6:
        lane_polylines.append(poly)

matched = [False] * len(osm_lines)
output_lines = []
tolerance = 0.00005

for poly in lane_polylines:
    best_match = -1
    best_dist = float("inf")
    for i, (_, _, _, pts) in enumerate(osm_lines):
        if matched[i]:
            continue
        osm_line = LineString(pts)
        dist = poly.distance(osm_line)
        if dist < best_dist and dist < tolerance:
            best_dist = dist
            best_match = i
    if best_match != -1:
        matched[best_match] = True
        wid, typ, name, pts = osm_lines[best_match]
        output_lines.append((wid, typ, name, LineString(pts)))
    else:
        output_lines.append(("cv", "unknown", "detected", poly))

# Add unmatched OSM lines that intersect tile
for i, (wid, typ, name, pts) in enumerate(osm_lines):
    if matched[i]:
        continue
    line = LineString(pts)
    if line.intersects(tile_box):
        output_lines.append((wid, typ, name, line))

# Write to WKT
with open(output_wkt_path, "w", encoding="utf-8") as f:
    for wid, typ, name, line in output_lines:
        f.write(f"{wid},{typ},{name},{line.wkt}\n")

print(f"✅ lanes_hybrid.wkt written with {len(output_lines)} polylines.")
