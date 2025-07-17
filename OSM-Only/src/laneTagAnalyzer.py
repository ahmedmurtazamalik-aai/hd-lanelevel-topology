import osmium

class LaneTagAnalyzer(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.lane_tagged_ways = 0
        self.total_ways = 0
        self.sample_tags = []

    def way(self, w):
        self.total_ways += 1
        tags = {tag.k: tag.v for tag in w.tags}
        if "lanes" in tags:
            self.lane_tagged_ways += 1
            if len(self.sample_tags) < 10:
                self.sample_tags.append(tags)

handler = LaneTagAnalyzer()
handler.apply_file("../data/osm-data/berlin-latest.osm.pbf")  # Adjust path as necessary

print("Total ways:", handler.total_ways)
print("Ways with 'lanes' tag:", handler.lane_tagged_ways)
print("Percentage with 'lanes':", round((handler.lane_tagged_ways / handler.total_ways) * 100, 2))
print("Sample lane-tagged ways:", handler.sample_tags)
