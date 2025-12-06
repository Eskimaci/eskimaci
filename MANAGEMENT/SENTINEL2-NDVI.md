# SENTINEL-2 DÁTA: Konfigurácia a Metodika v Projekte

Tento dokument vysvetľuje, ako projekt pracuje s dátami zo Sentinel-2.

---

## 1. Primárna Metóda: Priamy Prístup cez API (`sentinelhub`)

Hlavná funkcionalita projektu (dynamická analýza trendov) **nesťahuje manuálne ZIP súbory**. Namiesto toho využíva knižnicu `sentinelhub` v Pythone na priamy prístup k dátam cez API.

*   **Proces:** Skript `long_term_analysis_trnava.py` posiela požiadavku na Sentinel Hub API, ktorá obsahuje:
    1.  **Oblasť záujmu (AOI):** Polygón Trnavy.
    2.  **Časový filter:** Zvolené roky a mesiace.
    3.  **Evalscript:** Krátky skript v jazyku JavaScript, ktorý sa vykoná priamo na serveroch Sentinel Hub.

*   **Evalscript pre NDVI:** Toto je kľúčová časť, ktorá počíta NDVI na diaľku a posiela späť do aplikácie už hotové dáta, čím šetrí lokálne zdroje. V projekte použitý evalscript vyzerá takto:

```javascript
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B08", "dataMask"] }],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  if (sample.dataMask === 0) { return [NaN]; } // Ignoruje pixely bez dát
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
```

*   **Výhody:**
    *   **Efektivita:** Sťahujú sa len výsledné NDVI dáta (malý objem), nie celé 1.2 GB scény.
    *   **Automatizácia:** Celý proces je riadený kódom.
    *   **Mozaikovanie:** API automaticky vyberá najlepšie scény (najmenej oblakov) a spája ich do jednej mapy.

---

## 2. Alternatívna Metóda: Manuálne Sťahovanie (pre prieskum)

Nižšie popísaný postup manuálneho sťahovania je stále platný a užitočný pre prieskum dát, overovanie alebo ak by bolo potrebné pracovať s celými scénami lokálne.

*   **Platforma:** [Copernicus Browser](https://dataspace.copernicus.eu/browser)
*   **Login:** Vyžadovaný pre sťahovanie.

### Filtre pre vyhľadávanie

*   **Location:** `Trnava, Slovakia`
*   **Data Source:** `Sentinel-2`
*   **Product Level:** `L2A` (Level-2A, atmosféricky korigované)
*   **Cloud Cover:** `0% - 20%`
*   **Time Range:** napr. `2023-06-01` to `2023-08-31`

### Proces sťahovania

1.  **Visualize:** Skontrolujte náhľad, či Trnava nie je pod oblakmi.
2.  **Download:** Kliknite na "Download". Súbor bude mať formát `.zip`.
3.  **Extraction:** Rozbaľte archív, čím získate priečinok `.SAFE`.

### Štruktúra súborov a kľúčové pásma

V rámci `.SAFE` priečinka sú najdôležitejšie pásma v 10m rozlíšení tu:
`./[SAFE_NAME].SAFE/GRANULE/[GRANULE_NAME]/IMG_DATA/R10m/`

*   `*_B04_10m.jp2` -> **Red** (Červené pásmo - kľúčové pre NDVI)
*   `*_B08_10m.jp2` -> **NIR** (Blízke infračervené pásmo - kľúčové pre NDVI)
*   `*_B03_10m.jp2` -> **Green** (Zelené pásmo - kľúčové pre NDWI)

---

## 3. Vzorce pre Indexy (Použité v Projekte)

*   **NDVI (Normalized Difference Vegetation Index):** Používa sa na meranie zdravia a hustoty vegetácie.
    *   Vzorec: `(B08 - B04) / (B08 + B04)`

*   **NDWI (Normalized Difference Water Index):** Používa sa na identifikáciu vodných plôch.
    *   Vzorec: `(B03 - B08) / (B03 + B08)`
    *   *Poznámka: Tento index bol v pôvodných návrhoch, ale finálny projekt ho nevyužíva.*
