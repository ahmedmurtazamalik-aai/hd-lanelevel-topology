import osmium
import pandas as pd

class WayHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.data = []

    def way(self, w):
        if not any(t.k == "highway" for t in w.tags):
            return

        tags = {t.k: t.v for t in w.tags}
        highway = tags.get("highway", "")
        name = tags.get("name", "")
        oneway = tags.get("oneway", "no")
        lanes = tags.get("lanes", None)

        # Heuristic inference if 'lanes' is not provided
        if lanes is None:
            if highway in ["motorway", "trunk"]:
                lanes = 4
            elif highway in ["primary", "secondary"]:
                lanes = 2
            else:
                lanes = 1
        else:
            try:
                lanes = int(lanes)
            except ValueError:
                lanes = 1  # fallback

        coords = [(n.lon, n.lat) for n in w.nodes]

        self.data.append({
            "id": w.id,
            "name": name,
            "highway": highway,
            "lanes": lanes,
            "oneway": oneway,
            "geometry": coords
        })

# Paths
input_file = "../data/osm-data/berlin-latest.osm.pbf"
output_file = "../data/roads.csv"

# Run extraction
handler = WayHandler()
handler.apply_file(input_file,locations=True)

df = pd.DataFrame(handler.data)
df.to_csv(output_file, index=False)

print(f"Extracted {len(df)} ways and saved to {output_file}")
