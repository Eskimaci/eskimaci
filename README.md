# Project: Urban Greenery Analysis in Trnava

A web application for analyzing and visualizing long-term vegetation (NDVI) trends in Trnava. The project uses satellite data from Sentinel-2 and compares it with local temperature data to identify changes in the ecosystem.

---

## Key Features

The application provides two main analytical tools:

1.  **Dynamic Vegetation Trend Analysis**:
    -   The user can select any years (from 2017 onwards) and a pollen season.
    -   The application downloads live data from the **Sentinel Hub API** and generates a map that color-codes whether the greenery across Trnava is improving (green), deteriorating (red), or stagnating (white) over the long term.
    -   This tool is ideal for monitoring large-scale changes and the impacts of climate change or urbanization.

2.  **Pollen Season Onset Comparison**:
    -   The application displays interactive charts for selected parks and green areas in Trnava.
    -   The charts compare the development of the vegetation index (NDVI) and average temperatures over the years 2020-2025.
    -   This allows for identifying whether warmer winters are causing an earlier onset of the vegetation season, which is directly related to the start of pollen allergies.

---

## Technologies Used

*   **Backend**: [Flask](https://flask.palletsprojects.com/)
*   **Data Analysis & Processing**: [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/), [geopandas](https://geopandas.org/), [rasterio](https://rasterio.readthedocs.io/)
*   **Satellite Data**: [Sentinel Hub API](https://www.sentinel-hub.com/) (`sentinelhub-py`)
*   **Frontend**: Vanilla JavaScript, HTML5, CSS3
*   **Charting**: [Plotly.js](https://plotly.com/javascript/)
*   **Environment Configuration**: `python-decouple`

---

## Project Structure

    .
    ├── manage.py               # Main Flask server (API)
    ├── requirements.txt        # Python dependency list
    ├── README.md               # This file
    ├── docs/
    │   ├── DOCUMENTATION.md    # Technical documentation
    │   └── SENTINEL2-NDVI.md   # Data processing methodology
    ├── source/                 # Scripts for data preparation and analysis
    │   ├── long_term_analysis_trnava.py # Script for city-wide trend analysis
    │   ├── long_term_analysis.py # Script for downloading NDVI data for parks
    │   ├── getMeteoData.py     # Script for downloading temperature data
    │   └── ...                 # Other utility scripts
    ├── static/                 # Frontend assets (CSS, JS) and data (CSV, GeoJSON)
    │   ├── js/main.js          # Main frontend logic
    │   ├── csv_interpol_lin/   # Processed data for charts
    │   └── output/             # Generated trend maps
    └── templates/
        └── index.html          # Main HTML template


---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Eskimaci/eskimaci.git
cd eskimaci
```

### 2. Create and Activate a Virtual Environment
Ensure you have Python 3.11 or newer installed.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the environment (macOS/Linux)
source venv/bin/activate
# For Windows: venv\Scripts\activate
```

### 3. Configure API Access
Access to Sentinel Hub is required for the dynamic trend analysis and for downloading new data.

1.  Create a free account on the [**Copernicus Dataspace Ecosystem**](https://dataspace.copernicus.eu/).
2.  Create an *OAuth Client* in your dashboard to get a `Client ID` and `Client Secret`.
3.  In the project's root directory, create a file named `.env`.
4.  Add your credentials to the `.env` file:
    ```env
    CLIENT_ID="your-client-id"
    CLIENT_SECRET="your-client-secret"
    ```

### 4. Install Dependencies
All required libraries are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

<details>
<summary>⚠️ OS-Specific Installation Notes</summary>

Installing some geo-libraries (e.g., `rasterio`) can be complex due to their system-level dependencies (like the GDAL library).

*   **🪟 Windows:**
    *   Direct installation via `pip` might fail. It is recommended to use `conda` (from an Anaconda/Miniconda environment), which handles these dependencies automatically:
        ```bash
        conda install -c conda-forge geopandas rasterio
        ```
    *   After that, run `pip install -r requirements.txt`.

*   **🍎 macOS:**
    *   First, install GDAL using Homebrew:
        ```bash
        brew install gdal
        ```
    *   The `pip install -r requirements.txt` command should then work correctly.

*   **🐧 Linux (Debian/Ubuntu):**
    *   Install the development headers for GDAL:
        ```bash
        sudo apt-get update && sudo apt-get install libgdal-dev
        ```
    *   Then, proceed with `pip install`.
</details>

### 5. Run the Application
After activating the environment and installing the dependencies, start the server with:

```bash
python3 manage.py
```

The application will be available at [**http://127.0.0.1:5001**](http://127.0.0.1:5001).

---
> ### 💡 Note on Data Scripts
>
> The `source/` directory contains scripts (`getMeteoData.py`, `long_term_analysis.py`, `interpolacia.py`, etc.) for **manual data preparation**. These scripts do not run automatically and are not needed for the application's normal operation if you are using the data already present in the repository. They are only meant to be run if you need to download and process entirely new data (e.g., for different years or locations). More details can be found in the [Technical Documentation](docs/DOCUMENTATION.md).

