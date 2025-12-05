# SENTINEL-2 DATA CONFIGURATION

## 1. Access Platform
* **URL:** [Copernicus Browser](https://dataspace.copernicus.eu/browser)
* **Login:** Required for downloading.

## 2. Search Filters (Copy & Paste)
Configure the search panel on the left with these exact parameters to match the hackathon requirements:

* **Location:** `Trnava, Slovakia`
* **Data Source:** `Sentinel-2`
* [cite_start]**Product Level:** `L2A` (Level-2A, Atmospherically Corrected) [cite: 88]
  * *Note: Do NOT use L1C (Top of Atmosphere).*
* **Cloud Cover:** `0% - 20%`
  * [cite_start]*Tip: Aim for 0-10%, but 20% is acceptable if the ROI (Trnava) is clear.* [cite: 87]
* **Time Range:** `2023-06-01` to `2023-08-31` (Summer months for best vegetation contrast)
  * [cite_start]*Alternative:* Compare with `2024-06-01` to `2024-08-31` for year-over-year analysis. [cite: 10]

## 3. Download Process
1.  **Visualize:** Check the preview image to ensure Trnava is not covered by clouds.
2.  **Download:** Click the "Download" icon.
3.  **File Format:** `.zip` archive (approx. 800MB - 1.2GB).
4.  **Extraction:** Unzip to get the `.SAFE` directory.

## 4. File Structure & Path to Bands
Inside the unzipped `.SAFE` folder, navigate to the 10m resolution bands:

**Path:**
`./[SAFE_NAME].SAFE/GRANULE/[GRANULE_NAME]/IMG_DATA/R10m/`

**Key Files (10m Resolution):**
* `*_B02_10m.jp2` -> **Blue** (Water bodies)
* `*_B03_10m.jp2` -> **Green** (Vegetation peak)
* [cite_start]`*_B04_10m.jp2` -> **Red** (Vegetation absorption - crucial for NDVI) [cite: 98]
* [cite_start]`*_B08_10m.jp2` -> **NIR** (Near-Infrared - crucial for NDVI) [cite: 98]

## 5. Optimization Tips (Hackathon Mode)
* **RAM Warning:** The full image covers 100x100km. [cite_start]Do not load the whole file if you have limited RAM. [cite: 92]
* [cite_start]**Subsetting:** Use a GeoJSON mask to crop the data to Trnava only. [cite: 93]
    * Tool: [geojson.io](https://geojson.io) -> Draw polygon around Trnava -> Save as `trnava.geojson`.
* **Cloud Masking:** If clouds are present, use the Scene Classification Layer (SCL) found in `IMG_DATA/R20m/` to mask them out.

## 6. Common Indices Formulas (Python/Numpy)
* [cite_start]**NDVI (Vegetation):** `(B08 - B04) / (B08 + B04)` [cite: 99]
* [cite_start]**NDWI (Water):** `(B03 - B08) / (B03 + B08)` [cite: 9]