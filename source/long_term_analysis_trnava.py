# -*- coding: utf-8 -*-
"""
Script for long-term analysis of the vegetation index (NDVI) from Sentinel-2 data.

This script performs the following steps:
1. Connects to the Sentinel Hub API.
2. For a defined area (Trnava) and time period (e.g., last 3 years, August), 
   it downloads NDVI data.
3. Calculates the vegetation development trend for each pixel using linear regression.
4. Creates and saves a summary map that colorfully visualizes this trend 
   (improvement, deterioration, stable).
"""

import os
import matplotlib
import numpy as np
from decouple import config

matplotlib.use('Agg')  # Must be before importing pyplot to prevent crash on macOS
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sentinelhub import (
    SentinelHubRequest,
    DataCollection,
    MimeType,
    CRS,
    Geometry,
    SHConfig,
    MosaickingOrder
)

# --- 1. BASIC CONFIGURATION ---

# Loading credentials from .env file
try:
    CLIENT_ID = config('CLIENT_ID')
    CLIENT_SECRET = config('CLIENT_SECRET')
except Exception as e:
    print(
        f"Error: Could not load CLIENT_ID or CLIENT_SECRET from .env file. Ensure the file exists and the variables are set. Details: {e}")
    # Do not exit, allow for a server to handle this error
    # exit() 

# Sentinel Hub API Configuration
sh_config = SHConfig()
if CLIENT_ID and CLIENT_SECRET:
    sh_config.sh_client_id = CLIENT_ID
    sh_config.sh_client_secret = CLIENT_SECRET
else:
    print("Warning: CLIENT_ID or CLIENT_SECRET are not configured. Requests to Sentinel Hub will fail.")

# Defining the Area of Interest (AOI) - Trnava
POLYGON_COORDINATES = [
    [[17.5724, 48.3860], [17.5471, 48.3819], [17.5475, 48.3700], [17.5702, 48.3484],
     [17.6294, 48.3375], [17.6504, 48.3605], [17.6093, 48.3768], [17.6143, 48.3912],
     [17.5836, 48.4043], [17.5609, 48.3925], [17.5678, 48.3882], [17.5724, 48.3860]]
]
AOI_GEOMETRY = Geometry(geometry={"type": "Polygon", "coordinates": POLYGON_COORDINATES}, crs=CRS.WGS84)

# Output parameters
OUTPUT_SIZE = [500, 500]  # Reduced size for faster testing
OUTPUT_FORMAT = MimeType.TIFF

# Evalscript for NDVI calculation
EVALSCRIPT_NDVI = """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B08", "dataMask"] }],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  if (sample.dataMask === 0) { return [NaN]; } // Use NaN for no data
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
"""


# --- 2. ANALYSIS FUNCTIONS ---

def get_ndvi_for_year(year, target_month_start, target_month_end, config, geometry, size):
    """Downloads NDVI data for the specified year and month range."""
    print(f"Downloading data for year {year} (period {target_month_start} to {target_month_end})...")
    time_interval = (f'{year}-{target_month_start}', f'{year}-{target_month_end}')
    request = SentinelHubRequest(
        evalscript=EVALSCRIPT_NDVI,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ],
        responses=[SentinelHubRequest.output_response('default', OUTPUT_FORMAT)],
        geometry=geometry,
        size=size,
        config=config
    )
    try:
        data = request.get_data(save_data=False)
        if not data:
            print(f"Warning: No data returned for year {year}.")
            return None
        ndvi_array = data[0]
        # Replace zeros (usually no-data) with NaN to not affect calculations
        ndvi_array[ndvi_array == 0] = np.nan
        print(
            f"DEBUG [{year}]: Data shape: {ndvi_array.shape}, Min: {np.nanmin(ndvi_array):.4f}, Max: {np.nanmax(ndvi_array):.4f}, Mean: {np.nanmean(ndvi_array):.4f}")
        return ndvi_array
    except Exception as e:
        print(f"Error downloading data for year {year}: {e}")
        return None


def generate_trend_map(years_to_analyze, target_month_start, target_month_end):
    """
    Main function that orchestrates the entire analysis process and returns the path to the generated image.
    """
    print(
        f"--- Starting long-term NDVI trend analysis for years {years_to_analyze} and period {target_month_start}-{target_month_end} ---")

    if not sh_config.sh_client_id:
        raise Exception("Configuration error: Sentinel Hub Client ID is not set.")

    yearly_ndvi_data = [
        get_ndvi_for_year(year, target_month_start, target_month_end, sh_config, AOI_GEOMETRY, OUTPUT_SIZE) for year in
        years_to_analyze]

    # Filter out years for which data download failed
    valid_years_data = [(year, data) for year, data in zip(years_to_analyze, yearly_ndvi_data) if
                        data is not None and not np.isnan(data).all()]

    if len(valid_years_data) < 2:
        print("Error: Trend analysis requires data from at least two valid years. Exiting.")
        return None

    # Unpack valid data
    valid_years, yearly_ndvi_data = zip(*valid_years_data)

    # Stack data into a single 3D numpy array (years, height, width)
    y = np.stack(yearly_ndvi_data, axis=0)
    print(f"DEBUG: Shape of stacked array (y): {y.shape}")

    print("Calculating trend for each pixel...")
    n_years = y.shape[0]
    x = np.arange(n_years)
    x_reshaped = x.reshape(n_years, 1, 1)

    # Use nanmean to ignore pixels without data
    mean_x = np.mean(x)
    mean_y = np.nanmean(y, axis=0)

    # Calculate numerator and denominator, ignoring NaN values
    numerator = np.nansum((x_reshaped - mean_x) * (y - mean_y), axis=0)
    denominator = np.sum((x - mean_x) ** 2)

    trend_map = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator != 0)

    # Masking areas with no valid data
    trend_map[np.isnan(mean_y)] = np.nan

    print("Trend calculation finished.")
    print(
        f"DEBUG: Trend map statistics - Min: {np.nanmin(trend_map):.4f}, Max: {np.nanmax(trend_map):.4f}, Mean: {np.nanmean(trend_map):.4f}")

    print("Creating and saving trend map...")
    with plt.style.context('default'):
        cmap_trend = LinearSegmentedColormap.from_list("trend_map", [(0, "red"), (0.5, "white"), (1, "green")])
        plt.figure(figsize=(12, 10))

        # Ignore NaN when calculating percentile
        vlim = np.nanpercentile(np.abs(trend_map), 98)
        if vlim == 0: vlim = 1.0

        img = plt.imshow(trend_map, cmap=cmap_trend, vmin=-vlim, vmax=vlim)
        plt.colorbar(img, label="NDVI Trend Slope (change per year)")
        plt.title(f"Vegetation Development Trend in Trnava ({valid_years[0]}-{valid_years[-1]})")
        plt.xlabel("Pixel X")
        plt.ylabel("Pixel Y")

        # Saving to static folder
        output_dir = "static/output"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"trend_map_{valid_years[0]}-{valid_years[-1]}_{target_month_start.replace('-','')}_{target_month_end.replace('-','')}.png"
        output_filepath = os.path.join(output_dir, filename)
        
        plt.savefig(output_filepath, dpi=150)  # Reduced DPI for faster generation
        plt.close()  # Freeing memory

    print(f"✅ Trend map successfully saved as: {output_filepath}")
    return output_filepath


# --- 3. MAIN PROCESSING (for direct execution) ---

if __name__ == "__main__":
    """Example run for testing purposes."""
    print("--- Running test analysis for direct script execution ---")

    # Parameters for test
    test_years = [2022, 2023, 2024]
    test_month_start = "06-01"
    test_month_end = "08-31"

    try:
        image_path = generate_trend_map(test_years, test_month_start, test_month_end)
        if image_path:
            print(f"\nTest successful. Resulting image is at: {image_path}")
        else:
            print("\nTest failed. No image was created.")
    except Exception as e:
        print(f"An error occurred during the test: {e}")
