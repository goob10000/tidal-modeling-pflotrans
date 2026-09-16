import numpy as np
import polars as pl

def extract_numbers_from_line(line):
    # Split the line into parts
    parts = line.split()
    
    # Initialize empty arrays for dpmx and dtmpmx
    dpmx_line = 0
    dtmpmx_line = 0
    
    # Check if the line contains the expected number of parts
    if len(parts) == 7:
        # Extract the numbers from the specific columns
        dpmx_line = float(parts[4])
        dtmpmx_line = float(parts[6])
    
    return dpmx_line, dtmpmx_line

def extract_time_from_line(line):
    # Split the line into parts
    parts = line.split()
    
    # Check if the line contains the expected number of parts
    if len(parts) == 9:
        # Extract the time from the specific column
        return float(parts[3]), float(parts[5])
    
    return 0, 0

f = open("B/B101/B101.out", "r")
l = f.readlines()

# cat B06.out | grep change > t
change_lines = [line for line in l if "change" in line]

# cat B06.out | grep Time= > B06/t1
t_lines = [line for line in l if "Time=" in line]

t, dt = np.zeros(len(t_lines)), np.zeros(len(t_lines))
dpmx, dtmpmx = np.zeros(len(change_lines)), np.zeros(len(change_lines))

for i, line in enumerate(change_lines):
    dpmx_line, dtmpmx_line = extract_numbers_from_line(line)
    dpmx[i] = dpmx_line
    dtmpmx[i] = dtmpmx_line

for i, line in enumerate(t_lines):
    t_here, dt_here = extract_time_from_line(line)
    t[i] = t_here
    dt[i] = dt_here

df = pl.DataFrame({
    "t": t,
    "dt": dt,
    "dpmx": dpmx,
    "dtmpmx": dtmpmx})

df.write_parquet("B/B101/out_data.parquet")