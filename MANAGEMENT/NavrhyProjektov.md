## Kategória A: Životné prostredie a Klíma (Environmentálne zameranie)

### 1. Projekt: "Trnava na suchu? (Boj o vodu)"

Trnava a okolie sú známe suchom. Tento projekt analyzuje vodné plochy a vlhkosť.
**Otázka:** Má Trnava dostatok vodných plôch na rekreáciu a ochladzovanie klímy?
**Dáta:** Sentinel-2.
**Metóda (Python):**

- Namiesto NDVI použijete index NDWI (Normalized Difference Water Index), ktorý zvýrazňuje vodu.
- Porovnáte snímky z jari a z neskorého leta.
- Analyzujte okolité nádrže (napr. Suchá nad Parnou, Buková) – ako dramaticky klesá ich hladina/plocha počas horúčav?
  **Náročnosť:** ⭐⭐ (Stredná - len zmena vzorca oproti NDVI).

### 2. Projekt: "Alergikova nočná mora"

Zadanie spomína "mestskú zeleň" a "trendy". Čo ak sa na zeleň pozriete z pohľadu zdravia?

**Otázka:** Kedy presne v Trnave "vybuchne" jar a kedy je peľová situácia najhoršia?
**Dáta:** Sentinel-2 (časová séria, napr. jedna snímka každé 2 týždne od marca do júna).
**Metóda (Python):**

- Vypočítať priemerné NDVI pre celé mesto v čase.
- Vykresliť graf nástupu vegetácie (fenológia).
- Porovnať rok 2024 s rokom 2020 – posúva sa jar na skorší termín kvôli klimatickej zmene?
  **Náročnosť:** ⭐⭐⭐ (Vyžaduje spracovať viacero snímok naraz).

### 3. Projekt: "Tepelný štít mesta"

Kombinácia dvoch družíc, ktorú navrhoval aj organizátor.

**Otázka:** Ktoré konkrétne parky alebo ulice v Trnave reálne fungujú ako klimatizácia?
**Dáta:** Sentinel-2 (presná mapa budov/stromov) + Sentinel-3 (teplota povrchu).
**Metóda (Python):**

- Sentinel-3 má "hrubé" pixely (nízke rozlíšenie). Vašou úlohou v Pythone bude prekryť tieto dáta detailnou mapou zo
  Sentinel-2.
- Cieľom je dokázať koreláciu: O koľko stupňov je chladnejšie pri rybníku v Kamennom mlyne oproti Trojičnému námestiu?
  **Náročnosť:** ⭐⭐⭐⭐ (Práca s rôznym rozlíšením dát je výzva).

## Kategória B: Urbanizmus a Kvalita života (Analytické zameranie)

### 4. Projekt: "Betónová džungľa vs. Oázy pokoja"

Využitie knižnice OpenCV na klasifikáciu terénu.

**Otázka:** Aký je pomer zastavanej plochy k rekreačnej ploche? Spĺňa Trnava štandardy moderného mesta?
**Dáta:** Sentinel-2.
**Metóda (Python):**

- Použiť OpenCV (computer vision) na segmentáciu obrazu.
- Naučiť program rozoznať 3 triedy: 1. Budovy/Asfalt, 2. Tráva/Parky, 3. Voda.
- Vypočítať percentuálne zastúpenie v kruhu 5 km od centra.
  **Náročnosť:** ⭐⭐⭐⭐ (Vyžaduje trochu znalosti spracovania obrazu).

### 5. Projekt: "Dýcha sa nám dobre? (Air Quality Tracker)"

Zadanie explicitne spomína Sentinel-5p pre "zdatnejších".

**Otázka:** Ako vplýva doprava a priemysel (PSA) na kvalitu vzduchu v Trnave? Je vzduch čistejší cez víkend?
**Dáta:** Sentinel-5p (monitoruje NO2, CO, aerosóly).
**Metóda (Python):**

- Stiahnuť dáta o NO2 (oxid dusičitý - hlavný indikátor splodín z áut).
- Porovnať koncentráciu v pondelok ráno (špička) vs. nedeľa poobede.
- Vizualizovať "mrak" znečistenia nad Trnavou.
  **Náročnosť:** ⭐⭐⭐⭐⭐ (Sentinel-5p má iný formát dát, vyžaduje "hrabanie sa" v dokumentácii).

## Kategória C: Kreatívny / "Punk" prístup (Netradičné riešenia)

### 6. Projekt: "Index ideálneho bývania (The Ultimate Map)"

Toto je komplexný projekt, ktorý spája všetko dokopy.
**Otázka:** Kde presne v Trnave si mám kúpiť byt?
**Dáta:** Sentinel-2 + Sentinel-3 + (voliteľne Google Maps dáta).
**Metóda (Python):**

- Vytvoríte vlastný vzorec (algoritmus).
- Mriežku mesta rozdelíte na malé štvorce.
- Každý štvorec dostane body:
    - +10 bodov za vysoké NDVI (blízko zeleň).
    - -10 bodov za vysokú teplotu (LST zo Sentinel-3).
    - -5 bodov za hustú zástavbu (OpenCV detekcia).
- Výstup: Mapa Trnavy, kde "najzelenšie" (najlepšie) miesta nebudú len parky, ale ideálne kompromisy na bývanie.
  **Náročnosť:** ⭐⭐⭐ (Logicky náročné na vymyslenie váh, programátorsky stredne ťažké).

### 7. Projekt: "Detektívka: Hľadanie ilegálnych skládok / zmien"

Využitie porovnávania v čase.
**Otázka:** Staráme sa o svoje okolie? Kde zmizla zeleň a objavil sa "bordel" alebo neplánovaná stavba?
**Dáta:** Sentinel-2 (rok 2023 vs 2024).
**Metóda (Python):**

- Image Differencing (odčítanie dvoch obrázkov v OpenCV).
- Hľadanie anomálií – miest, kde sa dramaticky zmenila farba pixelov z "prírodnej" na "umelú".
  **Náročnosť:** ⭐⭐ (Zábavné a vizuálne efektné).

## Čo všetko to bude obnášať? (Technický checklist)

Aby ste jeden z týchto projektov zvládli za víkend, tu je realita toho, čo musíte spraviť v Pythone (podľa PDF návodu):
**Stiahnutie dát (Piatok večer):**

- Musíte ísť na Copernicus Browser.
- Filtrovať oblaky na minimum (PDF varuje, že 0% je vzácnosť, berte aj 5-10%).
- Stiahnuť produkt L2A (už atmosféricky korigovaný, ľahší na prácu).

**Spracovanie "GeoJSON" (Sobota ráno):**

- Celá satelitná snímka má 100x100 km. To je na RAM veľa a zbytočné.
- Musíte použiť stránku geojson.io na vytvorenie výrezu Trnavy.
- V Pythone použiť funkciu subset (kód na to máte priamo v PDF na strane 4), aby ste pracovali len s malým výrezom.

**Výpočet indexov (Sobota deň):**

- Toto je jadro práce. Budete pracovať s "bands" (pásmami).
- Sentinel-2 má pásma: B4 (Červená), B8 (NIR - blízke infračervené).
- Vzorec pre NDVI v Pythone (pomocou knižnice Numpy) bude vyzerať cca takto:

```python
ndvi = (B8 - B4) / (B8 + B4)
```

- PDF odkazuje na skripty pre tieto indexy.

**Vizualizácia (Nedeľa doobeda):**

- Použiť Matplotlib na vykreslenie peknej mapy.
- Pridať legendu (čo je dobré, čo zlé).
- Uložiť ako obrázok do prezentácie.

### Tip Gemini-u na víťaza:

Ak chcete zapôsobiť, vyberte si Návrh č. 6 (Index ideálneho bývania). Ukazuje to technickú zručnosť (kombinácia
viacerých dát) a zároveň to dáva perfektnú, zrozumiteľnú odpoveď na otázku "Je dobré bývať v Trnave?".