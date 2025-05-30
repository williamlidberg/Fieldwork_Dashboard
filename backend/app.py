from flask import Flask, jsonify, send_from_directory
import rasterio
from pathlib import Path
import os
import glob

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
GEOTIFF_DIR = "/data"

def get_geotiff_bounds():
    features = []
    for tif_path in glob.glob(os.path.join(GEOTIFF_DIR, "*.tif")):
        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [bounds.left, bounds.top],
                        [bounds.right, bounds.top],
                        [bounds.right, bounds.bottom],
                        [bounds.left, bounds.bottom],
                        [bounds.left, bounds.top]
                    ]]
                },
                "properties": {
                    "filename": os.path.basename(tif_path)
                }
            })
    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.route("/api/scan-extents")
def scan_extents():
    return jsonify(get_geotiff_bounds())

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
