import pandas as pd
from gemini import analyze_title
import time

filename = "tenders01.xlsx"
file_path = "tenders02.xlsx"

df = pd.read_excel(filename)

if "TYPE" not in df.columns:
    df["TYPE"] = ""
if "TILES/STONES" not in df.columns:
    df["TILES/STONES"] = ""

for i,row in df.iterrows():
    if pd.notna(row["TYPE"]) and row["TYPE"] != "":
        continue

    title = row["TENDER TITLE"]
    job, tiles = analyze_title(title)

    df.at[i, "TYPE"] = job
    df.at[i, "TILES/STONES"] = tiles

    df.to_excel(file_path, index=False)

    print(f"Processed row {i+1}")

    time.sleep(4)

print("Excel file saved successfully!")