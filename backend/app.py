from flask import Flask, jsonify, send_from_directory
import rasterio
from pyproj import Transformer
from pathlib import Path
import os
import glob

# Create Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# Path to the GeoTIFF directory
GEOTIFF_DIR = "/data"

# Setup coordinate transformer from SWEREF 99 TM to WGS84
transformer = Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)

def get_geotiff_bounds():
    features = []

    for tif_path in glob.glob(os.path.join(GEOTIFF_DIR, "*.tif")):
        with rasterio.open(tif_path) as src:
            bounds = src.bounds

            # Reproject bounds corners to WGS84
            polygon_coords = [
                [bounds.left, bounds.top],
                [bounds.right, bounds.top],
                [bounds.right, bounds.bottom],
                [bounds.left, bounds.bottom],
                [bounds.left, bounds.top]
            ]
            polygon_coords_wgs84 = [list(transformer.transform(x, y)) for x, y in polygon_coords]

            # Create polygon feature
            polygon_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords_wgs84]
                },
                "properties": {
                    "filename": os.path.basename(tif_path),
                    "type": "extent"
                }
            }
            features.append(polygon_feature)

            # Reproject centroid to WGS84
            center_x = (bounds.left + bounds.right) / 2
            center_y = (bounds.top + bounds.bottom) / 2
            center_lon, center_lat = transformer.transform(center_x, center_y)

            point_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [center_lon, center_lat]
                },
                "properties": {
                    "filename": os.path.basename(tif_path),
                    "type": "centroid"
                }
            }
            features.append(point_feature)

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
