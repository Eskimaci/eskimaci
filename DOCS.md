# Technická dokumentácia projektu

Tento dokument poskytuje podrobný technický prehľad jednotlivých skriptov a komponentov v projekte.

## Štruktúra projektu

Projekt sa skladá z nasledujúcich častí:

-   **Backend**: Aplikácia postavená na frameworku Flask, ktorá slúži ako API pre frontend.
-   **Frontend**: Jednostránková webová aplikácia (SPA) napísaná v čistom JavaScripte, HTML a CSS.
-   **Dátové skripty**: Súbor Python skriptov určených na získavanie, spracovanie a analýzu dát z externých zdrojov (Sentinel Hub, Open-Meteo).
-   **Statické súbory**: Obsahuje CSS štýly, JavaScript kód, GeoJSON súbory definujúce oblasti, CSV súbory s dátami a výstupné obrázky.

---

## `backend.py`

Hlavný server aplikácie postavený na `Flask`. Zabezpečuje servírovanie frontendovej aplikácie a poskytuje API endpointy pre spracovanie požiadaviek.

### Knižnice
- `flask`: Webový framework.
- `pandas`: Spracovanie a analýza dát.
- `plotly`: Generovanie dát pre interaktívne grafy.
- `long_term_analysis_trnava`: Import funkcie `generate_trend_map` pre analýzu.

### Konfigurácia
- `POLLEN_TO_MONTHS`: Slovník, ktorý mapuje názvy sezón (`early_spring`, `mid_spring`, atď.) na konkrétne rozsahy mesiacov a dní.

### API Endpoints

#### `GET /`
- **Popis**: Servíruje hlavnú stránku `index.html`.
- **Návratová hodnota**: HTML stránka.

#### `POST /api/plot`
- **Popis**: Prijíma požiadavku s názvom lokality a vracia dáta potrebné na vykreslenie grafov NDVI a teploty.
- **Vstupné JSON dáta**:
    - `location` (string): Kľúč lokality (napr. `janka-krala`, `nemocnicny`).
- **Návratová hodnota (JSON)**:
    - `ndvi_data`: JSON string s dátami pre NDVI graf.
    - `temp_data`: JSON string s dátami pre teplotný graf.
    - `threshold_dates`: JSON string s dátami o dňoch, kedy teplota prekročila 5°C po dobu 5 dní.

#### `POST /api/analyze`
- **Popis**: Spúšťa dlhodobú analýzu trendu vegetácie na základe zvolených rokov a sezóny.
- **Vstupné JSON dáta**:
    - `years` (list): Zoznam rokov na analýzu (napr. `[2022, 2023, 2024]`).
    - `season` (string): Názov sezóny (napr. `late_spring`).
- **Návratová hodnota (JSON)**:
    - `image_url`: URL cesta k vygenerovanému obrázku s mapou trendu.

#### `GET /api/current_pollen`
- **Popis**: Načíta dáta o priemerných peľových zaťaženiach zo súboru `static/pollenAverageLoads.csv`.
- **Návratová hodnota (JSON)**:
    - `pollen_data`: Dáta pripravené na vykreslenie v grafe.

---

## `static/js/main.js`

Frontendová logika aplikácie. Zodpovedá za dynamické načítavanie obsahu, interakciu s používateľom, komunikáciu s backend API a vykresľovanie grafov pomocou knižnice Plotly.js.

### Hlavné funkcie

- **`loadVegetaciu(contentDiv)`**: Vykreslí v hlavnom kontajneri obsah pre analýzu trendu vegetácie (výber rokov, sezóny).
- **`loadPollenSeason(contentDiv)`**: Vykreslí obsah pre analýzu nástupu peľovej sezóny (výber lokality).
- **`loadCurrentPollen(contentDiv)`**: Načíta a zobrazí graf s aktuálnou peľovou situáciou.
- **`handleAnalysis()`**: Zozbiera vstupy od používateľa, odošle požiadavku na `/api/analyze`, zobrazí loading a následne výslednú mapu.
- **`handlePollenAnalysis()`**: Zozbiera vstupy, odošle požiadavku na `/api/plot` a pomocou funkcie `renderPlots` vykreslí grafy.
- **`renderPlots(ndviGraphs, tempGraphs, thresholdDates)`**: Vykreslí interaktívne grafy NDVI a teploty pomocou Plotly. Implementuje logiku prepojeného výberu (kliknutie na jeden graf zvýrazní dáta aj v druhom).
- **`renderPollenPlots(pollenGraphs)`**: Vykreslí graf aktuálnej peľovej situácie.

---

## Dátové skripty

### `long_term_analysis_trnava.py`
Skript určený na analýzu trendu NDVI v čase.

- **Knižnice**: `sentinelhub`, `numpy`, `matplotlib`, `decouple`.
- **Konfigurácia**: Vyžaduje `.env` súbor s `CLIENT_ID` a `CLIENT_SECRET` pre prístup k Sentinel Hub API.
- **Funkcie**:
    - **`get_ndvi_for_year(year, month_start, month_end, ...)`**: Stiahne priemerné NDVI dáta pre zadaný rok a časové obdobie pre definovanú oblasť Trnavy.
    - **`generate_trend_map(years_to_analyze, month_start, month_end)`**: Hlavná funkcia, ktorá pre zadané roky stiahne dáta, vypočíta lineárnu regresiu pre každý pixel a vygeneruje mapu trendu. Mapa sa uloží do `static/output/`.
        - **`years_to_analyze` (list)**: Zoznam rokov.
        - **`month_start` (string)**: Začiatok obdobia (napr. `'06-01'`).
        - **`month_end` (string)**: Koniec obdobia (napr. `'08-31'`).
        - **Návratová hodnota**: Cesta k uloženému obrázku.

### `long_term_analysis.py`
Skript pre detailnejšiu analýzu konkrétnych zelených plôch (parkov). Generuje dáta, ktoré slúžia ako vstup pre ďalšie spracovanie.

- **Popis**: Pre každý definovaný park a pre každý rok v `YEARS_TO_ANALYZE` sťahuje priemerné NDVI dáta v 2-týždňových intervaloch. Zároveň ukladá aj RGB satelitné snímky. Výsledky ukladá do PNG grafu a CSV súboru.
- **Výstupy**:
    - `ndvi_yearly_comparison_*.png`: Graf porovnávajúci roky.
    - `ndvi_yearly_comparison_*.csv`: Surové dáta pre graf. Tento súbor je vstupom pre `interpolacia.py`.

### `getMeteoData.py`
Získava a spracováva historické dáta o teplote.

- **Popis**: Pomocou Open-Meteo API sťahuje denné priemerné teploty pre roky 2020-2025. Následne dáta spracuje, nájde obdobie prvého nástupu vegetačnej sezóny (5 dní nad 5°C) a uloží dáta do `static/temperature_comparison.csv`, ktoré používa `backend.py`.

### `interpolacia.py`
Skript na čistenie a interpoláciu NDVI dát.

- **Popis**: Načíta surové NDVI dáta z `static/csv_raw_linear/`, odfiltruje nízke hodnoty (< 0.4) a pomocou lineárnej interpolácie doplní chýbajúce dáta. Výsledok uloží do `static/csv_interpol_lin/`. Tieto "vyčistené" dáta sa používajú na zobrazenie v grafe nástupu peľovej sezóny.

### `createGeojson.py`
Pomocný nástroj na tvorbu GeoJSON súborov.

- **Popis**: Interaktívny príkazový riadok, ktorý z vložených súradníc vytvorí `*.geojson` súbor v správnom formáte. Používa sa na definovanie hraníc parkov.
- **Použitie**: `python createGeojson.py <nazovSuboru> [--longlat|--latlong]`

### `traspose.py`
Jednoduchý nástroj na transpozíciu (otočenie riadkov za stĺpce) CSV súboru. Pravdepodobne bol použitý na jednorazovú úpravu dát.
