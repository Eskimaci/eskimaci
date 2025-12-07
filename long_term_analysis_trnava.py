# -*- coding: utf-8 -*-
"""
Skript pre dlhodobú analýzu vegetačného indexu (NDVI) z dát Sentinel-2.

Tento skript vykonáva nasledujúce kroky:
1. Pripojí sa k Sentinel Hub API.
2. Pre definovanú oblasť (Trnava) a časové obdobie (posledné 3 roky, mesiac august) 
   stiahne dáta NDVI.
3. Vypočíta trend vývoja vegetácie pre každý pixel pomocou lineárnej regresie.
4. Vytvorí a uloží sumárnu mapu, ktorá farebne vizualizuje tento trend 
   (zlepšenie, zhoršenie, stabilný stav).
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

# --- 1. ZÁKLADNÁ KONFIGURÁCIA ---

# Načítanie prihlasovacích údajov z .env súboru
try:
    CLIENT_ID = config('CLIENT_ID')
    CLIENT_SECRET = config('CLIENT_SECRET')
except Exception as e:
    print(
        f"Chyba: Nepodarilo sa načítať CLIENT_ID alebo CLIENT_SECRET z .env súboru. Uistite sa, že súbor existuje a premenné sú nastavené. Detaily: {e}")
    # Do not exit, allow for a server to handle this error
    # exit() 

# Konfigurácia Sentinel Hub API
sh_config = SHConfig()
if CLIENT_ID and CLIENT_SECRET:
    sh_config.sh_client_id = CLIENT_ID
    sh_config.sh_client_secret = CLIENT_SECRET
else:
    print("Varovanie: CLIENT_ID alebo CLIENT_SECRET nie sú nakonfigurované. Požiadavky na Sentinel Hub zlyhajú.")

# Definovanie oblasti záujmu (AOI) - Trnava
POLYGON_COORDINATES = [
    [[17.5724, 48.3860], [17.5471, 48.3819], [17.5475, 48.3700], [17.5702, 48.3484],
     [17.6294, 48.3375], [17.6504, 48.3605], [17.6093, 48.3768], [17.6143, 48.3912],
     [17.5836, 48.4043], [17.5609, 48.3925], [17.5678, 48.3882], [17.5724, 48.3860]]
]
AOI_GEOMETRY = Geometry(geometry={"type": "Polygon", "coordinates": POLYGON_COORDINATES}, crs=CRS.WGS84)

# Výstupné parametre
OUTPUT_SIZE = [500, 500]  # Znížená veľkosť pre rýchlejšie testovanie
OUTPUT_FORMAT = MimeType.TIFF

# Evalscript pre výpočet NDVI
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


# --- 2. FUNKCIE PRE ANALÝZU ---

def get_ndvi_for_year(year, target_month_start, target_month_end, config, geometry, size):
    """Stiahne NDVI dáta pre zadaný rok a mesiac."""
    print(f"Sťahujem dáta pre rok {year} (obdobie {target_month_start} až {target_month_end})...")
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
            print(f"Varovanie: Pre rok {year} neboli vrátené žiadne dáta.")
            return None
        ndvi_array = data[0]
        # Nahradíme nuly (zvyčajne no-data) za NaN, aby neovplyvnili výpočty
        ndvi_array[ndvi_array == 0] = np.nan
        print(
            f"DEBUG [{year}]: Tvar dát: {ndvi_array.shape}, Min: {np.nanmin(ndvi_array):.4f}, Max: {np.nanmax(ndvi_array):.4f}, Priemer: {np.nanmean(ndvi_array):.4f}")
        return ndvi_array
    except Exception as e:
        print(f"Chyba pri sťahovaní dát za rok {year}: {e}")
        return None


def generate_trend_map(years_to_analyze, target_month_start, target_month_end):
    """
    Hlavná funkcia, ktorá orchesteruje celý proces analýzy a vracia cestu k vygenerovanému obrázku.
    """
    print(
        f"--- Spúšťam dlhodobú analýzu NDVI trendu pre roky {years_to_analyze} a obdobie {target_month_start}-{target_month_end} ---")

    if not sh_config.sh_client_id:
        raise Exception("Chyba konfigurácie: Sentinel Hub Client ID nie je nastavené.")

    yearly_ndvi_data = [
        get_ndvi_for_year(year, target_month_start, target_month_end, sh_config, AOI_GEOMETRY, OUTPUT_SIZE) for year in
        years_to_analyze]

    # Odfiltrujeme roky, pre ktoré sa nepodarilo stiahnuť dáta
    valid_years_data = [(year, data) for year, data in zip(years_to_analyze, yearly_ndvi_data) if
                        data is not None and not np.isnan(data).all()]

    if len(valid_years_data) < 2:
        print("Chyba: Pre analýzu trendu sú potrebné dáta aspoň z dvoch platných rokov. Končím.")
        return None

    # Rozbalíme validné dáta
    valid_years, yearly_ndvi_data = zip(*valid_years_data)

    # Spojenie dát do jedného 3D numpy poľa (roky, výška, šírka)
    y = np.stack(yearly_ndvi_data, axis=0)
    print(f"DEBUG: Tvar spojeného poľa (y): {y.shape}")

    print("Vypočítavam trend pre každý pixel...")
    n_years = y.shape[0]
    x = np.arange(n_years)
    x_reshaped = x.reshape(n_years, 1, 1)

    # Použijeme nanmean, aby sme ignorovali pixely bez dát
    mean_x = np.mean(x)
    mean_y = np.nanmean(y, axis=0)

    # Vypočítame čitateľa a menovateľa, pričom ignorujeme NaN hodnoty
    numerator = np.nansum((x_reshaped - mean_x) * (y - mean_y), axis=0)
    denominator = np.sum((x - mean_x) ** 2)

    trend_map = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator != 0)

    # Maskovanie oblastí, kde neboli žiadne platné dáta
    trend_map[np.isnan(mean_y)] = np.nan

    print("Výpočet trendu dokončený.")
    print(
        f"DEBUG: Štatistiky mapy trendov - Min: {np.nanmin(trend_map):.4f}, Max: {np.nanmax(trend_map):.4f}, Priemer: {np.nanmean(trend_map):.4f}")

    print("Vytváram a ukladám mapu trendu...")
    with plt.style.context('default'):
        cmap_trend = LinearSegmentedColormap.from_list("trend_map", [(0, "red"), (0.5, "white"), (1, "green")])
        plt.figure(figsize=(12, 10))

        # Ignorujeme NaN pri výpočte percentilu
        vlim = np.nanpercentile(np.abs(trend_map), 98)
        if vlim == 0: vlim = 1.0

        img = plt.imshow(trend_map, cmap=cmap_trend, vmin=-vlim, vmax=vlim)
        plt.colorbar(img, label="Sklon trendu NDVI (zmena za rok)")
        plt.title(f"Trend vývoja vegetácie v Trnave ({valid_years[0]}-{valid_years[-1]})")
        plt.xlabel("Pixel X")
        plt.ylabel("Pixel Y")

        # Uloženie do statickej zložky
        output_dir = "static/output"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"ndvi_trend_trnava_{valid_years[0]}_{valid_years[-1]}_{target_month_start}_{target_month_end}.png"
        output_filepath = os.path.join(output_dir, filename)

        plt.savefig(output_filepath, dpi=150)  # Znížené DPI pre rýchlejšie generovanie
        plt.close()  # Uvoľnenie pamäte

    print(f"✅ Mapa trendu úspešne uložená ako: {output_filepath}")
    return output_filepath


# --- 3. HLAVNÝ PROCES SPRACOVANIA (pre priame spustenie) ---

if __name__ == "__main__":
    """Príklad spustenia pre testovacie účely."""
    print("--- Spúšťam testovaciu analýzu pre priame spustenie skriptu ---")

    # Parametre pre test
    test_years = [2022, 2023, 2024]
    test_month_start = "06-01"
    test_month_end = "08-31"

    try:
        image_path = generate_trend_map(test_years, test_month_start, test_month_end)
        if image_path:
            print(f"\nTest úspešný. Výsledný obrázok je v: {image_path}")
        else:
            print("\nTest neúspešný. Nevytvoril sa žiadny obrázok.")
    except Exception as e:
        print(f"Počas testu nastala chyba: {e}")
