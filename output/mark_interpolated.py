import pandas as pd

# Input file names
ORIGINAL = "CCSI_Dataset.xlsx"
FIXED    = "CCSI_Dataset_FIXED.xlsx"
OUTPUT   = "CCSI_Dataset_FINAL.xlsx"

# Load both datasets
df_old = pd.read_excel(ORIGINAL)
df_new = pd.read_excel(FIXED)

# Indicator columns (detected automatically)
indicator_cols = [
    c for c in df_old.columns
    if c.startswith(("D1_SM_", "D2_ED_", "D3_EC_", "D4_PO_", "D5_CU_"))
]

# Function → check whether a row was interpolated
def was_interpolated(old_row):
    notes = str(old_row.get("Notes", "")).lower()
    srcs  = str(old_row.get("Sources_List", "")).lower()
    if "parsing failed" in notes or "parsing failed" in srcs:
        return 1
    if all(float(old_row.get(c, 0)) == 0 for c in indicator_cols):
        return 1
    return 0

# Create "Interpolated" column
df_new["Interpolated"] = [
    was_interpolated(row) for _, row in df_old.iterrows()
]

# ---- REORDER COLUMNS ----
cols = list(df_new.columns)

# Remove and reinsert Interpolated before Sources_List
cols.remove("Interpolated")
insert_pos = cols.index("Sources_List")   # position of Sources_List
cols.insert(insert_pos, "Interpolated")   # insert Interpolated before it

df_new = df_new[cols]

# Save updated files
df_new.to_excel(OUTPUT, index=False)
df_new.to_csv(OUTPUT.replace(".xlsx", ".csv"), index=False)

print("Done — Interpolated column placed before Sources_List.")
