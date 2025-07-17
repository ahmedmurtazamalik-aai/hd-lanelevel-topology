import pandas as pd
import xml.etree.ElementTree as ET
from shapely.geometry import LineString
from pyproj import Transformer

# File paths
edges_path = "../data/output/graph/edges.csv"
nodes_path = "../data/output/graph/nodes.csv"
junctions_path = "../data/output/graph/junctions.csv"
wkt_path = "../data/output/lanes_hybrid.wkt"
output_file = "../data/output/map.xodr"

# WGS84 to UTM33N (Berlin)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)

# Load inputs
edges_df = pd.read_csv(edges_path, dtype=str)
nodes_df = pd.read_csv(nodes_path, dtype=str)
junctions_df = pd.read_csv(junctions_path, dtype=str)

# Robust WKT parsing
wkt_dict = {}
with open(wkt_path, "r", encoding="utf-8") as f:
    lines = f.readlines()[1:]  # skip header
    for line in lines:
        try:
            split_idx = line.index(",")
            way_id = line[:split_idx]
            wkt_str = line[split_idx + 1:].strip()

            if wkt_str.startswith("LINESTRING ("):
                coords_raw = wkt_str.replace("LINESTRING (", "").replace(")", "")
                coords = [tuple(map(float, pt.strip().split())) for pt in coords_raw.split(",")]
                if len(coords) >= 2:
                    wkt_dict[way_id] = LineString(coords)
        except Exception as e:
            print(f"⚠️ Skipping malformed WKT line: {e}")

print(f"✅ Loaded {len(edges_df)} edges with geometries.")

# XML structure
root = ET.Element("OpenDRIVE")

ET.SubElement(root, "header", {
    "revMajor": "1",
    "revMinor": "4",
    "name": "",
    "version": "1.00",
    "date": "2025-07-17",
    "north": "90", "south": "-90", "east": "180", "west": "-180",
    "vendor": "AAI-GmbH"
})

# Roads
for way_id, geom in wkt_dict.items():
    coords = list(geom.coords)
    if len(coords) < 2:
        continue

    projected_coords = [transformer.transform(x, y) for x, y in coords]
    road = ET.SubElement(root, "road", {
        "name": "",
        "length": str(LineString(projected_coords).length),
        "id": way_id,
        "junction": "-1"
    })

    ET.SubElement(road, "type", {
        "s": "0.0",
        "type": "rural"
    })

    planView = ET.SubElement(road, "planView")
    for i in range(len(projected_coords) - 1):
        x, y = projected_coords[i]
        segment = LineString(projected_coords[i:i + 2])
        ET.SubElement(planView, "geometry", {
            "s": str(i),
            "x": str(x),
            "y": str(y),
            "hdg": "0.0",
            "length": str(segment.length)
        }).append(ET.Element("line"))

    # Lanes (schema-compliant order)
    lanes = ET.SubElement(road, "lanes")
    laneSection = ET.SubElement(lanes, "laneSection", {"s": "0.0"})

    # 1. <left>
    left = ET.Element("left")
    left_lane = ET.SubElement(left, "lane", {
        "id": "1",
        "type": "driving",
        "level": "false"
    })
    ET.SubElement(left_lane, "link")
    ET.SubElement(left_lane, "width", {
        "sOffset": "0.0", "a": "3.0", "b": "0.0", "c": "0.0", "d": "0.0"
    })
    laneSection.append(left)

    # 2. <center>
    center = ET.Element("center")
    ET.SubElement(center, "lane", {
        "id": "0",
        "type": "none",
        "level": "false"
    })
    laneSection.append(center)

# Junctions (with <connection> if valid)
for _, row in junctions_df.iterrows():
    junc_id = row["id"]
    lon, lat = float(row["lon"]), float(row["lat"])
    incoming = edges_df[edges_df["end"] == junc_id]
    outgoing = edges_df[edges_df["start"] == junc_id]

    connection_count = 0
    conn_elements = []

    for _, inc in incoming.iterrows():
        for _, out in outgoing.iterrows():
            if inc["way_id"] != out["way_id"]:
                conn = ET.Element("connection", {
                    "id": f"{junc_id}_{connection_count}",
                    "incomingRoad": inc["way_id"],
                    "connectingRoad": out["way_id"],
                    "contactPoint": "start"
                })
                ET.SubElement(conn, "laneLink", {"from": "1", "to": "1"})
                conn_elements.append(conn)
                connection_count += 1

    if conn_elements:
        junction = ET.SubElement(root, "junction", {
            "id": junc_id,
            "name": f"Junction_{lon}_{lat}"
        })
        for conn in conn_elements:
            junction.append(conn)

# Write XML
tree = ET.ElementTree(root)
ET.indent(tree, space="  ", level=0)
tree.write(output_file, encoding="utf-8", xml_declaration=True)

print(f"OpenDRIVE file written to: {output_file}")
