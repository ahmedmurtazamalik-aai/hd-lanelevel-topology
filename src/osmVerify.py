import csv
import random

# Config
csv_path = '../data/roads.csv'
num_samples = 50  # Change this to how many points you want

links = []

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

    # Sample randomly
    sampled_rows = random.sample(rows, min(num_samples, len(rows)))

    for row in sampled_rows:
        lat = row['lat']
        lon = row['lon']
        name = row['way_name']
        url = f"https://www.google.com/maps?q={lat},{lon}"
        links.append(f"{name} ({lat}, {lon}) → {url}")

# Print links to console
print("\n🗺️ Verification Links:\n")
for link in links:
    print(link)