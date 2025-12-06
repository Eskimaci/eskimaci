# 🚀 Projekt: Analýza mestskej zelene v Trnave

**Cieľ:** Webová aplikácia pre analýzu a vizualizáciu dlhodobých trendov vegetácie (NDVI) v Trnave pomocou dát zo Sentinel-2 a porovnanie s teplotnými dátami.

**Platforma:** Python 3.13, Flask

---

## 1. Architektúra a Funkcionalita

Aplikácia má dve hlavné funkcie:

1.  **Dynamická analýza trendu vegetácie:** Používateľ si môže zvoliť obdobie (roky a sezónu) a aplikácia naživo vygeneruje mapu, ktorá ukazuje, ako sa zeleň v Trnave dlhodobo mení (zlepšuje/zhoršuje). Využíva priame pripojenie na **Sentinel Hub API**.
2.  **Porovnávacie grafy:** Pre vybrané parky v Trnave aplikácia zobrazuje interaktívne grafy, ktoré porovnávajú vývoj NDVI a teplôt v priebehu rokov 2020-2025.

**UPOZORNENIE:** Analýza odhalila, že zatiaľ čo NDVI dáta sú korektne z Trnavy, teplotné dáta v porovnávacom grafe pochádzajú z lokality v Berlíne, Nemecko.

---

## 2. Inštalácia Prostredia

### A. Klonovanie repozitára
```bash
git clone <https://github.com/Eskimaci/eskimaci.git>
cd eskimaci
```

### B. Python a Virtuálne Prostredie
Uistite sa, že máte nainštalovaný Python 3.13.

```bash
# Vytvorenie virtuálneho prostredia
python3 -m venv venv

# Aktivácia prostredia
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### C. Inštalácia Knižníc
Všetky potrebné knižnice sú v súbore `requirements.txt`. Nainštalujte ich príkazom:

```bash
pip install -r requirements.txt
```

#### ⚠️ Poznámky pre jednotlivé OS
Inštalácia niektorých geovedeckých knižníc (`rasterio`, `geopandas`) môže byť zložitá kvôli ich závislosti na C++ knižnici GDAL.

*   **🪟 Windows:**
    *   Priama inštalácia cez `pip` s veľkou pravdepodobnosťou zlyhá, ak nemáte správne nainštalované a nakonfigurované GDAL.
    *   **Odporúčaný postup:** Nainštalujte tieto knižnice pomocou manažéra balíčkov `conda` (z prostredia Anaconda/Miniconda), ktorý sa postará o všetky závislosti:
        ```bash
        conda install -c conda-forge geopandas rasterio
        ```
    *   Až potom spustite `pip install -r requirements.txt` na doinštalovanie ostatných závislostí.

*   **🍎 macOS:**
    *   Inštalácia by mala byť jednoduchšia. Ak narazíte na problém s GDAL, nainštalujte ho cez Homebrew:
        ```bash
        brew install gdal
        ```
    *   Následne by mal príkaz `pip install -r requirements.txt` fungovať korektne.

*   **🐧 Linux (Debian/Ubuntu):**
    *   Pred inštaláciou sa uistite, že máte nainštalované vývojárske hlavičky pre GDAL:
        ```bash
        sudo apt-get update && sudo apt-get install libgdal-dev
        ```
    *   Potom by mala inštalácia cez `pip` prebehnúť bez problémov.

#### Kľúčové knižnice v projekte:
- **[Flask](https://flask.palletsprojects.com/):** Mikro-framework, na ktorom beží backend aplikácie.
- **[sentinelhub](https://sentinelhub-py.readthedocs.io/):** Oficiálna knižnica pre priame sťahovanie a spracovanie dát zo Sentinel Hub API. Jadro dynamickej analýzy.
- **[openmeteo_requests](https://pypi.org/project/openmeteo-requests/):** Knižnica na sťahovanie historických dát o počasí.
- **[numpy](https://numpy.org/):** Základ pre numerické výpočty, najmä pre prácu s rastrovými dátami (NDVI) a výpočet trendu.
- **[pandas](https://pandas.pydata.org/) & [geopandas](https://geopandas.org/):** Nástroje na manipuláciu s dátovými tabuľkami a geo-dátami.
- **[matplotlib](https://matplotlib.org/):** Vykresľovanie finálnej mapy trendu.
- **[plotly](https://plotly.com/python/):** Generovanie interaktívnych grafov vo webovom rozhraní.
- **[python-decouple](https://pypi.org/project/python-decouple/):** Načítavanie citlivých premenných (API kľúče) zo súboru.

---

## 3. Konfigurácia API Prístupu

Pre fungovanie dynamickej analýzy (Funkcionalita 1) je potrebné získať prístupové údaje k Sentinel Hub.

1.  Vytvorte si účet na [**Copernicus Dataspace Ecosystem**](https://dataspace.copernicus.eu/).
2.  Vytvorte si OAuth Client v dashboarde a získajte `Client ID` a `Client Secret`.
3.  V hlavnom priečinku projektu vytvorte súbor s názvom `.env`
4.  Do súboru `.env` vložte svoje prístupové údaje v nasledovnom formáte:

```
CLIENT_ID=vas_client_id
CLIENT_SECRET=vas_client_secret
```

---

## 4. Spustenie Aplikácie

Po aktivácii virtuálneho prostredia a nainštalovaní knižníc spustite Flask server:

```bash
flask --app backend run --debug
```
Alebo alternatívne:
```bash
python backend.py
```

Aplikácia bude dostupná na adrese `http://127.0.0.1:5001`.

---
> ### 💡 Poznámka k ostatným skriptom
>
> V repozitári sa nachádzajú aj ďalšie skripty (`getMeteoData.py`, `interpolacia.py`, `createGeojson.py`), ktoré nie sú priamo súčasťou Flask aplikácie. Tieto slúžili na jednorazovú prípravu a spracovanie statických dát (CSV a GeoJSON súbory), ktoré aplikácia využíva pre porovnávacie grafy. Nie je nutné ich spúšťať pre bežnú prevádzku aplikácie.
>
> #### Poznámka k Matplotlib Backendu
> Hlavná webová aplikácia (spúšťaná cez `backend.py`) používa `matplotlib.use('Agg')`, čo je neinteraktívny backend, ktorý ukladá obrázky do súborov bez potreby grafického rozhrania. To zaručuje bezproblémový beh na akomkoľvek serverovom prostredí (Windows, macOS, Linux).
>
> Naopak, pomocné skripty (`getMeteoData.py`, `interpolacia.py`) používajú `matplotlib.use('TkAgg')` a pri priamom spustení sa pokúsia otvoriť okno s grafom. Na niektorých systémoch to môže vyžadovať doinštalovanie knižníc pre GUI (napr. `python3-tk` na Linuxe).