import pandas as pd

edges_path = "../data/output/graph/edges.csv"
output_path = "../data/output/graph/junctions.csv"

# Load edge data
edges_df = pd.read_csv(edges_path, dtype=str)

# Combine from_id and to_id for counting
all_nodes = pd.concat([edges_df["from_id"], edges_df["to_id"]])
junction_candidates = all_nodes.value_counts()
junction_coords = junction_candidates[junction_candidates > 2].index.tolist()

# Parse lon/lat from "lon_lat"
junction_data = []
for i, coord_str in enumerate(junction_coords):
    try:
        lon, lat = map(float, coord_str.split("_"))
        junction_data.append({
            "id": f"junction_{i}",
            "node": coord_str,
            "lon": lon,
            "lat": lat
        })
    except Exception as e:
        continue

# Save output
junction_df = pd.DataFrame(junction_data)
junction_df.to_csv(output_path, index=False)
print(f"{len(junction_df)} junctions written to {output_path}")
