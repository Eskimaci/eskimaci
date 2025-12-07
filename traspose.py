import csv
import numpy as np

with open('static/pollenAverageLoads.csv', newline="") as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)
print(data)

x = 4
pocetRokov = 366


header = [data[0][0], data[1][0], data[2][0], data[3][0]]
row_names = data[0][1::]
print(row_names)

with open("static/pollenAverageLoads.csv1", "w", newline="",
          encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    for i in range(1, pocetRokov-1):
        row = [row_names[i]]
        for rok in range(1, x):
            row.append(data[rok][i])
        writer.writerow(row)