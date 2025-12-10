# Sentinel-2 Data Processing Methodology

This document explains how the project acquires and processes Sentinel-2 satellite data for vegetation analysis.

---

## 1. Primary Method: API Access (`sentinelhub`)

The project's main feature—dynamic trend analysis—**does not rely on manual data downloads**. Instead, it connects directly to the Sentinel Hub API using the `sentinelhub` Python library. This approach is fully automated and extremely efficient.

### Processing Workflow

The `long_term_analysis_trnava.py` script sends a request to the API that defines everything needed for server-side analysis:

1.  **Area of Interest (AOI):** The polygon geometry bounding the city of Trnava.
2.  **Time Filter:** The specific years and months selected by the user in the application.
3.  **Evalscript:** A short JavaScript snippet that executes directly on the Sentinel Hub servers, ensuring that the application receives already-processed data.

### The Key Component: Evalscript

The evalscript is the core of this efficiency. Instead of downloading raw spectral bands (`B04`, `B08`), the NDVI calculation is performed remotely, and the application only downloads the final product.

```javascript
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B08", "dataMask"] }],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}

function evaluatePixel(sample) {
  // Ignores pixels with no data (e.g., outside the scene)
  if (sample.dataMask === 0) { 
    return [NaN]; 
  }
  
  // Formula for NDVI
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
```

### Advantages of the API-First Approach

-   **Efficiency:** Only the resulting NDVI data is downloaded (a small amount of data) instead of entire scenes (often >1 GB).
-   **Automation:** The entire process is code-driven, with no need for manual intervention.
-   **Mosaicking:** The API automatically selects the best scenes (with the least cloud cover) and stitches them together into a single, seamless map for the given period.

---

## 2. Manual Data Exploration (Alternative)

For verification, exploration, or manual checks, data can also be downloaded manually via a web interface.

-   **Platform:** [Copernicus Browser](https://dataspace.copernicus.eu/browser)
-   **Key Filters:**
    -   **Data Source:** `Sentinel-2`
    -   **Product Level:** `L2A` (atmospherically corrected data)
    -   **Cloud Cover:** `0% - 20%` (to get the clearest shots)

After downloading and unzipping the `.zip` archive, the key bands for NDVI are located in the `.../[SAFE_NAME].SAFE/GRANULE/.../IMG_DATA/R10m/` directory:

-   `*_B04_10m.jp2`: **Red Band**
-   `*_B08_10m.jp2`: **Near-Infrared (NIR) Band**

---

## 3. Vegetation Index Used

-   **NDVI (Normalized Difference Vegetation Index)**
    -   **Purpose:** Measures the health and density of vegetation. It is the primary index used throughout the project.
    -   **Formula:** `(B08 - B04) / (B08 - B04)`

---

### Summary
The project primarily relies on a **modern and efficient API-first approach**, which enables dynamic and automated data processing. Manual downloading serves only as a supplementary method for exploration.