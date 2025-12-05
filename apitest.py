import numpy as np
from decouple import config
import matplotlib.pyplot as plt
from sentinelhub import (
    SentinelHubRequest, 
    DataCollection, 
    MimeType, 
    CRS, 
    SHConfig,
    MosaickingOrder,
    Geometry
)
import os

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
# 1000x1000 pixels for the requested bounding box
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
  // Calculate NDVI
  let numerator = sample.B08 - sample.B04;
  let denominator = sample.B08 + sample.B04;
  
  let ndvi = numerator / denominator;


  return [ndvi];
}
"""

EVALSCRIPT_LCI = """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B05", "B08", "dataMask"] }], 
    output: { bands: 1, sampleType: "FLOAT32" } // Output LCI as a single floating-point band
  };
}

function evaluatePixel(sample) {
  // Check for valid data
  if (sample.dataMask === 0) {
    return [0]; 
  }
  
  // Sentinel-2 L2A values are in the range 0 to 1
  let B04 = sample.B04; // Red
  let B05 = sample.B05; // Red Edge
  let B08 = sample.B08; // NIR

  // Calculate MCARI (Modified Chlorophyll Absorption Reflectance Index)
  let MCARI = (B05 - B04) - 0.2 * (B05 - B08);

  // Calculate OSAVI (Optimized Soil Adjusted Vegetation Index) with L=0.16
  let OSAVI = 1.16 * (B08 + 0.16);
  
  // Calculate LCI proxy using the MCARI/OSAVI ratio
  let LCI = (MCARI * (B05 / B04)) / OSAVI;
  
  return [LCI];
}
"""

# --- 4. BUILD THE REQUEST ---

requestNDVI = SentinelHubRequest(
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

requestLCI = SentinelHubRequest(
    evalscript=EVALSCRIPT_LCI,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=TIME_INTERVAL,
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

def createNDVItiff(ndvi_array):         
        # Save as a visual RGB TIFF for image viewers
        from PIL import Image
        import rasterio
        from rasterio.transform import from_bounds
        
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
        
        # Save georeferenced GeoTIFF in the output folder
        if not os.path.exists("static/output"):
            os.makedirs("static/output")

        output_folder = "static/output"
        
        geotiff_filename = os.path.join(output_folder, "ndvi_trnava_aug_2023.tif")
        
        # Get bounds from geometry
        coords = polygon_coordinates
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        bounds = (min(lons), min(lats), max(lons), max(lats))
        
        # Create transform
        transform = from_bounds(*bounds, ndvi_array.shape[1], ndvi_array.shape[0])
        
        # Save georeferenced TIFF
        with rasterio.open(
            geotiff_filename,
            'w',
            driver='GTiff',
            height=ndvi_array.shape[0],
            width=ndvi_array.shape[1],
            count=1,
            dtype=ndvi_array.dtype,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dst.write(ndvi_array, 1)
        
        print(f"Georeferenced GeoTIFF saved to: {geotiff_filename}")

def createLCItiff(lci_array):
    from PIL import Image
    from matplotlib import cm
    import numpy as np
    # --- LCI NORMALIZATION AND CLIPPING ---
        
    # 1. Define a Visualization Range for LCI
    # LCI values often range from 0 (low/bare) up to around 1.5 - 2.5 for dense, healthy canopy.
    #
    # LCI rozsah treba odhadnut lepsie, zatial najlepsie co som nasiel je:
    #
    LCI_MIN = 0.0  # Assumed minimum (bare soil/water)
    LCI_MAX = 1.0  # Assumed maximum for visualization (high chlorophyll)
    
    # 2. Clip the LCI data to the visualization range
    lci_clipped = np.clip(lci_array, LCI_MIN, LCI_MAX)
    
    # 3. Normalize the clipped data from [LCI_MIN, LCI_MAX] to [0, 1]
    lci_normalized = (lci_clipped - LCI_MIN) / (LCI_MAX - LCI_MIN)
    
    # --- VISUALIZATION ---
    
    # Create RGB image using matplotlib colormap (RdYlGn is good for vegetation indices)
    # Note: You need to specify a color map name, not cm.get_cmap('RdYlGn') directly 
    # as it may be deprecated in newer matplotlib versions.
    colormap = cm.get_cmap('RdYlGn') 
    
    # Map the normalized [0, 1] data to RGB colors
    rgb_array = colormap(lci_normalized)
    
    # Convert the RGB array (which is currently float [0, 1]) to 8-bit RGB [0, 255]
    # We only take the first three channels (R, G, B), ignoring the alpha channel (A)
    rgb_array_8bit = (rgb_array[:, :, :3] * 255).astype(np.uint8)
    
    # --- SAVE FILES ---
    
    # Save as a regular visual TIFF
    output_filename = "lci_trnava_aug_2023_visual.tif"
    img = Image.fromarray(rgb_array_8bit)
    img.save(output_filename)
    print(f"Visual TIFF saved to: {output_filename}")
    
    # Save georeferenced GeoTIFF in the output folder
    import rasterio
    from rasterio.transform import from_bounds
    
    if not os.path.exists("static/output"):
        os.makedirs("static/output")
    output_folder = "static/output"
    os.makedirs(output_folder, exist_ok=True)
    
    geotiff_filename = os.path.join(output_folder, "lci_trnava_aug_2023.tif")
    
    # Get bounds from geometry
    coords = polygon_coordinates
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    bounds = (min(lons), min(lats), max(lons), max(lats))
    
    # Create transform
    transform = from_bounds(*bounds, lci_array.shape[1], lci_array.shape[0])
    
    # Save georeferenced TIFF
    with rasterio.open(
        geotiff_filename,
        'w',
        driver='GTiff',
        height=lci_array.shape[0],
        width=lci_array.shape[1],
        count=1,
        dtype=lci_array.dtype,
        crs='EPSG:4326',
        transform=transform,
    ) as dst:
        dst.write(lci_array, 1)
    
    print(f"Georeferenced GeoTIFF saved to: {geotiff_filename}") 

if __name__ == "__main__":
    print("Executing Sentinel Hub request...")
    try:
        print(f"\n✅ Request successful!")
        dataNDVI = requestNDVI.get_data()
        ndvi_array = dataNDVI[0]
        print(f"NDVI array shape: {ndvi_array.shape}")

        dataLCI = requestLCI.get_data()
        lci_array = dataLCI[0]

        createNDVItiff(ndvi_array)
        createLCItiff(lci_array)

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


        plt.figure(figsize=(8, 8))
        plt.imshow(lci_array, cmap='RdYlGn', vmin=-1.0, vmax=1.0) 
        plt.colorbar(label='LCI Value', orientation='vertical')
        plt.title(f"LCI from Sentinel-2 (Trnava, August 2023)")
        plt.xlabel("Pixel X")
        plt.ylabel("Pixel Y")
        plt.show()