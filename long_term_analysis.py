# -*- coding: utf-8 -*-
"""
Skript pre dlhodobú analýzu vegetačného indexu (NDVI) z dát Sentinel-2.

Tento skript vykonáva nasledujúce kroky:
1. Pripojí sa k Sentinel Hub API.
2. Pre definovanú oblasť (Trnava) a časové obdobie (2020-2025, mesiace február-júl) 
   stiahne dáta NDVI.
3. Vypočíta priemernú hodnotu NDVI pre každý mesiac naprieč všetkými rokmi.
4. Vytvorí a uloží graf zobrazujúci priemernú hodnotu NDVI pre jednotlivé mesiace.
"""

from matplotlib import colors
import numpy as np
from decouple import config
import matplotlib.pyplot as plt
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
MONTHS_TO_ANALYZE = [2, 3, 4, 5, 6, 7]  # Február až Júl
MONTH_NAMES = ['Február', 'Marec', 'Apríl', 'Máj', 'Jún', 'Júl']

# Definovanie oblasti záujmu (AOI) - park Janka Kráľa v Trnave
POLYGON_COORDINATES = [
    [17.56817676145432, 48.36381310513961],
    [17.56981977533604, 48.36359325939384],
    [17.57174067288043, 48.36399500611071],
    [17.57313437147868, 48.36471674075158],
    [17.57267368229819, 48.36520459481028],
    [17.57290262998025, 48.36555138873172],
    [17.5810650959477, 48.36958824198187],
    [17.58138863017993, 48.36935271412575],
    [17.58186315196065, 48.36958889475593],
    [17.58223565532713, 48.3695203311474],
    [17.58275839314176, 48.36977717283936],
    [17.58309114863392, 48.37065902992905],
    [17.58280761897207, 48.37081050876479],
    [17.58292551563057, 48.37106539370707],
    [17.58277629388541, 48.37119493710695],
    [17.56817676145432, 48.36381310513961]
]
zelenePlochy = []

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

zelenePlochy = [parkJankaKrala, bernolakovPark, ruzovyPark, strky, kamenac, parkZaDruzbou, zahradkarskaOblast]
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

def get_ndvi_for_period(year, month, config, geometry, size):
    """Stiahne NDVI dáta pre zadaný rok a mesiac."""
    print(f"Sťahujem dáta pre {year}-{month:02d}...")
    
    # Určíme prvý a posledný deň mesiaca
    if month == 2:
        # Február - kontrola na priestupný rok
        last_day = 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
    elif month in [4, 6]:
        last_day = 30
    else:
        last_day = 31
    
    time_interval = (f'{year}-{month:02d}-01', f'{year}-{month:02d}-{last_day}')
    
    request = SentinelHubRequest(
            evalscript=EVALSCRIPT_NDVI,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=time_interval,
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                )
            ],
            responses=[
                SentinelHubRequest.output_response('default', OUTPUT_FORMAT)
            ],
            geometry=geometry,
            size=size,
            config=config
        )
    try:
        data = request.get_data(save_data=False)
        if not data:
            print(f"Varovanie: Pre {year}-{month:02d} neboli vrátené žiadne dáta.")
            return None
        ndvi_array = data[0]
        # Vypočítame priemernú hodnotu NDVI pre celú oblasť
        # filter out hodnoty >0,35
        filtered_values = ndvi_array[(ndvi_array != 0) & (ndvi_array >= 0.4)]
        
        if len(filtered_values) == 0:
            print(f"Varovanie: Pre {year}-{month:02d} neboli nájdené žiadne hodnoty >= 0.4")
            print(f"  Rozsah hodnôt v poli: {np.min(ndvi_array):.4f} až {np.max(ndvi_array):.4f}")
            print(f"  Počet nenulových hodnôt: {np.count_nonzero(ndvi_array)}")
            # Použijeme všetky nenulové hodnoty
            filtered_values = ndvi_array[ndvi_array != 0]
            if len(filtered_values) == 0:
                return None
        
        mean_ndvi = np.mean(filtered_values)
        print(f"DEBUG [{year}-{month:02d}]: Priemerná NDVI: {mean_ndvi:.4f} (z {len(filtered_values)} pixelov)")
        return mean_ndvi
    except Exception as e:
        print(f"Chyba pri sťahovaní dát za {year}-{month:02d}: {e}")
        return None

# --- 3. HLAVNÝ PROCES SPRACOVANIA ---

def main():
    """Hlavná funkcia, ktorá orchesteruje celý proces analýzy."""
    print("--- Spúšťam dlhodobú analýzu priemernej NDVI ---")
            # Vytvorenie grafu
    print("\n--- Vytváram graf priemernej NDVI ---")
    plt.figure(figsize=(12, 6))
    # Slovník na uloženie dát: {mesiac: [hodnoty pre všetky roky]}

    for park in zelenePlochy:
        aoi_geometry = Geometry(
            geometry={"type": "Polygon", "coordinates": [park.suradnice]},
            crs=CRS.WGS84
        )
        print(f"\n--- Analyzujem park: {park.nazov} ---")
        monthly_averages = {month: [] for month in MONTHS_TO_ANALYZE}
        
        # Stiahnutie dát pre každý rok a mesiac
        for year in YEARS_TO_ANALYZE:
            for month in MONTHS_TO_ANALYZE:
                mean_ndvi = get_ndvi_for_period(year, month, sh_config, aoi_geometry, OUTPUT_SIZE)
                if mean_ndvi is not None:
                    monthly_averages[month].append(mean_ndvi)
        
        # Výpočet priemernej hodnoty NDVI pre každý mesiac naprieč všetkými rokmi
        print("\n--- Výpočet priemerných hodnôt NDVI pre jednotlivé mesiace ---")
        monthly_means = {}
        for month in MONTHS_TO_ANALYZE:
            if monthly_averages[month]:
                monthly_means[month] = np.mean(monthly_averages[month])
                print(f"{MONTH_NAMES[MONTHS_TO_ANALYZE.index(month)]}: {monthly_means[month]:.4f} (z {len(monthly_averages[month])} meraní)")
            else:
                print(f"{MONTH_NAMES[MONTHS_TO_ANALYZE.index(month)]}: Žiadne dostupné dáta")
                monthly_means[month] = None
        

        
        # Pripravíme dáta pre graf
        months = list(monthly_means.keys())
        values = [monthly_means[m] if monthly_means[m] is not None else 0 for m in months]
        month_labels = MONTH_NAMES
        
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        random_color = random.choice(colors)
        # Vytvoríme spojnicový graf (curve)
        plt.plot(month_labels, values, color=random_color, linewidth=2.5, marker='o', 
                markersize=8, markerfacecolor=random_color, markeredgecolor='white', 
                markeredgewidth=2, label=f'{park.nazov}')
        
        # Pridáme hodnoty pri každom bode
        for i, value in enumerate(values):
            if monthly_means[months[i]] is not None:
                plt.text(i, value + 0.01, f'{value:.3f}', 
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.xlabel('Mesiac', fontsize=12, fontweight='bold')
        plt.ylabel('Priemerná NDVI', fontsize=12, fontweight='bold')
        plt.title(f'Priemerná NDVI pre mesiace február-júl ({YEARS_TO_ANALYZE[0]}-{YEARS_TO_ANALYZE[-1]})', 
                fontsize=14, fontweight='bold')
        plt.ylim(0, max(values) * 1.15 if values else 1)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend()
        plt.tight_layout()
        
    # Uloženie grafu
    output_filename = f"ndvi_monthly_average_{YEARS_TO_ANALYZE[0]}_{YEARS_TO_ANALYZE[-1]}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"✅ Graf úspešne uložený ako: {output_filename}")

    # Zobrazenie grafu
    plt.show()

if __name__ == "__main__":
    main()