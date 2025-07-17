import pandas as pd
import os

edges_path = "../data/output/graph/edges.csv"
nodes_path = "../data/output/graph/nodes.csv"
output_path = "../data/output/graph/junctions.csv"

# Load data
edges_df = pd.read_csv(edges_path, dtype=str)
nodes_df = pd.read_csv(nodes_path, dtype=str)

# Count how many times each node appears in start/end of edges
node_counts = pd.concat([edges_df["start"], edges_df["end"]]).value_counts()

# Identify junctions: nodes that appear in 3 or more edges
junction_ids = node_counts[node_counts >= 3].index.tolist()

# Filter node details
junctions = nodes_df[nodes_df["id"].isin(junction_ids)]

# Write to CSV
junctions.to_csv(output_path, index=False)

print(f"{len(junctions)} junctions written to {output_path}")
