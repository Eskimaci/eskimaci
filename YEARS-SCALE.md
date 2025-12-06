# Dokumentácia: Dlhodobá analýza vývoja vegetácie

Tento dokument popisuje účel a použitie skriptu `long_term_analysis.py`.

## Ako spustiť analýzu

Skript spustíte jednoduchým príkazom v termináli z hlavného adresára projektu:

```bash
python long_term_analysis_trnava.py
```

## Ako to funguje

Proces analýzy prebieha v niekoľkých krokoch:

1.  **Slučka cez roky:** Skript si prejde zoznam definovaných rokov (napr. 2023, 2024, 2025).
2.  **Zber dát:** Pre každý rok stiahne satelitné dáta (NDVI) za rovnaké obdobie (napr. august). Tým zabezpečí porovnateľnosť dát.
3.  **Výpočet trendu:** Keď sú všetky dáta stiahnuté, skript pre každý pixel v mape vypočíta trend pomocou lineárnej regresie. Zistí, či sa hodnota vegetačného indexu v čase zvyšovala alebo znižovala.
4.  **Generovanie mapy:** Výsledky z predošlého kroku použije na vytvorenie finálnej mapy trendu.

## Výstup

Výstupom skriptu je obrázkový súbor vo formáte `.png`, napríklad `ndvi_trend_trnava_2023_2025.png`.

### Interpretácia farieb na mape:

-   **Zelená:** Označuje oblasti s **pozitívnym trendom**. Vegetácii sa tu v priebehu sledovaných rokov darilo stále lepšie.
-   **Červená:** Označuje oblasti s **negatívnym trendom**. Zeleň tu slabla, ustupovala alebo bola pod stresom.
-   **Biela / Svetlé farby:** Označuje oblasti, kde nedošlo k žiadnej významnej zmene (stabilný stav).

Intenzita farby zodpovedá sile trendu – čím je farba sýtejšia, tým bola zmena výraznejšia.
