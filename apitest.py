import numpy as np
from decouple import config
import matplotlib.pyplot as plt
from sentinelhub import (
    SentinelHubRequest, 
    DataCollection, 
    MimeType, 
    CRS, 
    BBox, 
    SHConfig,
    MosaickingOrder
)

# --- 1. CONFIGURATION ---

# !!! REPLACE THESE WITH YOUR ACTUAL SENTINEL HUB CREDENTIALS !!!
# You can get these from your Sentinel Hub Dashboard
clinet_id = config('CLIENT_ID')
client_secret = config('CLIENT_SECRET')
CLIENT_ID = clinet_id
CLIENT_SECRET = client_secret

config = SHConfig()
config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET

# --- 2. DEFINE REQUEST PARAMETERS ---

# Area of Interest (AOI): A small agricultural area near Fresno, California
# Coordinates are defined as (min_x, min_y, max_x, max_y) in WGS84 CRS (EPSG:4326)
AOI_BBOX = [-119.5, 36.6, -119.4, 36.7]
AOI_CRS = CRS.WGS84 

# Time range for the request (Look for a single, cloud-free image)
TIME_INTERVAL = ('2023-08-01', '2023-08-30')

# Output resolution and format
# 512x512 pixels for the requested bounding box
OUTPUT_SIZE = [512, 512] 
OUTPUT_FORMAT = MimeType.TIFF 

# --- 3. THE EVALSCRIPT (JavaScript logic) ---

# This script calculates the Normalized Difference Vegetation Index (NDVI)
# NDVI = (NIR - Red) / (NIR + Red)
# Sentinel-2 bands: B08 = Near Infrared (NIR), B04 = Red
EVALSCRIPT_NDVI = """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B08", "dataMask"] }], // Red, NIR, and dataMask for cloud check
    output: { bands: 1, sampleType: "FLOAT32" }     // Single band output, floating point for NDVI value
  };
}

function evaluatePixel(sample) {
  // Check if there is valid data (not masked by clouds/shadows)
  if (sample.dataMask === 0) {
    return [0]; // Return 0 (water/bare soil range) for no data
  }
  
  let numerator = sample.B08 - sample.B04;
  let denominator = sample.B08 + sample.B04;
  
  let ndvi = numerator / denominator;
  
  return [ndvi];
}
"""

# --- 4. BUILD THE REQUEST ---

request = SentinelHubRequest(
    evalscript=EVALSCRIPT_NDVI,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A, # Using Level 2A (Atmospherically Corrected) data
            time_interval=TIME_INTERVAL,
            # Find the scene with least cloud cover within the interval
            mosaicking_order=MosaickingOrder.LEAST_CC,
        )
    ],
    responses=[
        SentinelHubRequest.output_response(
            'default', 
            OUTPUT_FORMAT
        )
    ],
    bbox=BBox(bbox=AOI_BBOX, crs=AOI_CRS),
    size=OUTPUT_SIZE,
    config=config
)

# --- 5. EXECUTE AND VISUALIZE ---

print("Executing Sentinel Hub request...")
try:
    data = request.get_data()
except Exception as e:
    print(f"An error occurred during request execution: {e}")
    print("Please check your CLIENT_ID and CLIENT_SECRET and ensure your time interval has valid, cloud-free data.")
    exit()

# The result is a list of data arrays (one for each time step requested, which is usually one)
ndvi_array = data[0]

# Save the GeoTIFF file (metadata for georeferencing is included by default)
output_filename = "ndvi_fresno_aug_2023.tif"
with open(output_filename, 'wb') as f:
    f.write(ndvi_array.tobytes())

print(f"\n✅ Request successful! Data saved to: {output_filename}")
print(f"Shape of the resulting array: {ndvi_array.shape}")

# Optional: Visualize the result
plt.figure(figsize=(8, 8))
# Squeeze to remove the single-band dimension (512, 512, 1) -> (512, 512)
plt.imshow(np.squeeze(ndvi_array), cmap='RdYlGn', vmin=-1.0, vmax=1.0) 
plt.colorbar(label='NDVI Value', orientation='vertical')
plt.title(f"NDVI from Sentinel-2 (Least Cloudy in August 2023)")
plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")
plt.show()
