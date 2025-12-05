import pandas as pd

df = pd.read_excel("output/CCSI_Dataset_WORKING.xlsx")


# Normalize Era_ID display
df['Era_ID_clean'] = df['Era_ID'].astype(str).str.strip().str.upper()

# Count by prefix
print(df['Era_ID_clean'].str.startswith("E").sum(), "Total E rows")
print(df['Era_ID_clean'].str.startswith("M").sum(), "Total M rows")

# Group by Region & Era_ID type
print("\nM rows by region:\n", df[df['Era_ID_clean'].str.startswith("M")]['Region'].value_counts())

# Check for extra modern eras (M06 etc.)
print("\nUnique M era IDs:", sorted(df[df['Era_ID_clean'].str.startswith("M")]['Era_ID_clean'].unique()))
