# Dokumentácia Projektu: Analýza mestskej zelene v Trnave

Tento dokument popisuje reálne implementovaný stav projektu a jeho kľúčové funkcie. Pôvodné nápady sú uvedené v druhej časti pre historický kontext.

---

## Implementovaný Projekt: Dlhodobá analýza NDVI a teplotných trendov

Projekt je webová aplikácia, ktorá poskytuje dva hlavné pohľady na analýzu mestskej zelene a klímy v Trnave.

### Funkcionalita 1: Dynamická mapa trendu vývoja vegetácie

Táto funkcia predstavuje jadro projektu a umožňuje dynamickú analýzu na základe vstupov od používateľa.

*   **Otázka:** Zlepšuje sa alebo zhoršuje stav vegetácie v Trnave v priebehu posledných rokov?
*   **Dáta:** Sentinel-2 L2A (sťahované naživo cez API).
*   **Metóda (Python - `sentinelhub`, `numpy`):**
    1.  Používateľ si vo webovom rozhraní zvolí periódu (napr. 2022-2024) a sezónu (napr. leto).
    2.  Aplikácia sa pripojí na Sentinel Hub API a pre každý zadaný rok stiahne mozaiku NDVI dát pre oblasť Trnavy.
    3.  Pre každý pixel v mape sa vypočíta **trend pomocou lineárnej regresie** cez zadané roky.
    4.  Výsledkom je farebná mapa, ktorá vizualizuje, či sa NDVI v danej lokalite dlhodobo zvyšuje (zlepšenie, zelená farba) alebo znižuje (zhoršenie, červená farba).
*   **Technický stav:** ⭐⭐⭐⭐ (Pokročilá analýza, práca s API, výpočet trendu).

### Funkcionalita 2: Porovnávací graf NDVI a Teploty

Táto funkcia slúži na vizuálne porovnanie ročných období v predpripravených grafoch.

*   **Otázka:** Ako vyzeral priebeh vegetácie a teplôt v jednotlivých parkoch v Trnave v porovnaní s minulými rokmi?
*   **Dáta:**
    *   **NDVI:** Pred-spracované dáta z `static/csv_interpol_lin/`. Pôvodom zo Sentinel-2.
    *   **Teplota:** Pred-spracované dáta z `static/temperature_comparison.csv`. Pôvodom z Open-Meteo API.
*   **Metóda (Python - `Flask`, `pandas`, `plotly`):**
    1.  Používateľ si vyberie konkrétny park (napr. Park Janka Kráľa, Kamenný mlyn).
    2.  Aplikácia načíta zodpovedajúce CSV súbory a vykreslí dva interaktívne grafy:
        *   Jeden porovnáva priemerný vývoj NDVI v danom parku naprieč rokmi 2020-2025.
        *   Druhý porovnáva priebeh priemerných denných teplôt naprieč rokmi 2020-2025.
*   **Kľúčové zistenie (Metodická chyba):** Analýza kódu (`getMeteoData.py`) odhalila, že dáta o teplote nie sú pre Trnavu, ale pre lokalitu v **Berlíne, Nemecko**. Aplikácia teda chybne koreluje NDVI z Trnavy s teplotami z Berlína.
*   **Technický stav:** ⭐⭐ (Jednoduché zobrazenie statických dát).

---

## Pôvodné nápady a koncepty (pred implementáciou)

Toto bola pôvodná sada návrhov, z ktorých projekt vychádzal.

### Kategória A: Životné prostredie a Klíma

1.  **Projekt: "Trnava na suchu?"**
    *   **Stav:** Nerealizované. Projekt sa zameral na NDVI (vegetáciu), nie na NDWI (vodu).
2.  **Projekt: "Alergikova nočná mora"**
    *   **Stav:** Čiastočne implementované. Projekt analyzuje NDVI v čase a hľadá nástup vegetácie cez teplotné prahy, čo sú základy fenológie.
3.  **Projekt: "Tepelný štít mesta"**
    *   **Stav:** Implementované v upravenej forme. Projekt síce nespája Sentinel-2 a Sentinel-3, ale priamo koreluje NDVI (zo Sentinel-2) s externými teplotnými dátami (aj keď z chybnej lokality).

### Kategória B: Urbanizmus a Kvalita života

4.  **Projekt: "Betónová džungľa vs. Oázy pokoja"**
    *   **Stav:** Nerealizované. Knižnica `OpenCV` nebola použitá na klasifikáciu.
5.  **Projekt: "Dýcha sa nám dobre? (Air Quality Tracker)"**
    *   **Stav:** Nerealizované. Dáta zo Sentinel-5p neboli použité.

### Kategória C: Kreatívny / "Punk" prístup

6.  **Projekt: "Index ideálneho bývania"**
    *   **Stav:** Nerealizované. Komplexný index nebol vytvorený.
7.  **Projekt: "Detektívka: Hľadanie ilegálnych skládok"**
    *   **Stav:** Nerealizované. Metóda "Image Differencing" nebola implementovaná.
