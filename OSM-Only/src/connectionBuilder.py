import pandas as pd
from collections import defaultdict

# Paths
edges_csv = "../data/output/graph/edges.csv"
nodes_csv = "../data/output/graph/nodes.csv"
junctions_csv = "../data/output/graph/junctions.csv"
output_csv = "../data/output/graph/connections.csv"

# Load data
edges_df = pd.read_csv(edges_csv, dtype=str)
junctions_df = pd.read_csv(junctions_csv, dtype=str)

# Create lookup: node_id → list of way_ids
node_to_ways = defaultdict(set)

for _, row in edges_df.iterrows():
    way_id = row["way_id"]
    node_to_ways[row["start"]].add(way_id)
    node_to_ways[row["end"]].add(way_id)

# Build connections
connections = []

for _, row in junctions_df.iterrows():
    junction_id = row["id"]
    way_ids = list(node_to_ways.get(junction_id, []))

    # For each pair of distinct roads meeting at this junction
    for i in range(len(way_ids)):
        for j in range(len(way_ids)):
            if i != j:
                incoming = way_ids[i]
                outgoing = way_ids[j]
                connections.append({
                    "junction_id": junction_id,
                    "incomingRoad": incoming,
                    "connectingRoad": outgoing,
                    "lane_from": 0,
                    "lane_to": 0
                })

# Save to CSV
conn_df = pd.DataFrame(connections)
conn_df.to_csv(output_csv, index=False)
print(f"{len(conn_df)} road-to-road connections written to {output_csv}")
