import xml.etree.ElementTree as ET
import pandas as pd
from shapely.geometry import LineString

# Load input files
nodes_df = pd.read_csv("../data/output/graph/nodes.csv", dtype=str)
edges_df = pd.read_csv("../data/output/graph/edges.csv", dtype=str)
junctions_df = pd.read_csv("../data/output/graph/junctions.csv", dtype=str)

# Parse WKT from lanes_hybrid.wkt
wkt_dict = {}
with open("../data/output/lanes_hybrid.wkt", "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split(",", 3)
        if len(parts) == 4 and parts[3].startswith("LINESTRING"):
            way_id, typ, name, wkt_string = parts
            try:
                coords = wkt_string.replace("LINESTRING (", "").replace(")", "").split(", ")
                points = [tuple(map(float, c.split())) for c in coords]
                wkt_dict[way_id] = LineString(points)
            except Exception as e:
                print(f"Failed to parse WKT for way_id {way_id}: {e}")

# Attach geometries to edge rows
edges_df["geometry"] = edges_df["way_id"].map(wkt_dict)
edges_df = edges_df[edges_df["geometry"].notnull()]
print(f"Loaded {len(edges_df)} edges with geometries.")

# Build OpenDRIVE root
root = ET.Element("OpenDRIVE")

# Add header first to satisfy schema
ET.SubElement(root, "header", {
    "revMajor": "1",
    "revMinor": "4",
    "name": "GeneratedMap",
    "version": "1.00",
    "date": "2025-07-16T00:00:00",
    "north": "90.0",
    "south": "-90.0",
    "east": "180.0",
    "west": "-180.0",
    "vendor": "AAI"
})

# Add roads
for _, row in edges_df.iterrows():
    geom = row["geometry"]
    if not isinstance(geom, LineString):
        continue

    coords = list(geom.coords)
    if len(coords) < 2:
        continue

    road = ET.SubElement(root, "road", {
        "name": row.get("name", ""),
        "length": str(geom.length),
        "id": row["way_id"],
        "junction": "-1"
    })
    ET.SubElement(road, "type", {"s": "0.0", "type": "rural"})
    planView = ET.SubElement(road, "planView")

    for i in range(len(coords) - 1):
        x, y = coords[i]
        dx = coords[i+1][0] - x
        dy = coords[i+1][1] - y
        length = (dx**2 + dy**2)**0.5
        ET.SubElement(planView, "geometry", {
            "s": str(i),
            "x": str(x),
            "y": str(y),
            "hdg": "0.0",
            "length": str(length)
        }).append(ET.Element("line"))

    # Lanes section
    lanes = ET.SubElement(road, "lanes")
    section = ET.SubElement(lanes, "laneSection", {"s": "0.0"})
    center = ET.SubElement(section, "center")

    lane = ET.SubElement(center, "lane", {
        "id": "0",
        "type": "driving",
        "level": "false"
    })
    link = ET.SubElement(lane, "link")
    ET.SubElement(link, "predecessor", {"id": "0"})
    ET.SubElement(link, "successor", {"id": "0"})

    # ✅ Skip <width> in center lanes to satisfy XSD
    # ET.SubElement(lane, "width", {...}) ← removed

# Add dummy junctions
for _, row in junctions_df.iterrows():
    junction = ET.SubElement(root, "junction", {
        "id": row["id"],
        "name": f"Junction_{row['lon']}_{row['lat']}"
    })
    connection = ET.SubElement(junction, "connection", {
        "id": f"{row['id']}_conn",
        "incomingRoad": "dummy",
        "connectingRoad": "dummy",
        "contactPoint": "start"
    })
    ET.SubElement(connection, "laneLink", {"from": "0", "to": "0"})

# Save file
tree = ET.ElementTree(root)
ET.indent(tree, space="  ", level=0)
tree.write("../data/output/map.xodr", encoding="utf-8", xml_declaration=True)
print("OpenDRIVE exported to ../data/output/map.xodr")
