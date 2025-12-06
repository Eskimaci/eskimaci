import csv

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("TkAgg")


def nenulova_hodnota(pole, idx):
    if idx == 0:
        i = 0
        while pole[idx + i] == 0.0:
            i += 1
        return pole[idx + i]
    elif idx == len(pole) - 1:
        i = 0
        while pole[idx - i] == 0.0:
            i += 1
        return pole[idx - i]
    else:
        # doprava
        i = 0
        while pole[idx + i] == 0.0:
            i += 1
        prava = pole[idx + i]

        # dolava
        i = 0
        while pole[idx - i] == 0.0:
            i += 1
        lava = pole[idx - i]

        # linearna interpolacia
        rozdiel = np.abs(lava - prava)
        if lava < prava:
            return lava + (rozdiel / 2)
        else:
            return prava + (rozdiel / 2)


def hodnota_v_bode_x(x, pole_x, pole_y, pct):
    s = 0
    for i in range(pct):
        p = 1
        for j in range(pct):
            if i != j:
                p *= (x - pole_x[j]) / (pole_x[i] - pole_x[j])
        if pole_y[i] == 0.0:
            p *= nenulova_hodnota(pole_y, i)
        else:
            p *= pole_y[i]
        s += p
    return s


with open('static/csv_raw_linear/ndvi_yearly_comparison_2020_2025_Nemocnicny_Park.csv', newline="") as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)
print(data)

pocetx = 12
pocetRokov = 6
odseknut = 0.4
x_hodnoty = np.arange(0, pocetx)

data_roky = [[0.0 for _ in range(pocetx)] for _ in range(pocetRokov)]

for i in range(1, pocetRokov + 1):
    for j in range(1, pocetx + 1):
        if float(data[j][i]) > 0.4:
            data_roky[i - 1][j - 1] = float(data[j][i])
print(data_roky)
for i in range(pocetRokov):
    for j in range(pocetx):
        if data_roky[i][j] == 0.0:
            data_roky[i][j] = float(hodnota_v_bode_x(i, x_hodnoty, data_roky[i], pocetRokov))
print(data_roky)

header = ["Obdobie", "Rok 2020", "Rok 2021", "Rok 2022", "Rok 2023", "Rok 2024", "Rok 2025"]
row_names = ["Feb 1-14", "Feb 15-28", "Mar 1-14", "Mar 15-31", "Apr 1-14", "Apr 15-30", "May 1-14", "May 15-31",
             "Jun 1-14", "Jun 15-30", "Jul 1-14", "Jul 15-31"]
with open("static/csv_interpol_lin/ndvi_yearly_comparison_2020_2025_Nemocnicny_Park.csv", "w", newline="",
          encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    for i in range(pocetx):
        row = [row_names[i]]
        for rok in range(pocetRokov):
            row.append(data_roky[rok][i])
        writer.writerow(row)

# plot

x = np.arange(1, pocetx + 1)

row_names = [
    "Feb 1-14", "Feb 15-28",
    "Mar 1-14", "Mar 15-31",
    "Apr 1-14", "Apr 15-30",
    "May 1-14", "May 15-31",
    "Jun 1-14", "Jun 15-30",
    "Jul 1-14", "Jul 15-31"
]

roky = ["2020", "2021", "2022", "2023", "2024", "2025"]

# plot so zvyrazneniami myskou
fig, ax = plt.subplots(figsize=(14, 7))

lines = []
farby = ["red", "blue", "green", "brown", "cyan", "magenta"]
# vykreslenie kriviek s možnosťou klikania (picker)
for i in range(pocetRokov):
    line, = ax.plot(
        x, data_roky[i],
        marker="o",
        label=roky[i],
        color=farby[i],
        picker=5  # umožní kliknúť na čiaru
    )
    lines.append(line)


# funkcia po kliknutí na čiaru
def on_pick(event):
    line = event.artist

    for l in lines:
        l.set_linewidth(1.5)
        l.set_color("gray")
        l.set_alpha(0.3)

    line.set_linewidth(2)
    line.set_color(farby[int(str(line)[7:11]) - 2020])
    line.set_alpha(1.0)

    fig.canvas.draw_idle()


# prepojenie eventu
fig.canvas.mpl_connect("pick_event", on_pick)

ax.set_xticks(x)
ax.set_xticklabels(row_names, rotation=45, ha="right")
ax.set_xlabel("Obdobie")
ax.set_ylabel("NDVI")
ax.set_ylim(0, 1)
ax.set_title("NDVI vývoj podľa rokov (interpolované hodnoty)")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()
