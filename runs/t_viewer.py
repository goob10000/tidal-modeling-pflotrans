# parse a file to pull the numbers out of this line to make 2 numpy arrays
# The numbers are always in the same columns
#   --> max change: dpmx=   4.6215E+01 dtmpmx=   7.2802E-01

# Time extraction
#  Step   4662 Time=  2.00000E+06 Dt=  1.00000E+00 [yr] conv_reason: 4
import numpy as np
import matplotlib.pyplot as plt
import polars as pl

path = "B/B101/out_data.parquet"
df = pl.read_parquet(path)

t = df["t"]
dt = df["dt"]
dpmx = df["dpmx"]
dtmpmx = df["dtmpmx"]

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

ax1.plot(t, dpmx/dt, 'b-')
ax1.set_ylabel('dpmx')
ax1.set_yscale('log')

ax2.plot(t, dtmpmx/dt, 'r-')
ax2.set_ylabel('dtmpmx')
ax2.set_yscale('log')

ax3.plot(t, dt, 'b-', label='dt [yr]')
ax3.set_ylabel('dt [yr]')
ax3.set_xlabel('Time [yr]')
ax3.set_yscale('log')

plt.show()
# plt.savefig("dpmx_dtmpmx_vs_time_B02.png")