import gzip
import numpy as np
import pandas as pd

path = "data/external/GSE31210_series_matrix.txt.gz"
chars = []
sample_ids = []

with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if line.startswith("!Sample_geo_accession"):
            sample_ids = [s.strip('"\n\r ') for s in line.split("\t")[1:]]
        elif line.startswith("!Sample_characteristics_ch1"):
            chars.append([s.strip('"\n\r ') for s in line.split("\t")[1:]])
        elif line.startswith("!series_matrix_table_begin"):
            break

arr = np.array(chars)
records = []

for col_idx in range(len(sample_ids)):
    sample_id = sample_ids[col_idx]
    entry = {"sample_id": sample_id}
    for row_idx in range(arr.shape[0]):
        val = arr[row_idx, col_idx]
        if ":" in val:
            k, v = val.split(":", 1)
            k = k.strip().lower()
            v = v.strip()
            entry[k] = v
    records.append(entry)

df = pd.DataFrame(records).set_index("sample_id")
print("Total parsed samples:", len(df))
print("Columns:", df.columns.tolist())
print("\nDeath counts:")
print(df["death"].value_counts(dropna=False))
print("\nDays before death/censor summary:")
days = pd.to_numeric(df["days before death/censor"], errors="coerce")
print(days.describe())
print("\nExclude flag counts:")
excl_col = [c for c in df.columns if "exclude" in c][0]
print(df[excl_col].value_counts(dropna=False))

