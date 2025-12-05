"""
CCSI (Civilizational Cohesion & Social Inclusivity) Dataset Generator
GEMINI-ONLY VERSION (no Perplexity)

Requirements:
    pip install requests pandas openpyxl
"""

import requests
import pandas as pd
import time
import os
import datetime

# ==============================
# 🔑 PUT YOUR GEMINI KEY HERE
# ==============================
GEMINI_API_KEY = "PUT_YOUR_API_KEY_HERE"

# ==============================
# ERA & REGION GRID
# ==============================

ERAS = [
    "E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10",
    "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20",
    "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28"
]

REGIONS = {
    "Gangetic North": ERAS,
    "Northwest (Punjab–Gandhāra)": ERAS,
    "Deccan": ERAS[2:],
    "Tamilakam": ERAS[3:],
    "Northeast": ERAS[5:]
}

COLUMNS = [
    "Era_ID", "Era_Start_Year", "Era_End_Year", "Region",
    "D1_SM_OccupationalMobility", "D1_SM_StatusFluidity", "D1_SM_InstitutionalMobility",
    "D1_SM_IntergroupTransferability", "D1_SM_MeritocraticPathways",
    "D2_ED_KnowledgeGatekeeping", "D2_ED_LanguageOfTransmission", "D2_ED_EducationalInfrastructure",
    "D2_ED_PedagogicalInclusivity", "D2_ED_IntellectualPluralism",
    "D3_EC_OccupationalPlurality", "D3_EC_GuildMarketAccessibility", "D3_EC_InternalMarketIntegration",
    "D3_EC_ExternalTradeLinkages", "D3_EC_StateRedistributionWelfare",
    "D4_PO_AdminIntegration", "D4_PO_SuccessionStability", "D4_PO_TerritorialContinuity",
    "D4_PO_ConflictManagement", "D4_PO_DiplomaticStability",
    "D5_CU_FreedomOfWorship", "D5_CU_RitualInclusivity", "D5_CU_SocialContactNorms",
    "D5_CU_SyncretismHybridization", "D5_CU_NormativeHierarchyVsEquality",
    "D1_Total", "D2_Total", "D3_Total", "D4_Total", "D5_Total", "CCSI_Total",
    "Notes", "Sources_List"
]

def get_era_years(era_id):
    era_years = {
        "E01": (-1500, -1000), "E02": (-1000, -500), "E03": (-500, -200), "E04": (-200, 100),
        "E05": (100, 300), "E06": (300, 500), "E07": (500, 700), "E08": (700, 900),
        "E09": (900, 1100), "E10": (1100, 1300), "E11": (1300, 1500), "E12": (1500, 1700),
        "E13": (1700, 1800), "E14": (1800, 1850), "E15": (1850, 1900), "E16": (1900, 1920),
        "E17": (1920, 1947), "E18": (1947, 1960), "E19": (1960, 1980), "E20": (1980, 2000),
        "E21": (2000, 2020), "E22": (2020, 2040), "E23": (2040, 2060), "E24": (2060, 2080),
        "E25": (2080, 2100), "E26": (2100, 2120), "E27": (2120, 2140), "E28": (2140, 2160)
    }
    return era_years.get(era_id, (0, 0))

# ==============================
# LOGGING & FILE IO
# ==============================

def log_message(message: str):
    os.makedirs("output", exist_ok=True)
    log_path = os.path.join("output", "log.txt")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
    print(message)

def create_output_directory():
    if not os.path.exists("output"):
        os.makedirs("output")
        log_message("Created output directory")

def load_existing_dataset():
    csv_path = os.path.join("output", "CCSI_Dataset.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            log_message(f"Loaded existing dataset with {len(df)} rows")
            return df
        except Exception as e:
            log_message(f"Error loading dataset: {e}")
            return pd.DataFrame(columns=COLUMNS)
    else:
        log_message("No existing dataset found")
        return pd.DataFrame(columns=COLUMNS)

def save_dataset(df: pd.DataFrame):
    csv_path = os.path.join("output", "CCSI_Dataset.csv")
    xls_path = os.path.join("output", "CCSI_Dataset.xlsx")
    try:
        df.to_csv(csv_path, index=False)
        df.to_excel(xls_path, index=False)
        log_message(f"Saved dataset: {len(df)} rows")
    except Exception as e:
        log_message(f"Error saving dataset: {e}")

# ==============================
# GEMINI HELPERS
# ==============================

def call_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=60
        )
        if not resp.ok:
            log_message(f"Gemini RAW: {resp.status_code} {resp.text}")
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        log_message(f"Gemini error: {e}")
        return f"ERROR: {e}"

# ==============================
# PROMPT TO GEMINI (EVIDENCE + SCORES)
# ==============================

GEMINI_FULL_PROMPT = """
You are an academic historian and historical sociologist.

TASK:
For the given ERA and REGION, you must:
1. Internally gather historical evidence (using your web tools where needed) about:
   - social structure and mobility
   - education
   - economy
   - polity
   - culture & religion
2. Score 25 sub-indicators on a 0–4 scale.
3. Provide a short summary sentence.
4. List key academic sources (books/articles) used.

Era ID: {era}
Region: {region}
Approximate years: {start_year} to {end_year} CE

SCORING SCALE (0–4):
0 = Trait absent or opposite
1 = Very weak / marginal
2 = Moderate / mixed
3 = Strong / structurally important
4 = Dominant / defining

SUB-INDICATORS (IN ORDER):
D1 – SOCIAL MOBILITY
1. D1_SM_OccupationalMobility
2. D1_SM_StatusFluidity
3. D1_SM_InstitutionalMobility
4. D1_SM_IntergroupTransferability
5. D1_SM_MeritocraticPathways

D2 – EDUCATION
6.  D2_ED_KnowledgeGatekeeping
7.  D2_ED_LanguageOfTransmission
8.  D2_ED_EducationalInfrastructure
9.  D2_ED_PedagogicalInclusivity
10. D2_ED_IntellectualPluralism

D3 – ECONOMY
11. D3_EC_OccupationalPlurality
12. D3_EC_GuildMarketAccessibility
13. D3_EC_InternalMarketIntegration
14. D3_EC_ExternalTradeLinkages
15. D3_EC_StateRedistributionWelfare

D4 – POLITY
16. D4_PO_AdminIntegration
17. D4_PO_SuccessionStability
18. D4_PO_TerritorialContinuity
19. D4_PO_ConflictManagement
20. D4_PO_DiplomaticStability

D5 – CULTURE
21. D5_CU_FreedomOfWorship
22. D5_CU_RitualInclusivity
23. D5_CU_SocialContactNorms
24. D5_CU_SyncretismHybridization
25. D5_CU_NormativeHierarchyVsEquality

OUTPUT FORMAT (VERY IMPORTANT):
Return a SINGLE LINE CSV with this structure:

scores_csv|notes|sources_list

Where:
- scores_csv  = 25 integers (0–4) in the above order, comma-separated, NO spaces.
- notes       = one sentence (max 25 words) summarizing key structural features.
- sources_list= 6–12 academic sources, formatted as "Author (Year) – Title", separated by semicolons.

Example (structure, not actual values):

3,2,3,1,4,2,2,3,1,2,3,2,3,2,1,3,2,3,2,2,1,0,1,2,4|Late Vedic Ganga shows rigid varna, strong ritual gatekeeping, moderate agrarian commercialization, and early state formation.|Thapar (2002) – Early India; Sharma (1983) – Material Culture and Social Formations; Bronkhorst (2007) – Greater Magadha
"""

# ==============================
# TOTALS
# ==============================

def calculate_totals(row_data: dict) -> dict:
    d1 = sum(row_data[f"D1_SM_{k}"] for k in [
        "OccupationalMobility", "StatusFluidity", "InstitutionalMobility",
        "IntergroupTransferability", "MeritocraticPathways"
    ])
    d2 = sum(row_data[f"D2_ED_{k}"] for k in [
        "KnowledgeGatekeeping", "LanguageOfTransmission", "EducationalInfrastructure",
        "PedagogicalInclusivity", "IntellectualPluralism"
    ])
    d3 = sum(row_data[f"D3_EC_{k}"] for k in [
        "OccupationalPlurality", "GuildMarketAccessibility", "InternalMarketIntegration",
        "ExternalTradeLinkages", "StateRedistributionWelfare"
    ])
    d4 = sum(row_data[f"D4_PO_{k}"] for k in [
        "AdminIntegration", "SuccessionStability", "TerritorialContinuity",
        "ConflictManagement", "DiplomaticStability"
    ])
    d5 = sum(row_data[f"D5_CU_{k}"] for k in [
        "FreedomOfWorship", "RitualInclusivity", "SocialContactNorms",
        "SyncretismHybridization", "NormativeHierarchyVsEquality"
    ])
    row_data["D1_Total"] = d1
    row_data["D2_Total"] = d2
    row_data["D3_Total"] = d3
    row_data["D4_Total"] = d4
    row_data["D5_Total"] = d5
    row_data["CCSI_Total"] = d1 + d2 + d3 + d4 + d5
    return row_data

# ==============================
# PROCESS ONE REGION–ERA
# ==============================

def process_region_era(region: str, era: str) -> dict:
    """Process one region–era: call Gemini, parse scores, notes, sources."""
    log_message(f"Processing {region} - {era}")
    start_year, end_year = get_era_years(era)

    # Build full prompt for this era–region
    full_prompt = GEMINI_FULL_PROMPT.format(
        era=era,
        region=region,
        start_year=start_year,
        end_year=end_year,
    )

    # Call Gemini once
    reply = call_gemini(full_prompt)
    time.sleep(1.5)

    # Ensure we have a string to work with
    raw_reply = reply if isinstance(reply, str) else str(reply)

    # Expect final line like: scores_csv|notes|sources_list
    try:
        # Split into lines, drop empty ones
        lines = [ln.strip() for ln in raw_reply.splitlines() if ln.strip()]
        if not lines:
            raise ValueError(f"No non-empty lines in reply: {raw_reply}")

        # Take only the last non-empty line (Gemini may add explanations or headers)
        last_line = lines[-1]

        parts = last_line.split("|")
        if len(parts) != 3:
            raise ValueError(
                f"Expected 3 parts (scores|notes|sources), got {len(parts)}: {last_line}"
            )

        scores_str, notes, sources = parts
        scores = [int(x.strip()) for x in scores_str.split(",")]
        if len(scores) != 25:
            raise ValueError(
                f"Expected 25 scores, got {len(scores)}: {scores_str}"
            )

    except Exception as e:
        log_message(f"Parse error for {region}-{era}: {e} | raw reply: {raw_reply}")
        scores = [0] * 25
        notes = "Parsing failed; placeholder summary."
        sources = "Parsing failed; placeholder sources."

    # Build row data
    row_data = {
        "Era_ID": era,
        "Era_Start_Year": start_year,
        "Era_End_Year": end_year,
        "Region": region,
    }

    indicators = [
        "D1_SM_OccupationalMobility", "D1_SM_StatusFluidity", "D1_SM_InstitutionalMobility",
        "D1_SM_IntergroupTransferability", "D1_SM_MeritocraticPathways",
        "D2_ED_KnowledgeGatekeeping", "D2_ED_LanguageOfTransmission", "D2_ED_EducationalInfrastructure",
        "D2_ED_PedagogicalInclusivity", "D2_ED_IntellectualPluralism",
        "D3_EC_OccupationalPlurality", "D3_EC_GuildMarketAccessibility", "D3_EC_InternalMarketIntegration",
        "D3_EC_ExternalTradeLinkages", "D3_EC_StateRedistributionWelfare",
        "D4_PO_AdminIntegration", "D4_PO_SuccessionStability", "D4_PO_TerritorialContinuity",
        "D4_PO_ConflictManagement", "D4_PO_DiplomaticStability",
        "D5_CU_FreedomOfWorship", "D5_CU_RitualInclusivity", "D5_CU_SocialContactNorms",
        "D5_CU_SyncretismHybridization", "D5_CU_NormativeHierarchyVsEquality",
    ]

    for i, ind in enumerate(indicators):
        row_data[ind] = scores[i]

    # Compute totals
    row_data = calculate_totals(row_data)

    # Clean up notes & sources text
    row_data["Notes"] = notes.strip().replace("\n", " ")
    row_data["Sources_List"] = sources.strip().replace("\n", " ")

    return row_data


# ==============================
# MAIN LOOP
# ==============================

def is_row_completed(df: pd.DataFrame, region: str, era: str) -> bool:
    if df.empty:
        return False
    return not df[(df["Region"] == region) & (df["Era_ID"] == era)].empty

def main():
    print("Starting CCSI dataset generation (Gemini-only)...")
    log_message("=== CCSI (Gemini-only) Dataset Generation Started ===")
    create_output_directory()
    df = load_existing_dataset()
    processed = 0

    for region, eras in REGIONS.items():
        for era in eras:
            if is_row_completed(df, region, era):
                log_message(f"Skipping {region} - {era} (exists)")
                continue
            try:
                row = process_region_era(region, era)
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_dataset(df)
                processed += 1
                print(f"Completed {processed}: {region} - {era}")
            except Exception as e:
                log_message(f"Error on {region}-{era}: {e}")
                continue

    save_dataset(df)
    log_message("=== CCSI (Gemini-only) dataset generation completed ===")
    print("=== CCSI (Gemini-only) dataset generation completed ===")

if __name__ == "__main__":
    main()
