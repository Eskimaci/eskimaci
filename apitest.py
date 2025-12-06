# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request, send_from_directory
from long_term_analysis_trnava import generate_trend_map
import logging
import os

# --- 1. NASTAVENIE APLIKÁCIE ---
app = Flask(__name__, static_folder='static')
logging.basicConfig(level=logging.INFO)

# Definovanie mapovania sezón na mesiace
POLLEN_TO_MONTHS = {
    "early_spring": ("02-01", "03-31"),
    "mid_spring": ("04-01", "05-31"),
    "late_spring": ("06-01", "08-31"),
    "year": ("01-01", "12-31"),
}

# --- 2. DEFINOVANIE ENDPOINTOV (ROUTES) ---

@app.route('/')
def index():
    """Servíruje hlavnú stránku."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Servíruje statické súbory (ako CSS, JS, a vygenerované obrázky)."""
    return send_from_directory('static', path)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint, ktorý prijíma požiadavky na analýzu, spúšťa skript 
    a vracia cestu k výslednému obrázku.
    """
    try:
        data = request.get_json()
        app.logger.info(f"Prijatá požiadavka na analýzu s dátami: {data}")

        years = data.get('years')
        season = data.get('season')

        # --- Validácia vstupov ---
        if not years or not isinstance(years, list) or len(years) < 2:
            return jsonify({"error": "Je potrebné poskytnúť pole s aspoň dvoma rokmi."}), 400
        
        if not season or season not in POLLEN_TO_MONTHS:
            return jsonify({"error": f"Neplatné obdobie. Dostupné možnosti: {', '.join(POLLEN_TO_MONTHS.keys())}"}), 400

        # Konvertujeme roky na celé čísla
        try:
            years = [int(y) for y in years]
        except (ValueError, TypeError):
            return jsonify({"error": "Pole 'years' musí obsahovať iba celé čísla."}), 400

        month_start, month_end = POLLEN_TO_MONTHS[season]

        app.logger.info(f"Spúšťam generovanie mapy pre roky {years} a obdobie {season} ({month_start} - {month_end})...")
        
        # --- Spustenie analýzy ---
        # Funkcia generate_trend_map je importovaná z long_term_analysis_trnava.py
        image_path = generate_trend_map(years, month_start, month_end)

        if image_path:
            # Prevedieme cestu k súboru na URL, ktorú môže frontend použiť
            # napr. 'static/output/map.png' -> '/static/output/map.png'
            image_url = "/" + image_path.replace(os.path.sep, '/')
            app.logger.info(f"Generovanie úspešné. Obrázok dostupný na: {image_url}")
            return jsonify({"image_url": image_url})
        else:
            app.logger.error("Generovanie zlyhalo, nebol vrátený žiadny obrázok.")
            return jsonify({"error": "Nepodarilo sa vygenerovať mapu. Skontrolujte logy pre viac detailov."}), 500

    except Exception as e:
        app.logger.error(f"Nastala neočakávaná chyba v /api/analyze: {e}", exc_info=True)
        return jsonify({"error": f"Interná chyba servera: {e}"}), 500

# --- 3. SPUSTENIE SERVERA ---

if __name__ == '__main__':
    # Spustenie Flask servera v debug móde pre jednoduchší vývoj
    app.run(debug=True, port=5001)
