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
    MosaickingOrder,
    Geometry
)

# --- 1. CONFIGURATION ---

# Load credentials from .env file
CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

# Configure Sentinel Hub API
config = SHConfig()
config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET

# --- 2. DEFINE REQUEST PARAMETERS ---

# Area of Interest (AOI): Trnava
# Coordinates are defined as (min_x, min_y, max_x, max_y) in WGS84 CRS (EPSG:4326)
polygon_coordinates = [
    [
              17.572404371198303,
              48.38602850840101
            ],
            [
              17.54711099372517,
              48.38190722723843
            ],
            [
              17.547585841075488,
              48.37002151811984
            ],
            [
              17.57025398010623,
              48.34845776922049
            ],
            [
              17.629438958596808,
              48.33751242125385
            ],
            [
              17.650432762218827,
              48.36050767001183
            ],
            [
              17.609390031826052,
              48.3768349941939
            ],
            [
              17.61439982889695,
              48.391254333499944
            ],
            [
              17.58361950944743,
              48.4043997142976
            ],
            [
              17.560951961203756,
              48.3925219286466
            ],
            [
              17.567871150498718,
              48.38824510665356
            ],
            [
              17.572404371198303,
              48.38602850840101
            ]
]


AOI_GEOMETRY = Geometry(
    geometry={
        "type": "Polygon",  
        "coordinates": [polygon_coordinates]
    },
    crs=CRS.WGS84
)

# Time range for the request (Look for a single, cloud-free image)
TIME_INTERVAL = ('2023-08-01', '2023-08-30')

# Output resolution and format
# 512x512 pixels for the requested bounding box
OUTPUT_SIZE = [1000, 1000] 
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
    geometry = AOI_GEOMETRY,
    size=OUTPUT_SIZE,
    data_folder='.',
    config=config
)

# --- 5. EXECUTE AND VISUALIZE ---

print("Executing Sentinel Hub request...")

try:
    # Get the data as numpy array
    data = request.get_data()
    ndvi_array = data[0]
    
    print(f"\n✅ Request successful!")
    print(f"NDVI array shape: {ndvi_array.shape}")
    
    # Save as a visual RGB TIFF for image viewers
    from PIL import Image
    
    # Normalize NDVI from [-1, 1] to [0, 255] for RGB visualization
    # Apply colormap: red for low values, yellow for medium, green for high
    ndvi_normalized = np.clip((ndvi_array + 1) / 2, 0, 1)  # Map [-1,1] to [0,1]
    
    # Create RGB image using matplotlib colormap
    from matplotlib import cm
    colormap = cm.get_cmap('RdYlGn')
    rgb_array = colormap(ndvi_normalized)
    rgb_array = (rgb_array[:, :, :3] * 255).astype(np.uint8)  # Convert to 8-bit RGB
    
    # Save as regular TIFF
    output_filename = "ndvi_trnava_aug_2023_visual.tif"
    img = Image.fromarray(rgb_array)
    img.save(output_filename)
    print(f"Visual TIFF saved to: {output_filename}")
    
    # Also save the georeferenced version for GIS use
    request.save_data(redownload=True)
    print(f"Georeferenced GeoTIFF saved to: ./e7b26b530a0ec6c28408f96c265692f5/response.tiff")
    
except Exception as e:
    print(f"An error occurred during request execution: {e}")
    print("Please check your CLIENT_ID and CLIENT_SECRET and ensure your time interval has valid, cloud-free data.")
    exit()

# Optional: Visualize the result
plt.figure(figsize=(8, 8))
plt.imshow(ndvi_array, cmap='RdYlGn', vmin=-1.0, vmax=1.0) 
plt.colorbar(label='NDVI Value', orientation='vertical')
plt.title(f"NDVI from Sentinel-2 (Trnava, August 2023)")
plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")
plt.show()
