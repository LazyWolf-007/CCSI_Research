# import pandas as pd

# # 1. Load the big combined file
# df = pd.read_excel("output/CCSI_Dataset_WITH_MODERN.xlsx")

# def is_future_scenario(eid):
#     eid = str(eid)
#     if not eid.startswith("E"):
#         return False
#     try:
#         num = int(eid.replace("E", ""))
#     except ValueError:
#         return False
#     # Treat E23–E28 as future scenario
#     return num >= 23

# # 2. Drop future-scenario E rows
# df_clean = df[~df["Era_ID"].apply(is_future_scenario)].copy()

# # 3. Quick sanity checks (optional, just prints)
# n_E = (df_clean["Era_ID"].astype(str).str.startswith("E")).sum()
# n_M = (df_clean["Era_ID"].astype(str).str.startswith("M")).sum()
# print("Historical E-rows:", n_E)
# print("Modern M-rows:", n_M)
# print("Total rows:", len(df_clean))

# # 4. Save a dedicated working file
# df_clean.to_excel("output/CCSI_Dataset_WORKING.xlsx", index=False)
# df_clean.to_csv("output/CCSI_Dataset_WORKING.csv", index=False)
# print("Saved cleaned working file as CCSI_Dataset_WORKING.*")




"""
CCSI — Build the Working Dataset (Historical + Modern, no future scenarios)

This script:
1) loads the combined dataset (historical + modern + future-scenario rows)
2) removes hypothetical future rows (E23 and above)
3) saves the cleaned version used for PCA / KMeans / ML analysis
"""

import os
import pandas as pd

INPUT_FILE = "output/CCSI_Dataset_WITH_MODERN.xlsx"
OUTPUT_XLSX = "output/CCSI_Dataset_WORKING.xlsx"
OUTPUT_CSV = "output/CCSI_Dataset_WORKING.csv"

def is_future_scenario(eid: str) -> bool:
    """Returns True if an Era_ID represents a future/hypothetical era (E23+)."""
    eid = str(eid).strip().upper()
    if not eid.startswith("E"):
        return False
    try:
        num = int(eid[1:])
    except ValueError:
        return False
    return num >= 23

def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)
    print("Loaded:", INPUT_FILE)

    # remove future-scenario rows
    df_clean = df[~df["Era_ID"].apply(is_future_scenario)].copy()

    # print sanity counts
    n_E = df_clean["Era_ID"].str.startswith("E").sum()
    n_M = df_clean["Era_ID"].str.startswith("M").sum()
    print("\n=== CLEANED COUNTS ===")
    print("Historical E rows:", n_E)
    print("Modern M rows:", n_M)
    print("Total rows:", len(df_clean))

    # save files
    df_clean.to_excel(OUTPUT_XLSX, index=False)
    df_clean.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved working dataset:\n - {OUTPUT_XLSX}\n - {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
