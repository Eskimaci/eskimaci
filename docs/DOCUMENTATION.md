# Project Technical Documentation

This document provides a detailed technical overview of the individual scripts and components in the project.

## Project Structure

The project consists of the following parts:

-   **Backend**: An application built on the Flask framework (`manage.py`), which serves as an API for the frontend.
-   **Frontend**: A single-page application (SPA) written in vanilla JavaScript, HTML, and CSS (`static/` and `templates/`).
-   **Data Scripts**: A set of Python scripts in the `source/` directory designed for manual retrieval, processing, and analysis of data from external sources (Sentinel Hub, Open-Meteo).
-   **Static Files**: The `static/` directory contains CSS styles, JavaScript code, GeoJSON files, CSV data, and generated image outputs.

---

## `manage.py`

The main application server, built on `Flask`. It handles serving the frontend application (`index.html`) and provides API endpoints to process requests from the frontend. It is launched with the command `python3 manage.py`.

### Libraries
- `flask`: The web framework.
- `pandas`: For processing and analyzing data from CSV files.
- `plotly`: For preparing data structures for interactive charts.
- `source.long_term_analysis_trnava`: Imports the `generate_trend_map` function for on-the-fly analysis.

### Configuration
- `POLLEN_TO_MONTHS`: A dictionary that maps season names (`early_spring`, `mid_spring`, etc.) to specific month and day ranges for the `/api/analyze` endpoint.

### API Endpoints

#### `GET /`
- **Description**: Serves the main `index.html` page.
- **Returns**: An HTML page.

#### `POST /api/plot`
- **Description**: Receives a request with a location name, loads pre-processed data, and returns it in a format suitable for Plotly.js.
- **Input JSON data**:
    - `location` (string): The location key (e.g., `janka-krala`, `nemocnicny`).
- **Data Sources**:
    - NDVI data: `static/csv_interpol_lin/<location>.csv`
    - Temperature data: `static/temperature_comparison.csv`
- **Return Value (JSON)**:
    - `ndvi_data`: A JSON string with data for the NDVI chart.
    - `temp_data`: A JSON string with data for the temperature chart.
    - `threshold_dates`: A JSON string with data on the days when the temperature exceeded 5°C for 5 consecutive days.

#### `POST /api/analyze`
- **Description**: Triggers a live, long-term analysis of the vegetation trend based on the selected years and season. It calls the `generate_trend_map` function from the `long_term_analysis_trnava.py` script.
- **Input JSON data**:
    - `years` (list): A list of years to analyze (e.g., `[2022, 2023, 2024]`).
    - `season` (string): The name of the season (e.g., `late_spring`).
- **Return Value (JSON)**:
    - `image_url`: The URL path to the generated trend map image (e.g., `/static/output/trend_map_2022-2024_late_spring.png`).

#### `GET /api/current_pollen`
- **Description**: Loads data on average pollen loads from the `static/pollenAverageLoads.csv` file.
- **Return Value (JSON)**:
    - `pollen_data`: Data prepared for rendering in a chart.

---

## `static/js/main.js`

The frontend logic of the application. It is responsible for dynamic content loading, user interaction, communication with the backend API, and rendering charts using the Plotly.js library.

### Main Functions

- **`loadVegetaciu(contentDiv)`**: Prepares the UI for vegetation trend analysis (year and season selection).
- **`loadPollenSeason(contentDiv)`**: Prepares the UI for pollen season onset analysis (location selection).
- **`loadCurrentPollen(contentDiv)`**: Loads and displays a chart with the current pollen situation.
- **`handleAnalysis()`**: Collects user inputs, sends a request to `/api/analyze`, and displays the resulting map once the URL is received.
- **`handlePollenAnalysis()`**: Collects user inputs, sends a request to `/api/plot`, and renders the charts using the `renderPlots` function.
- **`renderPlots(...)`**: Renders interactive NDVI and temperature charts using Plotly.
- **`renderPollenPlots(...)`**: Renders the current pollen situation chart.

---

## Data Scripts (`source/`)

These scripts are not run as part of the web application. They are **tools for manual data preparation**, which the application then uses.

### `long_term_analysis_trnava.py`
This script is used directly by the `/api/analyze` endpoint for live analysis of the NDVI trend over time for the entire city of Trnava.

- **Libraries**: `sentinelhub`, `numpy`, `matplotlib`, `decouple`.
- **Configuration**: Requires an `.env` file with `CLIENT_ID` and `CLIENT_SECRET` for Sentinel Hub API access.
- **Function**:
    - **`generate_trend_map(years_to_analyze, month_start, month_end)`**: For the given years, it downloads data, calculates a linear regression for each pixel, and generates a trend map. The map is saved to `static/output/`.

### Chart Data Preparation (Manual Process)

The data for the charts comparing NDVI and temperature is not generated live but goes through a manual, multi-step process.

#### Step 1: `long_term_analysis.py`
This script downloads **raw data** for specific parks.
- **Description**: For each defined park and for each year, it downloads average NDVI data at 2-week intervals from Sentinel Hub.
- **Output**: `static/csv_raw_linear/ndvi_yearly_comparison_*.csv`. These files contain raw data with potential gaps (due to cloud cover).

#### Step 2: `interpolacia.py`
This script **cleans and completes the data**.
- **Description**: It loads the raw NDVI data from `static/csv_raw_linear/`, filters out low values (< 0.4), and fills in missing data using linear interpolation.
- **Input**: `static/csv_raw_linear/ndvi_yearly_comparison_*.csv`
- **Output**: `static/csv_interpol_lin/<park-name>.csv`. This "cleaned" data is used by the `/api/plot` endpoint.

#### Step 3: `getMeteoData.py`
This script downloads **historical temperature data**.
- **Description**: It uses the Open-Meteo API to download daily average temperatures. It then processes and saves the data.
- **Output**: `static/temperature_comparison.csv`, which is used by the `/api/plot` endpoint.

### Other Scripts

#### `createGeojson.py`
- **Description**: An interactive command-line tool that creates a `*.geojson` file from input coordinates. It is used to define the boundaries of parks in `static/geojson/`.
- **Usage**: `python source/createGeojson.py <fileName> [--longlat|--latlong]`

#### `traspose.py`
- **Description**: A simple tool for transposing (swapping rows and columns) a CSV file. It was likely used for a one-time data transformation, such as for `static/pollenAverageLoads.csv`.
