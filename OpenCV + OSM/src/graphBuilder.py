import networkx as nx
from shapely import wkt
import os

wkt_path = "../data/output/lanes_hybrid.wkt"
nodes_path = "../data/output/graph/nodes.csv"
edges_path = "../data/output/graph/edges.csv"
os.makedirs(os.path.dirname(nodes_path), exist_ok=True)

G = nx.DiGraph()
invalid_lines = 0
edge_count = 0

with open(wkt_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        line = line.strip()
        if not line:
            continue

        parts = line.split(",", 3)  # split only the first 3 commas
        if len(parts) != 4:
            print(f"Skipping malformed line {idx}: {line}")
            invalid_lines += 1
            continue

        way_id, highway_type, way_name, wkt_str = parts

        if not wkt_str.startswith("LINESTRING"):
            print(f"Skipping invalid WKT at line {idx}: {wkt_str}")
            invalid_lines += 1
            continue

        try:
            geom = wkt.loads(wkt_str)
            coords = list(geom.coords)
        except Exception as e:
            print(f"Error parsing WKT at line {idx}: {e}")
            invalid_lines += 1
            continue

        for i in range(len(coords) - 1):
            src = coords[i]
            dst = coords[i + 1]

            G.add_node(src, lon=src[0], lat=src[1])
            G.add_node(dst, lon=dst[0], lat=dst[1])

            dx = dst[0] - src[0]
            dy = dst[1] - src[1]
            length = (dx ** 2 + dy ** 2) ** 0.5

            G.add_edge(src, dst, way_id=way_id, highway_type=highway_type,
                       way_name=way_name, length=length)
            edge_count += 1

# --- Write edges ---
with open(edges_path, "w", encoding="utf-8") as ef:
    ef.write("from_id,to_id,way_id,highway_type,way_name,length\n")
    for src, dst, data in G.edges(data=True):
        ef.write(f"{src[0]}_{src[1]},{dst[0]}_{dst[1]},{data['way_id']},{data['highway_type']},{data['way_name']},{data['length']:.6f}\n")

# --- Write nodes ---
with open(nodes_path, "w", encoding="utf-8") as nf:
    nf.write("node_id,lon,lat\n")
    for idx, node in enumerate(G.nodes()):
        nf.write(f"{idx},{node[0]},{node[1]}\n")

print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
if invalid_lines > 0:
    print(f"{invalid_lines} invalid WKT lines were skipped.")
