# Technická dokumentácia projektu

Tento dokument poskytuje podrobný technický prehľad jednotlivých skriptov a komponentov v projekte.

## Štruktúra projektu

Projekt sa skladá z nasledujúcich častí:

-   **Backend**: Aplikácia postavená na frameworku Flask (`manage.py`), ktorá slúži ako API pre frontend.
-   **Frontend**: Jednostránková webová aplikácia (SPA) napísaná v čistom JavaScripte, HTML a CSS (`static/` a `templates/`).
-   **Dátové skripty**: Súbor Python skriptov v adresári `source/` určených na manuálne získavanie, spracovanie a analýzu dát z externých zdrojov (Sentinel Hub, Open-Meteo).
-   **Statické súbory**: Adresár `static/` obsahuje CSS štýly, JavaScript kód, GeoJSON súbory, CSV dáta a vygenerované obrázkové výstupy.

---

## `manage.py`

Hlavný server aplikácie postavený na `Flask`. Zabezpečuje servírovanie frontendovej aplikácie (`index.html`) a poskytuje API endpointy pre spracovanie požiadaviek z frontendu. Spúšťa sa príkazom `python3 manage.py`.

### Knižnice
- `flask`: Webový framework.
- `pandas`: Spracovanie a analýza dát z CSV súborov.
- `plotly`: Príprava dátových štruktúr pre interaktívne grafy.
- `source.long_term_analysis_trnava`: Import funkcie `generate_trend_map` pre on-the-fly analýzu.

### Konfigurácia
- `POLLEN_TO_MONTHS`: Slovník, ktorý mapuje názvy sezón (`early_spring`, `mid_spring`, atď.) na konkrétne rozsahy mesiacov a dní pre API endpoint `/api/analyze`.

### API Endpoints

#### `GET /`
- **Popis**: Servíruje hlavnú stránku `index.html`.
- **Návratová hodnota**: HTML stránka.

#### `POST /api/plot`
- **Popis**: Prijíma požiadavku s názvom lokality, načíta pred-spracované dáta a vracia ich vo formáte pre knižnicu Plotly.js.
- **Vstupné JSON dáta**:
    - `location` (string): Kľúč lokality (napr. `janka-krala`, `nemocnicny`).
- **Zdroj dát**:
    - NDVI dáta: `static/csv_interpol_lin/<location>.csv`
    - Teplotné dáta: `static/temperature_comparison.csv`
- **Návratová hodnota (JSON)**:
    - `ndvi_data`: JSON string s dátami pre NDVI graf.
    - `temp_data`: JSON string s dátami pre teplotný graf.
    - `threshold_dates`: JSON string s dátami o dňoch, kedy teplota prekročila 5°C po dobu 5 dní.

#### `POST /api/analyze`
- **Popis**: Spúšťa živú, dlhodobú analýzu trendu vegetácie na základe zvolených rokov a sezóny. Volá funkciu `generate_trend_map` zo skriptu `long_term_analysis_trnava.py`.
- **Vstupné JSON dáta**:
    - `years` (list): Zoznam rokov na analýzu (napr. `[2022, 2023, 2024]`).
    - `season` (string): Názov sezóny (napr. `late_spring`).
- **Návratová hodnota (JSON)**:
    - `image_url`: URL cesta k vygenerovanému obrázku s mapou trendu (napr. `/static/output/trend_map_2022-2024_late_spring.png`).

#### `GET /api/current_pollen`
- **Popis**: Načíta dáta o priemerných peľových zaťaženiach zo súboru `static/pollenAverageLoads.csv`.
- **Návratová hodnota (JSON)**:
    - `pollen_data`: Dáta pripravené na vykreslenie v grafe.

---

## `static/js/main.js`

Frontendová logika aplikácie. Zodpovedá za dynamické načítavanie obsahu, interakciu s používateľom, komunikáciu s backend API a vykresľovanie grafov pomocou knižnice Plotly.js.

### Hlavné funkcie

- **`loadVegetaciu(contentDiv)`**: Pripraví UI pre analýzu trendu vegetácie (výber rokov, sezóny).
- **`loadPollenSeason(contentDiv)`**: Pripraví UI pre analýzu nástupu peľovej sezóny (výber lokality).
- **`loadCurrentPollen(contentDiv)`**: Načíta a zobrazí graf s aktuálnou peľovou situáciou.
- **`handleAnalysis()`**: Zozbiera vstupy, odošle požiadavku na `/api/analyze` a po prijatí URL zobrazí výslednú mapu.
- **`handlePollenAnalysis()`**: Zozbiera vstupy, odošle požiadavku na `/api/plot` a pomocou funkcie `renderPlots` vykreslí grafy.
- **`renderPlots(...)`**: Vykreslí interaktívne grafy NDVI a teploty pomocou Plotly.
- **`renderPollenPlots(...)`**: Vykreslí graf aktuálnej peľovej situácie.

---

## Dátové skripty (`source/`)

Tieto skripty sa nespúšťajú ako súčasť webovej aplikácie. Sú to **nástroje na manuálnu prípravu dát**, ktoré aplikácia následne využíva.

### `long_term_analysis_trnava.py`
Skript je priamo využívaný endpointom `/api/analyze` na živú analýzu trendu NDVI v čase pre celú Trnavu.

- **Knižnice**: `sentinelhub`, `numpy`, `matplotlib`, `decouple`.
- **Konfigurácia**: Vyžaduje `.env` súbor s `CLIENT_ID` a `CLIENT_SECRET` pre prístup k Sentinel Hub API.
- **Funkcia**:
    - **`generate_trend_map(years_to_analyze, month_start, month_end)`**: Pre zadané roky stiahne dáta, vypočíta lineárnu regresiu pre každý pixel a vygeneruje mapu trendu. Mapa sa uloží do `static/output/`.

### Príprava dát pre grafy (manuálny proces)

Dáta pre grafy porovnávajúce NDVI a teplotu sa negenerujú naživo, ale prechádzajú manuálnym, niekoľkokrokovým procesom.

#### 1. krok: `long_term_analysis.py`
Tento skript sťahuje **surové dáta** pre konkrétne parky.
- **Popis**: Pre každý definovaný park a pre každý rok sťahuje priemerné NDVI dáta v 2-týždňových intervaloch zo Sentinel Hub.
- **Výstup**: `static/csv_raw_linear/ndvi_yearly_comparison_*.csv`. Tieto súbory obsahujú surové dáta s možnými medzerami (kvôli oblačnosti).

#### 2. krok: `interpolacia.py`
Tento skript **čistí a dopĺňa dáta**.
- **Popis**: Načíta surové NDVI dáta z `static/csv_raw_linear/`, odfiltruje nízke hodnoty (< 0.4) a pomocou lineárnej interpolácie doplní chýbajúce dáta.
- **Vstup**: `static/csv_raw_linear/ndvi_yearly_comparison_*.csv`
- **Výstup**: `static/csv_interpol_lin/<nazov-parku>.csv`. Tieto "vyčistené" dáta používa endpoint `/api/plot`.

#### 3. krok: `getMeteoData.py`
Tento skript sťahuje **historické dáta o teplote**.
- **Popis**: Pomocou Open-Meteo API sťahuje denné priemerné teploty. Následne dáta spracuje a uloží.
- **Výstup**: `static/temperature_comparison.csv`, ktorý používa endpoint `/api/plot`.

### Ostatné skripty

#### `createGeojson.py`
- **Popis**: Interaktívny nástroj na príkazovom riadku, ktorý z vložených súradníc vytvorí `*.geojson` súbor. Používa sa na definovanie hraníc parkov v `static/geojson/`.
- **Použitie**: `python source/createGeojson.py <nazovSuboru> [--longlat|--latlong]`

#### `traspose.py`
- **Popis**: Jednoduchý nástroj na transpozíciu (otočenie riadkov za stĺpce) CSV súboru. Pravdepodobne bol použitý na jednorazovú úpravu dát, napr. `static/pollenAverageLoads.csv`.
