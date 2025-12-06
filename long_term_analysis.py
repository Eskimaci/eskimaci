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
import json
import random
import os
from PIL import Image
import csv

class park:
    def __init__(self, nazov, suradnice):
        self.nazov = nazov
        self.suradnice = suradnice

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
YEARS_TO_ANALYZE = [2020, 2021, 2022, 2023, 2024, 2025]

# Definovanie 2-týždňových období (február až júl)
# Formát: (mesiac_začiatok, deň_začiatok, mesiac_koniec, deň_koniec, názov)
BI_WEEKLY_PERIODS = [
    (2, 1, 2, 14, 'Feb 1-14'),
    (2, 15, 2, 28, 'Feb 15-28'),
    (3, 1, 3, 14, 'Mar 1-14'),
    (3, 15, 3, 31, 'Mar 15-31'),
    (4, 1, 4, 14, 'Apr 1-14'),
    (4, 15, 4, 30, 'Apr 15-30'),
    (5, 1, 5, 14, 'May 1-14'),
    (5, 15, 5, 31, 'May 15-31'),
    (6, 1, 6, 14, 'Jun 1-14'),
    (6, 15, 6, 30, 'Jun 15-30'),
    (7, 1, 7, 14, 'Jul 1-14'),
    (7, 15, 7, 31, 'Jul 15-31'),
]

# Definovanie oblasti záujmu (AOI) - Trnava
POLYGON_COORDINATES = [
    [[17.5724, 48.3860], [17.5471, 48.3819], [17.5475, 48.3700], [17.5702, 48.3484],
     [17.6294, 48.3375], [17.6504, 48.3605], [17.6093, 48.3768], [17.6143, 48.3912],
     [17.5836, 48.4043], [17.5609, 48.3925], [17.5678, 48.3882], [17.5724, 48.3860]]
]
AOI_GEOMETRY = Geometry(geometry={"type": "Polygon", "coordinates": POLYGON_COORDINATES}, crs=CRS.WGS84)

with open('static/geojson/parkJankaKrala.geojson', 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    parkJankaKrala = park("Park Janka Kráľa", geojsonData['features'][0]['geometry']['coordinates'][0])


with open('static/geojson/bernolakovPark.geojson', 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    bernolakovPark = park("Bernolákov Park", geojsonData['features'][0]['geometry']['coordinates'][0])

with open('static/geojson/ruzovyPark.geojson', 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    ruzovyPark = park("Ružový Park", geojsonData['features'][0]['geometry']['coordinates'][0])

with open('static/geojson/strky.geojson' , 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    strky = park("Park Strky", geojsonData['features'][0]['geometry']['coordinates'][0])

with open('static/geojson/kamenac.geojson' , 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    kamenac = park("Park Kamenný mlyn", geojsonData['features'][0]['geometry']['coordinates'][0])

with open('static/geojson/parkZaDruzbou.geojson' , 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    parkZaDruzbou = park("Park Za družbou", geojsonData['features'][0]['geometry']['coordinates'][0])

with open('static/geojson/zahradkarskaOblast.geojson' , 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    zahradkarskaOblast = park("Záhradkárska Oblasť", geojsonData['features'][0]['geometry']['coordinates'][0])

with open('static/geojson/nemocnicnyPark.geojson' , 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    nemocnicnyPark = park("Nemocnicny Park", geojsonData['features'][0]['geometry']['coordinates'][0])

with open('static/geojson/rybniky.geojson' , 'r') as geojsonFile:
    geojsonData = json.load(geojsonFile)
    rybniky = park("Rybníky", geojsonData['features'][0]['geometry']['coordinates'][0])

zelenePlochy = [parkJankaKrala, bernolakovPark, ruzovyPark, strky, kamenac, parkZaDruzbou, zahradkarskaOblast, nemocnicnyPark]

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

# Evalscript pre true color RGB obrázok
EVALSCRIPT_TRUE_COLOR = """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B02", "B03", "B04"] }],
    output: { bands: 3, sampleType: "AUTO" }
  };
}
function evaluatePixel(sample) {
  return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
}
"""

# --- 2. FUNKCIE PRE ANALÝZU ---

def save_satellite_image(year, start_month, start_day, end_month, end_day, period_name, config, geometry, size, park_name):
    """Stiahne a uloží RGB satelitný snímok s viditeľnými oblakmi."""
    print(f"Sťahujem RGB snímok pre {year} {period_name}...")
    
    # Upravíme konečný deň pre priestupné roky
    if end_month == 2 and end_day == 28:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            end_day = 29
    
    time_interval = (f'{year}-{start_month:02d}-{start_day:02d}', f'{year}-{end_month:02d}-{end_day:02d}')
    
    request = SentinelHubRequest(
        evalscript=EVALSCRIPT_TRUE_COLOR,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.PNG)
        ],
        geometry=geometry,
        size=size,
        config=config
    )
    
    try:
        data = request.get_data(save_data=False)
        if not data:
            print(f"Varovanie: Pre {year} {period_name} neboli vrátené žiadne RGB dáta.")
            return False
        
        # Vytvoríme výstupný adresár ak neexistuje
        output_dir = 'static/output/satelite'
        os.makedirs(output_dir, exist_ok=True)
        
        # Uložíme obrázok
        rgb_image = data[0]
        safe_park_name = park_name.replace(' ', '_').replace('á', 'a').replace('ô', 'o').replace('ý', 'y').replace('ž', 'z')
        safe_period_name = period_name.replace(' ', '_').replace('-', '_')
        filename = f"{output_dir}/{safe_park_name}_{year}_{safe_period_name}.png"
        
        # Konvertujeme numpy array na PIL Image a uložíme
        img = Image.fromarray(rgb_image)
        img.save(filename)
        
        print(f"✅ RGB snímok uložený: {filename}")
        return True
    except Exception as e:
        print(f"Chyba pri sťahovaní RGB snímku za {year} {period_name}: {e}")
        return False

def get_ndvi_for_period(year, start_month, start_day, end_month, end_day, period_name, config, geometry, size):
    """Stiahne NDVI dáta pre zadané 2-týždňové obdobie."""
    print(f"Sťahujem dáta pre {year} {period_name}...")
    
    # Upravíme konečný deň pre priestupné roky
    if end_month == 2 and end_day == 28:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            end_day = 29
    
    time_interval = (f'{year}-{start_month:02d}-{start_day:02d}', f'{year}-{end_month:02d}-{end_day:02d}')
    
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
            print(f"Varovanie: Pre {year} {period_name} neboli vrátené žiadne dáta.")
            return None
        ndvi_array = data[0]
        # Vypočítame priemernú hodnotu NDVI pre celú oblasť
        # filter out hodnoty >0,35
        filtered_values = ndvi_array[(ndvi_array != 0) & (ndvi_array >= 0.4)]
        
        if len(filtered_values) == 0:
            print(f"Varovanie: Pre {year} {period_name} neboli nájdené žiadne hodnoty >= 0.4")
            print(f"  Rozsah hodnôt v poli: {np.min(ndvi_array):.4f} až {np.max(ndvi_array):.4f}")
            print(f"  Počet nenulových hodnôt: {np.count_nonzero(ndvi_array)}")
            # Použijeme všetky nenulové hodnoty
            filtered_values = ndvi_array[ndvi_array != 0]
            if len(filtered_values) == 0:
                return None
        
        mean_ndvi = np.mean(filtered_values)
        print(f"DEBUG [{year} {period_name}]: Priemerná NDVI: {mean_ndvi:.4f} (z {len(filtered_values)} pixelov)")
        return mean_ndvi
    except Exception as e:
        print(f"Chyba pri sťahovaní dát za {year} {period_name}: {e}")
        return None

# --- 3. HLAVNÝ PROCES SPRACOVANIA ---

def main():
    """Hlavná funkcia, ktorá orchesteruje celý proces analýzy."""
    print("--- Spúšťam dlhodobú analýzu priemernej NDVI ---")
    
    # Vytvorenie grafu
    print("\n--- Vytváram graf priemernej NDVI ---")
    plt.figure(figsize=(14, 8))
    
    all_values = []  # Pre výpočet správnych limitov grafu
    
    # Vyberieme prvý park pre porovnanie rokov
    selected_park = zelenePlochy[0]  # Defaultne prvý park, môžete zmeniť index
    
    aoi_geometry = Geometry(
        geometry={"type": "Polygon", "coordinates": [selected_park.suradnice]},
        crs=CRS.WGS84
    )
    
    print(f"\n--- Analyzujem park: {selected_park.nazov} ---")
    print(f"--- Porovnávam jednotlivé roky (2-týždňové obdobia) ---")
    
    # Slovník na uloženie dát pre každý rok: {rok: [hodnoty pre každé 2-týždňové obdobie]}
    yearly_data = {}
    
    # Stiahnutie dát pre každý rok
    for year in YEARS_TO_ANALYZE:
        print(f"\n--- Rok {year} ---")
        yearly_data[year] = []
        
        for start_month, start_day, end_month, end_day, period_name in BI_WEEKLY_PERIODS:
            # Stiahnutie NDVI dát
            mean_ndvi = get_ndvi_for_period(year, start_month, start_day, end_month, end_day, period_name, 
                                           sh_config, aoi_geometry, OUTPUT_SIZE)
            yearly_data[year].append(mean_ndvi)
            if mean_ndvi is not None:
                all_values.append(mean_ndvi)
            
            # Stiahnutie a uloženie RGB satelitného snímku
            save_satellite_image(year, start_month, start_day, end_month, end_day, period_name,
                               sh_config, aoi_geometry, OUTPUT_SIZE, selected_park.nazov)
    
    # Vytvorenie kriviek pre každý rok
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    period_labels = [period[4] for period in BI_WEEKLY_PERIODS]
    
    for i, year in enumerate(YEARS_TO_ANALYZE):
        # Pripravíme hodnoty pre daný rok
        values = yearly_data[year]
        
        # Vyberieme farbu
        color = colors[i % len(colors)]
        
        # Vytvoríme spojnicový graf pre daný rok
        plt.plot(period_labels, values, color=color, linewidth=2.5, marker='o', 
                markersize=6, markerfacecolor=color, markeredgecolor='white', 
                markeredgewidth=1.5, label=f'Rok {year}')
        
        print(f"\nRok {year}:")
        for j, (start_month, start_day, end_month, end_day, period_name) in enumerate(BI_WEEKLY_PERIODS):
            if yearly_data[year][j] is not None:
                print(f"  {period_name}: {yearly_data[year][j]:.4f}")
            else:
                print(f"  {period_name}: Žiadne dáta")
    
    # Nastavíme limity grafu
    if all_values:
        y_min = min(all_values) * 0.95
        y_max = max(all_values) * 1.05
        plt.ylim(y_min, y_max)
    
    plt.xlabel('2-týždňové obdobie', fontsize=12, fontweight='bold')
    plt.ylabel('Priemerná NDVI', fontsize=12, fontweight='bold')
    plt.title(f'Porovnanie NDVI naprieč rokmi (2-týždňové obdobia) - {selected_park.nazov}', 
            fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='best', fontsize=10)
    plt.tight_layout()
        
    # Uloženie grafu
    output_filename = f"ndvi_yearly_comparison_{YEARS_TO_ANALYZE[0]}_{YEARS_TO_ANALYZE[-1]}_{selected_park.nazov.replace(' ', '_')}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\n✅ Graf úspešne uložený ako: {output_filename}")
    
    # Uloženie dát do CSV súboru
    csv_filename = f"ndvi_yearly_comparison_{YEARS_TO_ANALYZE[0]}_{YEARS_TO_ANALYZE[-1]}_{selected_park.nazov.replace(' ', '_')}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Hlavička - prvý stĺpec je "Obdobie", potom roky
        header = ['Obdobie'] + [f'Rok {year}' for year in YEARS_TO_ANALYZE]
        csv_writer.writerow(header)
        
        # Dáta - každý riadok je jedno 2-týždňové obdobie
        for j, (start_month, start_day, end_month, end_day, period_name) in enumerate(BI_WEEKLY_PERIODS):
            row = [period_name]
            for year in YEARS_TO_ANALYZE:
                value = yearly_data[year][j]
                # Ak je hodnota None, zapíšeme prázdny reťazec
                row.append(f"{value:.4f}" if value is not None else "")
            csv_writer.writerow(row)
    
    print(f"✅ CSV súbor úspešne uložený ako: {csv_filename}")

if __name__ == "__main__":
    main()