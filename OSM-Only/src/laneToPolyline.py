import pandas as pd
from shapely.geometry import LineString
import rasterio
import math
import ast
import sys

def offset_linestring(line, offset):
    try:
        return line.parallel_offset(offset, side='right', join_style=2)
    except Exception:
        return None

def infer_lanes(row):
    if pd.notnull(row['lanes']) and str(row['lanes']).isdigit():
        return int(row['lanes'])

    highway = str(row.get('highway', '')).lower()
    width = float(row['width']) if 'width' in row and pd.notnull(row['width']) else 0

    if width >= 6:
        return 2
    elif width >= 4:
        return 1
    elif highway == 'motorway':
        return 4
    elif highway in ['primary', 'secondary']:
        return 2
    elif highway in ['residential', 'tertiary']:
        return 1
    else:
        return 1


def get_bbox_from_tif(tif_path):
    with rasterio.open(tif_path) as src:
        bounds = src.bounds
        return (bounds.left, bounds.bottom, bounds.right, bounds.top)  # (minx, miny, maxx, maxy)

def geometry_in_bbox(geometry_str, bbox):
    try:
        coords = ast.literal_eval(geometry_str)
        for lon, lat in coords:
            if bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]:
                return True
    except:
        pass
    return False

# --- MAIN ---
if len(sys.argv) < 2:
    print("Usage: python laneToPolyline.py <path_to_tif>")
    sys.exit(1)

tif_path = sys.argv[1]
bbox = get_bbox_from_tif(tif_path)

input_csv = '../data/roads.csv'
output_wkt = '../data/output/lanes_hybrid.wkt'

df = pd.read_csv(input_csv)

lane_polylines = []

for idx, row in df.iterrows():
    try:
        if not geometry_in_bbox(row['geometry'], bbox):
            continue

        coords = ast.literal_eval(row['geometry'])
        if len(coords) < 2:
            continue

        base_line = LineString(coords)
        lane_count = infer_lanes(row)

        lane_width = 3.0
        center_offset = (lane_count - 1) * lane_width / 2.0

        for i in range(lane_count):
            offset = center_offset - i * lane_width
            lane_geom = offset_linestring(base_line, offset)
            if lane_geom:
                lane_polylines.append(f"{row['id']},{lane_geom.wkt}")
    except Exception as e:
        print(f"Skipping way id={row.get('id', '?')} due to error: {e}")

with open(output_wkt, "w", encoding="utf-8") as f:
    f.write("id,WKT\n")
    for line in lane_polylines:
        f.write(line + "\n")

print(f"lanes_hybrid.wkt written with {len(lane_polylines)} polylines.")
