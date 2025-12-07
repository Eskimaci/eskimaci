import csv

with open('static/pollenAverageLoads.csv', newline="") as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)

y = len(data[0]) #dlzka riadku
pocetRokov = len(data) #dlzka stlpca


with open("static/pollenAverageLoads.csv1", "w", newline="",
          encoding="utf-8") as f:
    writer = csv.writer(f)

    for i in range(y):
        row = []
        for rok in range(pocetRokov):
            row.append(data[rok][i])
        writer.writerow(row)