import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("TkAgg")


def non_zero_value(arr, idx):
    if idx == 0:
        i = 0
        while arr[idx + i] == 0.0:
            i += 1
        return arr[idx + i]
    elif idx == len(arr) - 1:
        i = 0
        while arr[idx - i] == 0.0:
            i += 1
        return arr[idx - i]
    else:
        # right
        i = 0
        while arr[idx + i] == 0.0:
            i += 1
        right_val = arr[idx + i]

        # left
        i = 0
        while arr[idx - i] == 0.0:
            i += 1
        left_val = arr[idx - i]

        # linear interpolation
        difference = np.abs(left_val - right_val)
        if left_val < right_val:
            return left_val + (difference / 2)
        else:
            return right_val + (difference / 2)


def value_at_x(x, x_array, y_array, count):
    s = 0
    for i in range(count):
        p = 1
        for j in range(count):
            if i != j:
                p *= (x - x_array[j]) / (x_array[i] - x_array[j])
        if y_array[i] == 0.0:
            p *= non_zero_value(y_array, i)
        else:
            p *= y_array[i]
        s += p
    return s


with open('static/csv_raw_linear/ndvi_yearly_comparison_2020_2025_Nemocnicny_Park.csv', newline="") as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)
print(data)

num_x = 12
num_years = 6
cutoff = 0.4
x_values = np.arange(0, num_x)

yearly_data = [[0.0 for _ in range(num_x)] for _ in range(num_years)]

for i in range(1, num_years + 1):
    for j in range(1, num_x + 1):
        if float(data[j][i]) > cutoff:
            yearly_data[i - 1][j - 1] = float(data[j][i])
print(yearly_data)

for i in range(num_years):
    for j in range(num_x):
        if yearly_data[i][j] == 0.0:
            yearly_data[i][j] = float(value_at_x(j, x_values, yearly_data[i], num_x))
print(yearly_data)

header = ["Period", "Year 2020", "Year 2021", "Year 2022", "Year 2023", "Year 2024", "Year 2025"]
row_names = ["Feb 1-14", "Feb 15-28", "Mar 1-14", "Mar 15-31", "Apr 1-14", "Apr 15-30", "May 1-14", "May 15-31",
             "Jun 1-14", "Jun 15-30", "Jul 1-14", "Jul 15-31"]
with open("static/csv_interpol_lin/nemocnicny.csv", "w", newline="",
          encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    for i in range(num_x):
        row = [row_names[i]]
        for year in range(num_years):
            row.append(yearly_data[year][i])
        writer.writerow(row)

# plot

x = np.arange(1, num_x + 1)

row_names = [
    "Feb 1-14", "Feb 15-28",
    "Mar 1-14", "Mar 15-31",
    "Apr 1-14", "Apr 15-30",
    "May 1-14", "May 15-31",
    "Jun 1-14", "Jun 15-30",
    "Jul 1-14", "Jul 15-31"
]

years = ["2020", "2021", "2022", "2023", "2024", "2025"]

# plot with mouse highlighting
fig, ax = plt.subplots(figsize=(14, 7))

lines = []
colors = ["red", "blue", "green", "brown", "cyan", "magenta"]
# plot curves with picking enabled
for i in range(num_years):
    line, = ax.plot(
        x, yearly_data[i],
        marker="o",
        label=years[i],
        color=colors[i],
        picker=5  # allow clicking on the line
    )
    lines.append(line)


# function for line click event
def on_pick(event):
    line = event.artist

    for l in lines:
        l.set_linewidth(1.5)
        l.set_color("gray")
        l.set_alpha(0.3)

    line.set_linewidth(2)
    line.set_color(colors[years.index(line.get_label())])
    line.set_alpha(1.0)

    fig.canvas.draw_idle()


# connect event
fig.canvas.mpl_connect("pick_event", on_pick)

ax.set_xticks(x)
ax.set_xticklabels(row_names, rotation=45, ha="right")
ax.set_xlabel("Period")
ax.set_ylabel("NDVI")
ax.set_ylim(0, 1)
ax.set_title("NDVI Development by Year (Interpolated Values)")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()
