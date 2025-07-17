import osmium
import csv
import sys

class HighwayHandler(osmium.SimpleHandler):
    def __init__(self, csv_writer):
        super().__init__()
        self.writer = csv_writer
        self.allowed_types = {
            "motorway", "trunk", "primary", "secondary", "tertiary",
            "residential", "living_street", "service"
        }

    def way(self, w):
        if 'highway' not in w.tags:
            return

        highway_type = w.tags['highway']
        if highway_type not in self.allowed_types:
            return

        name = w.tags.get('name', "")
        for idx, node in enumerate(w.nodes):
            if not node.location.valid():
                continue
            self.writer.writerow([
                w.id, highway_type, name, idx,
                node.location.lon, node.location.lat
            ])
        print(f"Way ID: {w.id}, Type: {highway_type}, Name: {name}, Nodes: {len(w.nodes)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python osmReader.py <file.osm.pbf>")
        sys.exit(1)

    pbf_path = sys.argv[1]
    output_csv_path = "../../roads.csv"

    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["way_id", "highway_type", "way_name", "node_index", "lon", "lat"])

        handler = HighwayHandler(writer)
        handler.apply_file(pbf_path, locations=True)

    print("CSV export complete.")
