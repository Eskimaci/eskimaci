import matplotlib

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

matplotlib.use("Agg")

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 48.3860,
    "longitude": 17.5724,
    "start_date": "2020-01-01",
    "end_date": "2025-12-04",
    "daily": "temperature_2m_mean",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
    freq=pd.Timedelta(seconds=daily.Interval()),
    inclusive="left"
)}

daily_data["temperature_2m_mean"] = daily_temperature_2m_mean

daily_dataframe = pd.DataFrame(data=daily_data)

years = range(2020, 2026)
data = []
for year in years:
    df = daily_dataframe[(daily_dataframe['date'] >= pd.Timestamp(str(year) + '-01-15', tz='UTC')) & (
            daily_dataframe['date'] <= pd.Timestamp(str(year) + '-07-31', tz='UTC'))].copy()
    data.append(df)

temp_threshold = 5
days_threshold = 5
start_days = []
for year in range(len(years)):
    for i in range(data[year]['date'].size - days_threshold):
        if data[year]['temperature_2m_mean'][i:i + days_threshold].min() >= temp_threshold:
            print(data[year][:][i:i + days_threshold])
            start_days.append(i)
            break

fig, ax = plt.subplots(figsize=(12, 7))
arbitrary_common_year = 2024

default_selection_index = 0

lines = []

for i in range(len(years)):
    data[i]['date'] = data[i]['date'].apply(lambda d: d.replace(year=arbitrary_common_year))
    start_date = pd.to_datetime(data[i]['date'].iloc[start_days[i]])
    end_date = start_date + pd.Timedelta(days=4)

    if i == default_selection_index:
        init_alpha = 1.0
        init_lw = 2.0
        init_highlight_visible = True
        init_zorder = 10
    else:
        init_alpha = 0.1
        init_lw = 1.5
        init_highlight_visible = False
        init_zorder = 1

    line, = ax.plot(data[i]['date'], data[i]['temperature_2m_mean'],
                    label=f'Rok {years[i]}',
                    linewidth=init_lw, alpha=init_alpha,
                    zorder=init_zorder, picker=5)
    # lines.append(line)
    line_color = line.get_color()
    mask = (data[i]['date'] >= start_date) & (data[i]['date'] <= end_date)
    highlight_data = data[i].loc[mask]
    # ax.plot(highlight_data['date'], highlight_data['temperature_2m_mean'], color=line_color, linewidth=4, marker='o', markersize=5)
    highlight, = ax.plot(highlight_data['date'], highlight_data['temperature_2m_mean'],
                         color="#000000", linewidth=4, marker='o', markersize=5,
                         visible=init_highlight_visible,  # Set visibility based on default
                         zorder=init_zorder)
    lines.append((line, highlight))

leg = ax.legend(loc='upper left')

picker_map = {}
for leg_line, leg_text, (main_line, high_line) in zip(leg.get_lines(), leg.get_texts(), lines):
    leg_line.set_picker(5)
    leg_text.set_picker(5)
    picker_map[leg_line] = (main_line, high_line)
    picker_map[leg_text] = (main_line, high_line)
    picker_map[main_line] = (main_line, high_line)


def on_pick(event):
    if event.artist in picker_map:
        target_main, target_high = picker_map[event.artist]

        # Iterate over PLOT lines and LEGEND items together by index
        # We assume they are in the same order because they were created in the same loop
        current_leg_lines = leg.get_lines()
        current_leg_texts = leg.get_texts()

        for i, (main, high) in enumerate(lines):
            # Get the corresponding legend items for this index
            lg_line = current_leg_lines[i]
            lg_text = current_leg_texts[i]

            if main == target_main:
                # === SELECTED ===
                # Plot
                main.set_alpha(1.0)
                main.set_linewidth(2.0)
                high.set_visible(True)
                main.set_zorder(10)
                high.set_zorder(10)

                # Legend
                lg_line.set_alpha(1.0)
                lg_text.set_alpha(1.0)
            else:
                # === DIMMED ===
                # Plot
                main.set_alpha(0.1)
                main.set_linewidth(1.5)
                high.set_visible(False)
                main.set_zorder(1)
                high.set_zorder(1)

                # Legend (Set alpha to 0.3 so it's faint but readable)
                lg_line.set_alpha(0.3)
                lg_text.set_alpha(0.3)

        fig.canvas.draw()


fig.canvas.mpl_connect("pick_event", on_pick)

ax.set_title("Temperature Trends (5-Day Highlight)", fontsize=16)
ax.set_xlabel("Date")
ax.set_ylabel("Temperature Mean")
# ax.legend()
ax.grid(True, linestyle='--', alpha=0.5)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
fig.autofmt_xdate()

# Create a pivot table format - find the minimum length across all years
min_length = min(len(data[i]) for i in range(len(years)))

combined_df = pd.DataFrame()

# ZMENA JE TU: Pridali sme .dt.date
# Toto oreže časovú zložku a nechá len dátum (YYYY-MM-DD)
combined_df['date'] = data[0]['date'].iloc[:min_length].dt.date.reset_index(drop=True)

for i, year in enumerate(years):
    combined_df[f'Rok {year}'] = data[i]['temperature_2m_mean'].iloc[:min_length].reset_index(drop=True)

combined_df.to_csv('../static/temperature_comparison.csv', index=False)
