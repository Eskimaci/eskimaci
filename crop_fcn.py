import rasterio
from rasterio.mask import mask
import json
import os


geojson_path = "static/geojson/trnava.geojson" # Cesta k geojson file

input_b2 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B02_10m.jp2"
input_b3 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B03_10m.jp2"
input_b4 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B04_10m.jp2"
input_b8 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B08_10m.jp2"

output_b2 = "static/cropped/trnava_b2.tif"
output_b3 = "static/cropped/trnava_b3.tif"
output_b4 = "static/cropped/trnava_b4.tif"
output_b8 = "static/cropped/trnava_b8.tif"


def crop_raster(input, output, shapes):
    """Funkcia na orezanie podľa GeoJSON"""
    print(f"Orezávam: {input} ...")

    with rasterio.open(input) as src:
        out_image, out_transform = mask(src, shapes, crop=True)
        out_meta = src.meta.copy()

        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        with rasterio.open(output, "w", **out_meta) as dest:
            dest.write(out_image)
    print(f"Hotovo! Ulozene ako: {output}")

# ---- SPUSTENIE ----

# Nacitanie geometrie z geojson
with open(geojson_path, "r") as f:
    geojson = json.load(f)

# Extrakcia polygonov z GeoJSON
shapes = [feature["geometry"] for feature in geojson["features"]]

# Orezanie pasiem
crop_raster(input_b4, output_b4, shapes)
crop_raster(input_b8, output_b8, shapes)