import os
import json
import requests
import numpy as np
from rasterio.transform import from_origin
import rasterio
from PIL import Image
from io import BytesIO

TILE_SIZE = 2000
RESOLUTION = 1.0
X_OFFSET = 369097.8529
Y_OFFSET = 5799298.1358
CRS = 'EPSG:25833'

def download_tile(wms_url, layer, x, y, year_dir, year):
    xmin = X_OFFSET + x * TILE_SIZE
    ymin = Y_OFFSET + y * TILE_SIZE
    xmax = xmin + TILE_SIZE
    ymax = ymin + TILE_SIZE
    bbox = f"{xmin},{ymin},{xmax},{ymax}"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "BBOX": bbox,
        "CRS": CRS,
        "WIDTH": TILE_SIZE,
        "HEIGHT": TILE_SIZE,
        "LAYERS": layer,
        "STYLES": "",
        "FORMAT": "image/jpeg"
    }
    url = wms_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    output = os.path.join(year_dir, f"tile_{x}_{y}_{year}.tif")
    if os.path.exists(output):
        print(f"Already exists: {output}")
        return
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content))
        img_array = np.array(img)

        if len(img_array.shape) == 2:
            img_array = np.stack((img_array,) * 3, axis=-1)
        elif img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]

        transform = from_origin(xmin, ymin + TILE_SIZE, RESOLUTION, RESOLUTION)

        with rasterio.open(
            output, 'w',
            driver='GTiff',
            height=img_array.shape[0],
            width=img_array.shape[1],
            count=3,
            dtype=img_array.dtype,
            crs=CRS,
            transform=transform
        ) as dst:
            dst.write(img_array.transpose(2, 0, 1))

        print(f"Downloaded and saved: {output}")
    except Exception as e:
        print(f"Failed to download {output}: {e}")

def process_year(year, layer_name):
    year_dir = os.path.join("../data/berlin-tiles", year)
    os.makedirs(year_dir, exist_ok=True)
    with open("randomTileIndices.json") as f:
        tiles = json.load(f)
    for tile in tiles:
        x, y = tile["i"], tile["j"]
        download_tile(f"https://fbinter.stadt-berlin.de/fb/wms/senstadt/{layer_name}", layer_name, x, y, year_dir, year)

if __name__ == "__main__":
    wms_layers = {
        "2004": "k_luftbild2004_rgb",
        "2007": "k_luftbild2007_rgb",
        "2009": "k_luftbild2009_rgb",
        "2010": "k_luftbild2010_rgb",
        "2011": "k_luftbild2011_rgb",
        "2014": "k_luftbild2014_rgb",
        "2015": "k_luftbild2015_rgb",
        "2016": "k_luftbild2016_rgb",
        "2017": "k_luftbild2017_rgb",
        "2018": "k_luftbild2018_rgb",
        "2019": "k_luftbild2019_rgb"
    }
    for year, layer in wms_layers.items():
        process_year(year, layer)
