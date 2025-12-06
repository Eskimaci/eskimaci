import numpy as np
def hodnota_v_bode_x(x, pole_x, pole_y, pct):
    s = 0
    for i in range(pct):
        p = 1
        for j in range(pct):
            if i != j:
                p*=(x - pole_x[j])/(pole_x[i] - pole_x[j])
        p*=pole_y[i]
        s += p
    return s

import csv
with open('static/csv/ndvi_yearly_comparison_2020_2025_Nemocnicny_Park.csv', newline="")as csvfile:
    reader= csv.reader(csvfile)
    data = list(reader)
print(data)

pocetx = 12
pocetRokov = 6
odseknut = 0.4
x_hodnoty = np.arange(0, pocetx)

data_roky = [[0.0 for _ in range(pocetx)] for _ in range(pocetRokov)]

for i in range(1,pocetRokov+1):
    for j in range(1, pocetx+1):
        if float(data[j][i]) > 0.4:
            data_roky[i-1][j-1] = float(data[j][i])
print(data_roky)
for i in range(pocetRokov):
    for j in range(pocetx):
        if data_roky[i][j] == 0.0:
            data_roky[i][j] = float(hodnota_v_bode_x(i, x_hodnoty ,data_roky[i] ,pocetRokov))
print(data_roky)

import csv

header = ["Obdobie", "Rok 2020", "Rok 2021", "Rok 2022", "Rok 2023", "Rok 2024", "Rok 2025"]
row_names = ["Feb 1-14", "Feb 15-28", "Mar 1-14", "Mar 15-31", "Apr 1-14", "Apr 15-30", "May 1-14", "May 15-31", "Jun 1-14", "Jun 15-30", "Jul 1-14", "Jul 15-31"]
with open("vystup.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    for i in range(pocetx):
        row = [row_names[i]]
        for rok in range(pocetRokov):
            row.append(data_roky[rok][i])
        writer.writerow(row)

