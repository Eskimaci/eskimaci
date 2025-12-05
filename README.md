# 🚀 Hackathon Setup Guide: Analýza dát zo Sentinelu v Trnave

**Cieľ:** Pripraviť kompletné vývojové prostredie na spracovanie satelitných snímok (Sentinel-2) do 15 minút.

**Platforma:** Python 3.13

---

## 1. Inštalácia IDE (PyCharm)

Odporúčané IDE je [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/), ktoré je zadarmo a plne postačujúce pre tento projekt.

### 🪟 Windows
1.  Stiahnite si **PyCharm Community Edition** z oficiálnej stránky.
2.  Spustite inštalátor (`.exe`).
3.  **Kľúčový krok:** Počas inštalácie zaškrtnite možnosť **"Add 'bin' folder to the PATH"**.
4.  Po dokončení inštalácie odporúčame reštartovať PC.

### 🍎 macOS
-   **Cez Homebrew (odporúčané):**
    Ak máte nainštalovaný [Homebrew](https://brew.sh/), otvorte terminál a zadajte:
    ```sh
    brew install --cask pycharm-ce
    ```
-   **Manuálna inštalácia:**
    1.  Stiahnite si `.dmg` súbor z webu JetBrains.
    2.  Otvorte ho a presuňte ikonu PyCharm do priečinku `Applications`.

### 🐧 Linux (Ubuntu/Debian)
-   **Cez Snap (odporúčané):**
    Otvorte terminál a zadajte príkaz:
    ```sh
    sudo snap install pycharm-community --classic
    ```
-   **Cez Software Center:**
    Vyhľadajte "PyCharm Community" a nainštalujte.

---

## 2. Inštalácia Pythonu (verzia 3.13)

Potrebujeme samotný engine pre beh skriptov. Verziu si overíte v termináli príkazom `python3 --version`.

### 🪟 Windows
1.  Stiahnite si inštalátor **Python 3.13** z [oficiálnej stránky](https://www.python.org/downloads/).
2.  **POZOR:** Pri spustení inštalácie zaškrtnite na spodnej lište možnosť **"Add Python to PATH"**.

### 🍎 macOS
Použite Homebrew v termináli:
```sh
brew install python@3.13
```

### 🐧 Linux
Väčšina distribúcií už Python má. Ak nie, alebo ak máte staršiu verziu, použite:
```sh
sudo apt update && sudo apt install python3 python3-pip python3-venv
```

---

## 3. Založenie Projektu a Virtuálneho Prostredia (Sandbox)

Každý projekt by mal mať vlastné izolované prostredie, aby sa predišlo konfliktom medzi knižnicami.

1.  Otvorte **PyCharm**.
2.  Zvoľte **New Project**.
3.  Nastavte nasledujúce parametre:
    -   **Location:** `.../TrnavaHackathon` (alebo názov podľa seba).
    -   **Interpreter type:** Zvoľte **Project venv**.
    -   **Python version:** Z ponuky vyberte nainštalovanú verziu 3.13.
4.  Kliknite na **Create**.

---

## 4. Inštalácia Knižníc (Nástroje)

Tieto knižnice sú nevyhnutné na analýzu (NDVI), detekciu objektov a prácu s geodátami.

V PyCharme otvorte panel **Terminal** (v dolnej lište) a skopírujte tam nasledujúci príkaz na hromadnú inštaláciu:

```bash
pip install numpy matplotlib opencv-python shapely geopandas rasterio sentinelsat
```

### Vysvetlenie arzenálu:
-   **[numpy](https://pypi.org/project/numpy/):** Základ pre matematiku a prácu s maticami (nevyhnutné pre výpočet indexov ako NDVI).
-   **[matplotlib](https://pypi.org/project/matplotlib/):** Knižnica na vykresľovanie grafov a máp pre vizualizáciu výsledkov.
-   **[opencv-python](https://pypi.org/project/opencv-python/):** Knižnica pre počítačové videnie (detekcia budov, ciest, klasifikácia terénu).
-   **[shapely](https://pypi.org/project/Shapely/) & [geopandas](https://pypi.org/project/geopandas/):** Nástroje na prácu s geometrickými dátami vo formáte GeoJSON (napr. ohraničenie územia Trnavy).
-   **[rasterio](https://pypi.org/project/rasterio/):** Efektívna knižnica na čítanie satelitných snímok (formát GeoTIFF). Je to rýchlejšia a flexibilnejšia alternatíva k SNAP API.
-   **[sentinelsat](https://pypi.org/project/sentinelsat/):** Voliteľná knižnica na automatizované sťahovanie dát priamo z Pythonu.

---

## 5. Prístup k Dátam (Copernicus)

Bez dát nemáme čo analyzovať.

1.  Vytvorte si účet (každý člen tímu) na [**Copernicus Dataspace Ecosystem**](https://dataspace.copernicus.eu/).
2.  Pre analýzu budeme sťahovať produkty **Sentinel-2 L2A**. Dátová vrstva L2A je už atmosféricky korigovaná, čo nám ušetrí veľa času.

---

> ### 💡 Tip Mentora pre SNAP API
>
> Ak by ste v zadaní hackathonu silou-mocou trvali na použití `snappy` (oficiálne, ale komplikované Python API pre softvér SNAP od ESA):
>
> 1.  Museli by ste stiahnuť a nainštalovať softvér **ESA SNAP**.
> 2.  Počas inštalácie je potrebné správne nakonfigurovať prepojenie s Pythonom, čo je často problematické a zlyháva na novších verziách Pythonu (nad 3.8).
>
> **Rada:** Na 48-hodinovom hackathone sa `snappy` radšej vyhnite. Použitie `rasterio` a `numpy` je výrazne rýchlejšie, jednoduchšie na inštaláciu a výsledok (napr. NDVI mapa) je úplne rovnaký.

---

### Ako toto všetko pomáha odpovedať na otázku, či je dobré bývať v Trnave?
S týmto setupom dokážete do 30 minút od začiatku načítať satelitnú snímku Trnavy, vypočítať, aký je podiel zelene (NDVI), a vizualizovať to. Získate nástroj na analýzu založenú na reálnych dátach, nie len na dojmoch.

Máte všetko nainštalované? Môžeme prejsť na "Hello World" kód pre načítanie prvej satelitnej snímky.
