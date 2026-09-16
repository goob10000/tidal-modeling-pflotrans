from os import listdir
import polars as pl
import numpy as np

dir = "B/B101"
pftfiles = [f for f in listdir(dir) if f.endswith("pft")]

# read in the file. On the first line remove the first character, then split the line into parts by ,. Each item will be a "" bounded string. Remove the "" from each item and save it as a list of strings. These are the column names
# every other line is two spaces followed by a number, repeated for however many column names there are. Read in the numbers and save them as a 2d array of floats.
# Define the array early on (it is #lines - 1 by #columns) and fill it in as you read in the numbers. The first line is the column names, so skip that line when reading in the numbers. Save the array as a numpy array of floats.
# once you have a list of arrays, convert them each to a data frame and then join the data frames on the column name "Time [yr]"
# save the whole thing as a partquet file

dfs = []

for pftfile in pftfiles:
    with open(f"{dir}/{pftfile}", 'r') as f:
        lines = f.readlines()
        column_names = [s.strip('"') for s in lines[0][1:].strip().split(',')]
        data = np.zeros((len(lines) - 1, len(column_names)))
        for i, line in enumerate(lines[1:]):
            numbers = [float(s) for s in line.strip().split()]
            data[i, :] = numbers
        df = pl.DataFrame(data, schema=column_names)
        dfs.append(df)

# join them
df_final = dfs[0]
for df in dfs[1:]:
    df_final = df_final.join(df, on="Time [yr]", how="full").drop("Time [yr]_right")

df_final.write_parquet(f"{dir}/combined.parquet")
