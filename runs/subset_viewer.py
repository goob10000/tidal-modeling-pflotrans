import polars as pl
import matplotlib.pyplot as plt
import numpy as np

df = pl.read_parquet("B/B09/combined.parquet")

pressure_func = lambda x: int(x.split(" ")[3][9:])
density_func = lambda x: int(x.split(" ")[3][9:])
temperature_func = lambda x: int(x.split(" ")[2][9:])

pressure_cols_ordered = sorted([x for x in df.columns if "Pressure" in x], key=pressure_func)
density_cols_ordered = sorted([x for x in df.columns if "Density" in x], key=density_func)
temperature_cols_ordered = sorted([x for x in df.columns if "Temperature" in x], key=temperature_func)

dfP = df.select(pressure_cols_ordered)
dfD = df.select(density_cols_ordered)
dfT = df.select(temperature_cols_ordered)

x = np.arange(5200, 14801, 1200)
y = np.array([-950, -500])

X, Y = np.meshgrid(x, y)

fig, axes = plt.subplots(3, 2, sharex=True)

ax1, ax2, ax3, ax4, ax5, ax6 = axes.T.flatten()

for col, x_value in zip(pressure_cols_ordered[:9], x):
    ax1.plot(df["Time [yr]"], df[col], label=x_value)
ax1.set_ylabel("Pressure [Pa]")
ax1.legend(loc="upper left", fontsize="small")
ax1.set_title("y = -962.5 m")

for col, x_value in zip(density_cols_ordered[:9], x):
    ax2.plot(df["Time [yr]"], df[col], label=x_value)
ax2.set_ylabel("Density [kg/m^3]")
ax2.legend(loc="upper left", fontsize="small")

for col, x_value in zip(temperature_cols_ordered[:9], x):
    ax3.plot(df["Time [yr]"], df[col], label=x_value)
ax3.set_ylabel("Temperature [K]")
ax3.set_xlabel("Time [yr]")
ax3.legend(loc="upper left", fontsize="small")

for col, x_value in zip(pressure_cols_ordered[9:], x):
    ax4.plot(df["Time [yr]"], df[col], label=x_value)
ax4.set_ylabel("Pressure [Pa]")
ax4.legend(loc="upper left", fontsize="small")
ax4.set_title("y = -512.5 m")

for col, x_value in zip(density_cols_ordered[9:], x):
    ax5.plot(df["Time [yr]"], df[col], label=x_value)
ax5.set_ylabel("Density [kg/m^3]")
ax5.legend(loc="upper left", fontsize="small")

for col, x_value in zip(temperature_cols_ordered[9:], x):
    ax6.plot(df["Time [yr]"], df[col], label=x_value)
ax6.set_ylabel("Temperature [K]")
ax6.set_xlabel("Time [yr]")
ax6.legend(loc="upper left", fontsize="small")

plt.show()