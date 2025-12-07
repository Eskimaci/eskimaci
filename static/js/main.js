function loadVegetaciu(contentDiv) {
    contentDiv.innerHTML = `
    <h1 class="hero-title">Ako sa mení vegetácia počas peľových sezón?</h1>
            <p class="hero-subtitle">
                Zvoľte si roky a peľovú sezónu pre analýzu. Nástroj vyhodnotí zeleň (NDVI) v danom období a porovná jej vývoj naprieč rokmi, čo môže pomôcť identifikovať zmeny v intenzite peľových alergénov.
            </p>

            <div class="hero-controls">
                <div class="control-group">
                    <label for="year-select">Vyberte roky (aspoň dva)</label>
                    <div id="year-checkbox-container" class="year-checkbox-group">
                        </div>
                </div>
                <div class="control-group">
                    <label for="season-select">Peľová sezóna</label>
                    <div class="control-input">
                        <select id="season-select">
                            <option value="early_spring">Skorá jar (Feb-Mar)</option>
                            <option value="mid_spring">Stredná jar (Apr-Máj)</option>
                            <option value="late_spring" selected>Neskorá jar / Leto (Jún-Aug)</option>
                            <option value="year">Celý rok</option>
                        </select>
                    </div>
                    <div id="season-info"></div>
                </div>
                <div class="control-group button-group">
                    <label>&nbsp;</label>
                    <button class="primary" id="analyze-btn">Analyzovať trend</button>
                </div>
            </div>
            <section id="results" class="results-section">
                <div class="placeholder-text">Výsledná mapa trendu sa zobrazí tu.</div>
            </section>
    `;
}

function loadPollenSeason(contentDiv) {
    contentDiv.innerHTML = `
           <h1 class="hero-title">Nástup peľovej sezóny</h1>
            <p class="hero-subtitle">
                Analyzujte zmeny vegetácie počas peľových sezón v Trnave v rôznych oblastiach. Vyberte oblasť, aby ste zistili, ako sa mení množstvo zelene, čo môže indikovať intenzitu peľových alergénov.
            </p>

            <div class="hero-controls">
                <div class="control-group">
                    <label for="location-select">Nástup peľovej sezóny</label>
                    <div class="control-input">
                        <select id="location-select">
                            <option value="janka-krala">Park Janka Kráľa</option>
                            <option value="nemocnicny">Nemocničný park</option>
                            <option value="strky" selected>Štrky</option>
                            <option value="druzba">Park za družbou</option>
                            <option value="zahradkarska">Záhradkárska oblasť</option>
                            <option value="kamenac">Kamenáč</option>
                            <option value="rybniky">Rybníky</option>
                            </select>
                    </div>
                </div>
                <div class="control-group">
                    <label>&nbsp;</label>
                    <button class="primary analyze-polen" id="analyze-polen-btn">Zobraziť vývoj peľovej sezóny</button>
                </div>
            </div>
            <section id="results" class="results-section">
                <div class="placeholder-text">Výsledná mapa trendu sa zobrazí tu.</div>
            </section>`;
}

async function loadCurrentPollen(contentDiv) {
    contentDiv.innerHTML = `
           <h1 class="hero-title">Aktuálna peľová situácia</h1>
            <p class="hero-subtitle">
                Aktuálne koncentrácie peľu za tento rok. Keďže analýza peľových údajov je zložitá a časovo náročná, nie je možné ju zobraziť v reálnom čase. Grafy budú aktualizované, keď budú k dispozícii nové údaje.
            </p>
            <section id="results austria-graph" class="results-section">

            </section>`;

    // Load the Austria pollen graph
    try{
        const response = await fetch('/api/current_pollen');
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! Status: ${response.status}`);
        }
        const resultsSection = document.getElementById('results austria-graph');
        if (resultsSection) {
            const pollenGraphs = JSON.parse(data.pollen_data);
            renderPollenPlots(pollenGraphs);

        }
    }catch(error){
        console.error('Error loading current pollen data:', error);
        showError(`Chyba pri načítaní aktuálnych peľových údajov: ${error.message}`);
    }
}

const content = document.querySelector('.content-div');

// Define pollenInfo at the top before any functions use it
const pollenInfo = {
    early_spring: "Hlavné alergény: Lieska, Jelša, Tis.",
    mid_spring: "Hlavné alergény: Javor, Jaseň, Bresty.",
    late_spring: "Hlavné alergény: Pagaštan, Lipa, trávy.",
    year: "Analýza pre celý kalendárny rok."
};

// Function to switch methodology visibility
function updateMethodology(activeId) {
    const methodologies = document.querySelectorAll('.metodika-content');
    methodologies.forEach(method => {
        if (method.id === activeId) {
            method.style.display = 'block';
        } else {
            method.style.display = 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // Load vegetation analysis by default on page load
    loadVegetaciu(content);
    let yearContainer = document.getElementById('year-checkbox-container');
    populateYearCheckboxes(yearContainer);
    attachVegetationListeners();
    updateMethodology('metodika-vegetacia'); // Show default methodology

    const vegBtn = document.querySelector('.load-veg-btn');
    vegBtn.addEventListener('click', () => {
        loadVegetaciu(content);
        yearContainer = document.getElementById('year-checkbox-container');
        populateYearCheckboxes(yearContainer);
        attachVegetationListeners();
        updateMethodology('metodika-vegetacia');
    });

    const pollenBtn = document.querySelector('.load-pollen-btn');
    pollenBtn.addEventListener('click', () => {
        loadPollenSeason(content);
        attachPollenListeners();
        updateMethodology('metodika-sezona');
    });

    const currPollenBtn = document.querySelector('.load-curr-poll-btn');
    currPollenBtn.addEventListener('click', () => {
        loadCurrentPollen(content);
        updateMethodology('metodika-pollen');
    });
});


function attachVegetationListeners() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const seasonSelect = document.getElementById('season-select');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalysis);
    }
    if (seasonSelect) {
        seasonSelect.addEventListener('change', updateSeasonInfo);
        updateSeasonInfo();
    }
}

function attachPollenListeners() {
    const analyzePolenBtn = document.getElementById('analyze-polen-btn');
    if (analyzePolenBtn) {
        analyzePolenBtn.addEventListener('click', handlePollenAnalysis);
    }
}



// Populácia rokov ako checkboxy
function populateYearCheckboxes(yearContainer) {
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= 2017; year--) {
        const div = document.createElement('div');
        div.className = 'year-checkbox';
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.id = `year-${year}`;
        input.value = year;
        // Predvolene vyberieme posledné dva roky
        if (year === currentYear || year === currentYear - 1) {
            input.checked = true;
        }
        const label = document.createElement('label');
        label.htmlFor = `year-${year}`;
        label.textContent = year;
        div.appendChild(input);
        div.appendChild(label);
        yearContainer.appendChild(div);
    }
}

function updateSeasonInfo() {
    const seasonSelect = document.getElementById('season-select');
    const seasonInfo = document.getElementById('season-info');
    if (seasonSelect && seasonInfo) {
        const selectedSeason = seasonSelect.value;
        seasonInfo.textContent = pollenInfo[selectedSeason] || "";
    }
}

async function handlePollenAnalysis() {

    const locationSelect = document.getElementById('location-select');
    const resultsSection = document.getElementById('results');
    const analyzePolenBtn = document.getElementById('analyze-polen-btn');

    const selectedLocation = locationSelect.value;

    showLoading();
    if (analyzePolenBtn) {
        analyzePolenBtn.disabled = true;
        analyzePolenBtn.textContent = 'Načítavam...';
    }

    try {
        const response = await fetch('/api/plot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                location: selectedLocation,
            }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! Status: ${response.status}`);
        }

        // Parse the plot data and render it
        const ndviData = JSON.parse(data.ndvi_data);
        const tempData = JSON.parse(data.temp_data);
        const thresholdDates = JSON.parse(data.threshold_dates);
        renderPlots(ndviData, tempData, thresholdDates);

    } catch (error) {
        console.error('Plot error:', error);
        showError(`Chyba pri generovaní grafu: ${error.message}`);
    } finally {
        if (analyzePolenBtn) {
            analyzePolenBtn.disabled = false;
            analyzePolenBtn.textContent = 'Zobraziť vývoj peľovej sezóny';
        }
    }
}

function renderPollenPlots(pollenGraphs){
    const resultsSection = document.getElementById('results austria-graph');
    if (!resultsSection) return;

    resultsSection.innerHTML = `
            <div id="pollen-chart-container" style="width: 100%; height: 500px;"></div>
            `;

    // Pollen Plot Layout
    const pollenLayout = {
        title: 'Aktuálna peľová situácia v tomto roku',
        xaxis: {
            title: 'Dátum',
            type: 'category',
            tickangle: -45,
            nticks: 15
        },
        yaxis: {
            title: 'Koncentrácia peľu',
            range: [0, null]
        },
        hovermode: 'closest',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {color: '#e5e7eb'},
        legend: {
            orientation: 'v',
            x: 1.02,
            y: 1
        }
    };

    Plotly.newPlot('pollen-chart-container', pollenGraphs, pollenLayout);
}

function renderPlots(ndviGraphs, tempGraphs, thresholdDates) {
    const resultsSection = document.getElementById('results');
    if (!resultsSection) return;

    // Create containers for both plots
    resultsSection.innerHTML = `
            <div id="ndvi-chart-container" style="width: 100%; height: 500px; margin-bottom: 30px;"></div>
            <div id="temp-chart-container" style="width: 100%; height: 500px;"></div>
        `;

    // --- 1. Apply rounding (2 decimal places) to tooltips ---
    ndviGraphs.forEach(trace => {
        trace.hovertemplate = `<b>${trace.name}</b><br>Obdobie: %{x}<br>NDVI: %{y:.2f}<extra></extra>`;
    });

    tempGraphs.forEach(trace => {
        trace.hovertemplate = `<b>${trace.name}</b><br>Dátum: %{x}<br>Teplota: %{y:.2f}°C<extra></extra>`;
    });

    // --- 2. Initialize Single Selection State ---
    // Defaults to index 0 (first year)
    let activeIndex = 5;

    // NDVI Plot Layout
    const ndviLayout = {
        title: 'NDVI - Porovnanie rokov',
        xaxis: {
            title: 'Obdobie',
            type: 'category',
            tickangle: -45,
            nticks: 10
        },
        yaxis: {
            title: 'NDVI',
            range: [0, 1]
        },
        hovermode: 'closest',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {color: '#e5e7eb'},
        legend: {
            orientation: 'v',
            x: 1.02,
            y: 1,
            itemclick: false,
            itemdoubleclick: false
        }
    };

    // Temperature Plot Layout
    const tempLayout = {
        title: 'Teplota - Porovnanie rokov',
        xaxis: {
            title: 'Dátum',
            type: 'category',
            tickangle: -45,
            nticks: 15
        },
        yaxis: {
            title: 'Teplota (°C)',
            range: [0, null]
        },
        hovermode: 'closest',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {color: '#e5e7eb'},
        legend: {
            orientation: 'v',
            x: 1.02,
            y: 1,
            itemclick: false,
            itemdoubleclick: false
        }
    };

    // Draw both plots
    Plotly.newPlot('ndvi-chart-container', ndviGraphs, ndviLayout);
    Plotly.newPlot('temp-chart-container', tempGraphs, tempLayout);

    const ndviPlot = document.getElementById('ndvi-chart-container');
    const tempPlot = document.getElementById('temp-chart-container');

    // --- 3. Add Threshold Markers (Hidden by default unless year is selected) ---
    const markerTraces = [];
    const renderedData = tempPlot.data;

    Object.entries(thresholdDates).forEach(([yearCol, info]) => {
        const lineIndex = tempGraphs.findIndex(trace => trace.name === yearCol);
        if (lineIndex === -1) return;

        const lineColor = renderedData[lineIndex].line.color;
        const dates = [];
        const values = [];

        for (let i = info.start_index; i <= info.end_index; i++) {
            dates.push(tempGraphs[lineIndex].x[i]);
            values.push(tempGraphs[lineIndex].y[i]);
        }

        const markerTrace = {
            x: dates,
            y: values,
            mode: 'markers',
            type: 'scatter',
            name: `${yearCol} - Threshold`,
            marker: {
                size: 10,
                color: lineColor,
                symbol: 'diamond',
                line: {
                    color: lineColor,
                    width: 2
                }
            },
            opacity: 0, // Initially hidden, handled by updateSingleSelection
            showlegend: false,
            hovertemplate: `<b>${yearCol}</b><br>5+ days ≥5°C<br>%{x}<br>%{y:.2f}°C<extra></extra>`
        };

        markerTraces.push(markerTrace);
    });

    if (markerTraces.length > 0) {
        Plotly.addTraces('temp-chart-container', markerTraces);
    }

    // --- 4. NEW Function: Update Single Selection ---
    function updateSingleSelection() {
        const nTraces = ndviGraphs.length;
        const lineOpacities = [];
        const lineWidths = [];

        // Calculate styles for lines
        for (let i = 0; i < nTraces; i++) {
            if (i === activeIndex) {
                lineOpacities.push(1.0); // Active
                lineWidths.push(4);
            } else {
                lineOpacities.push(0.15); // Inactive (dimmed)
                lineWidths.push(1.5);
            }
        }

        // Update lines on both plots
        const traceIndices = [...Array(nTraces).keys()];
        Plotly.restyle('ndvi-chart-container', { 'opacity': lineOpacities, 'line.width': lineWidths }, traceIndices);
        Plotly.restyle('temp-chart-container', { 'opacity': lineOpacities, 'line.width': lineWidths }, traceIndices);

        // Update markers (Temp only)
        const tempPlotDiv = document.getElementById('temp-chart-container');
        const totalTraces = tempPlotDiv.data.length;

        if (totalTraces > nTraces) {
            const markerIndices = [];
            const markerOpacities = [];
            const activeYearName = tempGraphs[activeIndex].name;

            for (let i = nTraces; i < totalTraces; i++) {
                markerIndices.push(i);
                const traceName = tempPlotDiv.data[i].name;
                // Only show markers that match the active year name
                if (traceName.startsWith(activeYearName)) {
                    markerOpacities.push(1.0);
                } else {
                    markerOpacities.push(0.0);
                }
            }
            Plotly.restyle('temp-chart-container', { 'opacity': markerOpacities }, markerIndices);
        }
    }

    // --- 5. Event Handlers ---

    function handleSelection(data) {
        // Get index from clicked point OR legend item
        const clickedIndex = data.points ? data.points[0].curveNumber : data.curveNumber;

        // Ignore clicks on markers (indices higher than line count)
        if (clickedIndex < ndviGraphs.length) {
            activeIndex = clickedIndex;
            updateSingleSelection();
        }
        return false; // Prevent default legend behavior
    }

    // Attach handlers
    ndviPlot.on('plotly_click', handleSelection);
    ndviPlot.on('plotly_legendclick', handleSelection);
    tempPlot.on('plotly_click', handleSelection);
    tempPlot.on('plotly_legendclick', handleSelection);

    // Apply initial state (select first year)
    updateSingleSelection();
}

async function handleAnalysis() {
    const yearContainer = document.getElementById('year-checkbox-container');
    const seasonSelect = document.getElementById('season-select');
    const resultsSection = document.getElementById('results');
    const analyzeBtn = document.getElementById('analyze-btn');

    const selectedYears = Array.from(yearContainer.querySelectorAll('input[type="checkbox"]:checked'))
            .map(cb => cb.value);
    const selectedSeason = seasonSelect.value;

    if (selectedYears.length < 2) {
        showError("Vyberte prosím aspoň dva roky pre analýzu trendu.");
        return;
    }

    showLoading();
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Spracúvam...';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                years: selectedYears,
                season: selectedSeason,
            }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! Status: ${response.status}`);
        }
        showImage(data.image_url);
    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Chyba pri analýze: ${error.message}`);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyzovať trend';
    }
}

function showLoading() {
    const resultsSection = document.getElementById('results');
    if (resultsSection) {
        resultsSection.innerHTML = '<div class="spinner"></div><p class="placeholder-text" style="margin-top: 10px;">Prebieha analýza, môže to trvať aj viac ako minútu...</p>';
    }
}

function showImage(imageUrl) {
    const resultsSection = document.getElementById('results');
    if (resultsSection) {
        const url = `${imageUrl}?t=${new Date().getTime()}`;
        resultsSection.innerHTML = `<img src="${url}" alt="Mapa trendu vegetácie">`;
    }
}

function showError(message) {
    const resultsSection = document.getElementById('results');
    if (resultsSection) {
        resultsSection.innerHTML = `<div class="error-message">${message}</div>`;
    }
}
