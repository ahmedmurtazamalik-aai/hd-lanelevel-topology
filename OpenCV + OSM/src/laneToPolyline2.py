import csv
from shapely.geometry import LineString
from collections import defaultdict

csv_path = "../data/roads.csv"
output_path = "../data/output/lanes_from_osm.wkt"

lanes = defaultdict(lambda: {"type": "", "name": "", "points": []})

with open(csv_path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        t = row["highway_type"]
        if t in ("construction", "steps"):
            continue
        try:
            lane_id = row["way_id"]
            lon = float(row["lon"])
            lat = float(row["lat"])
            idx = int(row["node_index"])
            lanes[lane_id]["type"] = t
            lanes[lane_id]["name"] = row["way_name"]
            lanes[lane_id]["points"].append((idx, lon, lat))
        except:
            continue

with open(output_path, "w") as out:
    for lid, info in lanes.items():
        if len(info["points"]) < 2:
            continue
        points = sorted(info["points"], key=lambda x: x[0])
        coords = [(lon, lat) for _, lon, lat in points]
        line = LineString(coords)
        out.write(f"{lid},{info['type']},{info['name']},{line.wkt}\n")

print("Exported lanes_from_osm.wkt")
