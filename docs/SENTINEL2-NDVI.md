# Metodika spracovania dát zo Sentinel-2

Tento dokument vysvetľuje, ako projekt získava a spracováva satelitné dáta Sentinel-2 pre analýzu vegetácie.

---

## 1. Primárna metóda: Prístup cez API (`sentinelhub`)

Hlavná funkcionalita projektu – dynamická analýza trendov – **nevyužíva manuálne sťahovanie dát**. Namiesto toho sa pripája priamo na Sentinel Hub API pomocou Python knižnice `sentinelhub`. Tento prístup je plne automatizovaný a extrémne efektívny.

### Proces spracovania

Skript `long_term_analysis_trnava.py` posiela na API požiadavku, ktorá definuje všetko potrebné pre analýzu na strane servera:

1.  **Oblasť záujmu (AOI):** Geometria polygónu ohraničujúceho Trnavu.
2.  **Časový filter:** Konkrétne roky a mesiace, ktoré si používateľ zvolil v aplikácii.
3.  **Evalscript:** Krátky skript v jazyku JavaScript, ktorý sa vykoná priamo na serveroch Sentinel Hub a zabezpečí, že sa do aplikácie pošlú už spracované dáta.

### Kľúčová časť: Evalscript

Evalscript je jadrom efektivity. Namiesto sťahovania surových pásiem (`B04`, `B08`) sa výpočet NDVI vykoná "na diaľku" a aplikácia stiahne len hotový produkt.

```javascript
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B04", "B08", "dataMask"] }],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}

function evaluatePixel(sample) {
  // Ignoruje pixely bez dát (napr. mimo záberu)
  if (sample.dataMask === 0) { 
    return [NaN]; 
  }
  
  // Vzorec pre NDVI
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
```

### Výhody API prístupu

-   **Efektivita:** Sťahuje sa len výsledné NDVI (malý objem dát) namiesto celých scén (často >1 GB).
-   **Automatizácia:** Celý proces je riadený kódom bez nutnosti manuálnej práce.
-   **Mozaikovanie:** API automaticky vyberá najlepšie scény (s najmenšou oblačnosťou) a spája ich do jednej bezchybnej mapy pre dané obdobie.

---

## 2. Manuálny prieskum dát (Alternatíva)

Pre účely overovania, prieskumu alebo manuálnej kontroly je možné dáta stiahnuť aj ručne cez webové rozhranie.

-   **Platforma:** [Copernicus Browser](https://dataspace.copernicus.eu/browser)
-   **Kľúčové filtre:**
    -   **Data Source:** `Sentinel-2`
    -   **Product Level:** `L2A` (atmosféricky korigované dáta)
    -   **Cloud Cover:** `0% - 20%` (pre čo najčistejšie zábery)

Po stiahnutí a rozbalení `.zip` archívu sa kľúčové pásma pre NDVI nachádzajú v priečinku `.../[SAFE_NAME].SAFE/GRANULE/.../IMG_DATA/R10m/`:

-   `*_B04_10m.jp2`: **Červené pásmo (Red)**
-   `*_B08_10m.jp2`: **Blízke infračervené pásmo (NIR)**

---

## 3. Použité vegetačné indexy

-   **NDVI (Normalized Difference Vegetation Index)**
    -   **Účel:** Meria zdravie a hustotu vegetácie. Je to hlavný index používaný v celom projekte.
    -   **Vzorec:** `(B08 - B04) / (B08 + B04)`

---

### Zhrnutie
Projekt sa primárne spolieha na **moderný a efektívny API prístup**, ktorý umožňuje dynamické a automatizované spracovanie dát. Manuálne sťahovanie slúži len ako doplnková metóda pre prieskum.