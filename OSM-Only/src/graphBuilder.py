import os
import pandas as pd
from shapely import wkt
from shapely.geometry import LineString

input_wkt = '../data/output/lanes_hybrid.wkt'
graph_dir = '../data/output/graph'
os.makedirs(graph_dir, exist_ok=True)

nodes = []
edges = []

# Custom WKT loader to avoid CSV parsing issues
with open(input_wkt, 'r', encoding='utf-8') as f:
    lines = f.readlines()[1:]  # skip header
    for eid, line in enumerate(lines):
        try:
            split_index = line.index(',LINESTRING')
            wid = line[:split_index]
            linestring_wkt = line[split_index+1:].strip()
        except ValueError:
            try:
                split_index = line.index(',MULTILINESTRING')
                wid = line[:split_index]
                linestring_wkt = line[split_index+1:].strip()
            except ValueError:
                print(f"Skipping malformed line: {line.strip()}")
                continue

        geom = wkt.loads(linestring_wkt)

        if isinstance(geom, LineString):
            segments = [geom]
        else:
            segments = list(geom.geoms)

        for seg in segments:
            coords = list(seg.coords)
            for i in range(len(coords) - 1):
                n1 = coords[i]
                n2 = coords[i + 1]

                # Add nodes
                n1_id = f"{n1[0]:.6f}_{n1[1]:.6f}"
                n2_id = f"{n2[0]:.6f}_{n2[1]:.6f}"

                nodes.append((n1_id, n1[0], n1[1]))
                nodes.append((n2_id, n2[0], n2[1]))

                # Add edge
                edges.append((wid, n1_id, n2_id))

nodes_df = pd.DataFrame(set(nodes), columns=["id", "lon", "lat"])
edges_df = pd.DataFrame(edges, columns=["way_id", "start", "end"])

nodes_df.to_csv(os.path.join(graph_dir, "nodes.csv"), index=False)
edges_df.to_csv(os.path.join(graph_dir, "edges.csv"), index=False)

print(f"Graph built with {len(nodes_df)} nodes and {len(edges_df)} edges.")
