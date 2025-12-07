# Projekt: Analýza mestskej zelene v Trnave

Webová aplikácia pre analýzu a vizualizáciu dlhodobých trendov vegetácie (NDVI) v Trnave. Projekt využíva satelitné dáta zo Sentinel-2 a porovnáva ich s lokálnymi teplotnými dátami na identifikáciu zmien v ekosystéme.

---

## Kľúčové funkcie

Aplikácia poskytuje dva hlavné analytické nástroje:

1.  **Dynamická analýza trendu vegetácie**:
    -   Používateľ si môže zvoliť ľubovoľné roky (od 2017) a peľovú sezónu.
    -   Aplikácia naživo stiahne dáta z **Sentinel Hub API** a vygeneruje mapu, ktorá farebne vizualizuje, či sa zeleň v celej Trnave dlhodobo zlepšuje (zelená), zhoršuje (červená) alebo stagnuje (biela).
    -   Tento nástroj je ideálny na sledovanie celoplošných zmien a dopadov klimatických zmien alebo urbanizácie.

2.  **Porovnanie nástupu peľovej sezóny**:
    -   Pre vybrané parky a zelené plochy v Trnave aplikácia zobrazuje interaktívne grafy.
    -   Grafy porovnávajú vývoj vegetačného indexu (NDVI) a priemerných teplôt v priebehu rokov 2020-2025.
    -   Umožňuje identifikovať, či teplejšie zimy spôsobujú skorší nástup vegetačnej sezóny, čo priamo súvisí so začiatkom peľových alergií.

---

## Štruktúra projektu

    .
    ├── backend.py              # Hlavný Flask server (API)
    ├── getMeteoData.py         # Skript na stiahnutie teplotných dát
    ├── long_term_analysis_trnava.py # Skript pre celoplošnú analýzu trendu
    ├── requirements.txt        # Zoznam Python knižníc
    ├── DOCS.md                 # Technická dokumentácia
    ├── static/                 # Frontend (CSS, JS) a dáta (CSV, GeoJSON)
    │   ├── js/main.js          # Hlavná logika frontendu
    │   ├── csv_interpol_lin/   # Spracované dáta pre grafy
    │   └── output/             # Vygenerované mapy trendu
    └── templates/
        └── index.html          # Hlavná HTML šablóna

---

## Inštalácia a spustenie

### 1. Klonovanie repozitára
```bash
git clone https://github.com/Eskimaci/eskimaci.git
cd eskimaci
```

### 2. Vytvorenie a aktivácia virtuálneho prostredia
Uistite sa, že máte nainštalovaný Python 3.11 alebo novší.

```bash
# Vytvorenie virtuálneho prostredia
python3 -m venv venv

# Aktivácia prostredia (macOS/Linux)
source venv/bin/activate
# Pre Windows: venv\Scripts\activate
```

### 3. Konfigurácia API prístupu
Pre fungovanie dynamickej analýzy trendu je potrebný prístup k Sentinel Hub.

1.  Vytvorte si bezplatný účet na [**Copernicus Dataspace Ecosystem**](https://dataspace.copernicus.eu/).
2.  Vytvorte si *OAuth Client* v dashboarde a získajte `Client ID` a `Client Secret`.
3.  V hlavnom priečinku projektu vytvorte súbor s názvom `.env`.
4.  Do súboru `.env` vložte svoje prístupové údaje:
    ```env
    CLIENT_ID="vas-client-id"
    CLIENT_SECRET="vas-client-secret"
    ```

### 4. Inštalácia závislostí
Všetky potrebné knižnice sú v súbore `requirements.txt`.

```bash
pip install -r requirements.txt
```

<details>
<summary>⚠️ Poznámky k inštalácii pre rôzne OS</summary>

Inštalácia niektorých geo-knižníc (napr. `rasterio`) môže byť zložitá kvôli ich systémovým závislostiam (knižnica GDAL).

*   **🪟 Windows:**
    *   Priama inštalácia cez `pip` môže zlyhať. Odporúča sa použiť `conda` (z prostredia Anaconda/Miniconda), ktorá nainštaluje všetko potrebné automaticky:
        ```bash
        conda install -c conda-forge geopandas rasterio
        ```
    *   Až potom spustite `pip install -r requirements.txt`.

*   **🍎 macOS:**
    *   Najprv nainštalujte GDAL cez Homebrew:
        ```bash
        brew install gdal
        ```
    *   Následne by mal príkaz `pip install -r requirements.txt` fungovať správne.

*   **🐧 Linux (Debian/Ubuntu):**
    *   Nainštalujte vývojárske hlavičky pre GDAL:
        ```bash
        sudo apt-get update && sudo apt-get install libgdal-dev
        ```
    *   Potom pokračujte s `pip install`.
</details>

### 5. Spustenie aplikácie
Po aktivácii prostredia a inštalácii spustite Flask server:

```bash
flask --app backend run --debug
```
alebo priamo:
```bash
python3 manage.py
```

Aplikácia bude dostupná na adrese [**http://127.0.0.1:5001**](http://127.0.0.1:5001).

---
> ### 💡 Poznámka k pomocným skriptom
>
> V repozitári sa nachádzajú aj ďalšie skripty (`getMeteoData.py`, `interpolacia.py`, `createGeojson.py`). Tieto slúžili na **jednorazovú prípravu statických dát** (CSV a GeoJSON súbory) a nie je nutné ich spúšťať pre bežnú prevádzku aplikácie. Pre viac detailov si pozrite [Technickú dokumentáciu](DOCS.md).
