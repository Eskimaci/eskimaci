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

import numpy as np
from decouple import config
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
    print(f"Chyba: Nepodarilo sa načítať CLIENT_ID alebo CLIENT_SECRET z .env súboru. Uistite sa, že súbor existuje a premenné sú nastavené. Detaily: {e}")
    exit()

# Konfigurácia Sentinel Hub API
sh_config = SHConfig()
sh_config.sh_client_id = CLIENT_ID
sh_config.sh_client_secret = CLIENT_SECRET

# Definovanie časového rozsahu analýzy
YEARS_TO_ANALYZE = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
TARGET_MONTH_START = "08-01"
TARGET_MONTH_END = "08-31"

# Definovanie oblasti záujmu (AOI) - Trnava
POLYGON_COORDINATES = [
    [[17.5724, 48.3860], [17.5471, 48.3819], [17.5475, 48.3700], [17.5702, 48.3484],
     [17.6294, 48.3375], [17.6504, 48.3605], [17.6093, 48.3768], [17.6143, 48.3912],
     [17.5836, 48.4043], [17.5609, 48.3925], [17.5678, 48.3882], [17.5724, 48.3860]]
]
AOI_GEOMETRY = Geometry(geometry={"type": "Polygon", "coordinates": POLYGON_COORDINATES}, crs=CRS.WGS84)

# Výstupné parametre
OUTPUT_SIZE = [1000, 1000]
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
  if (sample.dataMask === 0) { return [0]; }
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
"""

# --- 2. FUNKCIE PRE ANALÝZU ---

def get_ndvi_for_year(year, config, geometry, size):
    """Stiahne NDVI dáta pre zadaný rok."""
    print(f"Sťahujem dáta pre rok {year}...")
    time_interval = (f'{year}-{TARGET_MONTH_START}', f'{year}-{TARGET_MONTH_END}')
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
        print(f"DEBUG [{year}]: Tvar dát: {ndvi_array.shape}, Min: {np.min(ndvi_array):.4f}, Max: {np.max(ndvi_array):.4f}, Priemer: {np.mean(ndvi_array):.4f}")
        if np.all(ndvi_array == 0):
            print(f"DEBUG [{year}]: Varovanie - všetky hodnoty v poli sú nulové.")
        return ndvi_array
    except Exception as e:
        print(f"Chyba pri sťahovaní dát za rok {year}: {e}")
        return None

# --- 3. HLAVNÝ PROCES SPRACOVANIA ---

def main():
    """Hlavná funkcia, ktorá orchesteruje celý proces analýzy."""
    print("--- Spúšťam dlhodobú analýzu NDVI trendu ---")
    
    yearly_ndvi_data = [get_ndvi_for_year(year, sh_config, AOI_GEOMETRY, OUTPUT_SIZE) for year in YEARS_TO_ANALYZE]
    yearly_ndvi_data = [data for data in yearly_ndvi_data if data is not None]
    
    if len(yearly_ndvi_data) < 2:
        print("Chyba: Pre analýzu trendu sú potrebné dáta aspoň z dvoch rokov. Končím.")
        return

    # Spojenie dát do jedného 3D numpy poľa (roky, výška, šírka)
    y = np.stack(yearly_ndvi_data, axis=0)
    print(f"DEBUG: Tvar spojeného poľa (y): {y.shape}")

    # 2. Výpočet trendu pre každý pixel (Vektorizovaná metóda)
    print("Vypočítavam trend pre každý pixel (vektorizovaná metóda)...")

    # Vytvoríme x-ovú os (čas)
    n_years = y.shape[0]
    x = np.arange(n_years)
    
    # Prepneme osi, aby sme mohli ľahko broadcastovať
    # Tvar x: (N, 1, 1) -> bude sa opakovať pre každý pixel
    # Tvar y: (N, H, W)
    x_reshaped = x.reshape(n_years, 1, 1)

    # Vypočítame priemery potrebné pre vzorec sklonu
    mean_x = np.mean(x)
    mean_y = np.mean(y, axis=0) # Priemer pre každý pixel cez všetky roky

    # Vypočítame čitateľa a menovateľa vzorca pre sklon
    # Vzorec: slope = Σ((x - mean_x)(y - mean_y)) / Σ((x - mean_x)^2)
    numerator = np.sum((x_reshaped - mean_x) * (y - mean_y), axis=0)
    denominator = np.sum((x - mean_x)**2)
    
    # Vypočítame finálnu mapu trendov
    # Zabezpečíme sa proti deleniu nulou, ak by bol denominator 0
    trend_map = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator!=0)

    print("Výpočet trendu dokončený.")
    print(f"DEBUG: Tvar mapy trendov: {trend_map.shape}")
    print(f"DEBUG: Štatistiky mapy trendov - Min: {np.min(trend_map):.4f}, Max: {np.max(trend_map):.4f}, Priemer: {np.mean(trend_map):.4f}")

    # 3. Vizualizácia a uloženie mapy trendu
    print("Vytváram a ukladám mapu trendu...")
    cmap_trend = LinearSegmentedColormap.from_list("trend_map", [(0, "red"), (0.5, "white"), (1, "green")])
    plt.figure(figsize=(12, 10))
    
    # Normalizácia hodnôt sklonu pre lepšiu vizualizáciu
    vlim = np.percentile(np.abs(trend_map), 98)
    print(f"DEBUG: Vypočítaná hodnota vlim (98 percentil): {vlim:.4f}")

    if vlim == 0:
        print("DEBUG: vlim je 0, čo znamená, že mapa trendov je pravdepodobne prázdna. Nastavujem vlim na 1, aby sa predišlo chybe.")
        vlim = 1.0
    
    img = plt.imshow(trend_map, cmap=cmap_trend, vmin=-vlim, vmax=vlim)
    plt.colorbar(img, label="Sklon trendu NDVI (zmena za rok)")
    plt.title(f"Trend vývoja vegetácie v Trnave ({YEARS_TO_ANALYZE[0]}-{YEARS_TO_ANALYZE[-1]})")
    plt.xlabel("Pixel X")
    plt.ylabel("Pixel Y")
    
    output_filename = f"ndvi_trend_trnava_{YEARS_TO_ANALYZE[0]}_{YEARS_TO_ANALYZE[-1]}.png"
    plt.savefig(output_filename, dpi=300)
    print(f"✅ Mapa trendu úspešne uložená ako: {output_filename}")

if __name__ == "__main__":
    main()