import os
import json
import time
import pandas as pd
import requests

# ================== CONFIG ======================

# !!! PUT YOUR GEMINI KEY HERE !!!
GEMINI_API_KEY = "AIzaSyDiox4aEL1F0lPBtkZDLGV6Lffae8gq-f0"

BASE_FILE   = os.path.join("output", "CCSI_Dataset_FINAL.xlsx")
OUTPUT_FILE = os.path.join("output", "CCSI_Dataset_WITH_MODERN.xlsx")

MODEL_NAME = "gemini-2.0-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
)

# 5 modern 5-year eras
MODERN_ERAS = [
    ("M01", 2000, 2005),
    ("M02", 2005, 2010),
    ("M03", 2010, 2015),
    ("M04", 2015, 2020),
    ("M05", 2020, 2025),
]

# Modern regions (7 macro-regions + West Bengal as separate)
MODERN_REGIONS = [
    "Gangetic North",
    "Northwest (Punjab–Gandhāra)",
    "Western India",
    "Central India",
    "Deccan",
    "Tamilakam",
    "Northeast",
    "West Bengal",        # modern-only
    "Jammu & Kashmir",    # modern-only
]


# Indicator columns in EXACT dataset order
INDICATOR_COLS = [
    "D1_SM_OccupationalMobility",
    "D1_SM_StatusFluidity",
    "D1_SM_InstitutionalMobility",
    "D1_SM_IntergroupTransferability",
    "D1_SM_MeritocraticPathways",
    "D2_ED_KnowledgeGatekeeping",
    "D2_ED_LanguageOfTransmission",
    "D2_ED_EducationalInfrastructure",
    "D2_ED_PedagogicalInclusivity",
    "D2_ED_IntellectualPluralism",
    "D3_EC_OccupationalPlurality",
    "D3_EC_GuildMarketAccessibility",
    "D3_EC_InternalMarketIntegration",
    "D3_EC_ExternalTradeLinkages",
    "D3_EC_StateRedistributionWelfare",
    "D4_PO_AdminIntegration",
    "D4_PO_SuccessionStability",
    "D4_PO_TerritorialContinuity",
    "D4_PO_ConflictManagement",
    "D4_PO_DiplomaticStability",
    "D5_CU_FreedomOfWorship",
    "D5_CU_RitualInclusivity",
    "D5_CU_SocialContactNorms",
    "D5_CU_SyncretismHybridization",
    "D5_CU_NormativeHierarchyVsEquality",
]

TOTAL_COLS = [
    "D1_Total",
    "D2_Total",
    "D3_Total",
    "D4_Total",
    "D5_Total",
    "CCSI_Total",
]

NOTE_COL = "Notes"
SRC_COL  = "Sources_List"

# If you added this earlier:
INTERPOLATED_COL = "Interpolated"  # will set 0 for modern rows


# =============== UTILS ===================

def recompute_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Recalculate D1–D5 totals and CCSI_Total for all rows."""
    df["D1_Total"] = df[INDICATOR_COLS[0:5]].sum(axis=1)
    df["D2_Total"] = df[INDICATOR_COLS[5:10]].sum(axis=1)
    df["D3_Total"] = df[INDICATOR_COLS[10:15]].sum(axis=1)
    df["D4_Total"] = df[INDICATOR_COLS[15:20]].sum(axis=1)
    df["D5_Total"] = df[INDICATOR_COLS[20:25]].sum(axis=1)

    df["CCSI_Total"] = (
        df["D1_Total"]
        + df["D2_Total"]
        + df["D3_Total"]
        + df["D4_Total"]
        + df["D5_Total"]
    )
    return df


def row_exists(df: pd.DataFrame, era_id: str, region: str) -> bool:
    """Check if a row for (Era_ID, Region) already exists."""
    mask = (df["Era_ID"] == era_id) & (df["Region"] == region)
    return mask.any()


def build_gemini_prompt_modern(region: str, era_id: str, start_year: int, end_year: int) -> str:
    """
    Build the modern-era prompt for Gemini.
    Explicitly mention political polarization as a factor for cohesion,
    especially relevant for some regions (including West Bengal).
    """
    prompt = f"""
You are a socio-historical analyst and political sociologist.

We are building a modern extension (2000–2025) of a long-run dataset called the
Civilizational Cohesion and Social Inclusivity Index (CCSI) for the Indian subcontinent.

Each row describes one time-slice (5 years) in one region of India and scores
25 indicators (0–4) across 5 dimensions:

D1 — Social Mobility (5 indicators)
D2 — Education & Knowledge Regime (5 indicators)
D3 — Economic Structure (5 indicators)
D4 — Polity, Governance & Cohesion (5 indicators)
D5 — Culture, Religion & Hierarchy (5 indicators)

The row you must fill is:

- Era_ID: {era_id}
- Region: {region}
- Period: {start_year}–{end_year}

The scale for all 25 indicators is:
0 = Absent / extremely weak
1 = Very weak
2 = Moderate
3 = Strong
4 = Very strong / dominant feature

For the modern period, interpret the 25 indicators using contemporary proxies, for example:

D1 (Social Mobility)
- OccupationalMobility: income and job mobility, opportunities across classes and caste.
- StatusFluidity: permeability of caste, class, gender, and community boundaries.
- InstitutionalMobility: access to elite education, bureaucracy, and formal sectors.
- IntergroupTransferability: movement across caste, religious, linguistic, or regional lines.
- MeritocraticPathways: how far merit-based selection actually operates vs birth, networks, money.

D2 (Education & Knowledge Regime)
- KnowledgeGatekeeping: who controls elite knowledge (state, private, caste, language).
- LanguageOfTransmission: English vs regional language vs local dialect in higher education and state.
- EducationalInfrastructure: spread and quality of schools, colleges, digital access.
- PedagogicalInclusivity: access for poor, lower castes, minorities, women, rural areas.
- IntellectualPluralism: freedom for critical thought, dissent, non-majority narratives.

D3 (Economic Structure)
- OccupationalPlurality: diversity of sectors (agriculture, manufacturing, services, IT, informal work).
- GuildMarketAccessibility: access to markets, networks, and credit for small producers and informal workers.
- InternalMarketIntegration: integration with national markets, transport, logistics, inter-state trade.
- ExternalTradeLinkages: role in exports, FDI, global value chains.
- StateRedistributionWelfare: coverage and effectiveness of welfare (PDS, MGNREGA, DBT, health, etc.).

D4 (Polity & Governance)
- AdminIntegration: state capacity, bureaucratic reach, basic service delivery.
- SuccessionStability: stability of governments and ruling coalitions.
- TerritorialContinuity: absence of secessionist movements or chronic regional insurgency.
- ConflictManagement: ability to manage protests, communal tensions, and economic shocks.
- DiplomaticStability: relations with neighbouring regions and central government, federal friction.

D5 (Culture, Religion & Hierarchy)
- FreedomOfWorship: practical religious freedom for major and minor communities.
- RitualInclusivity: participation of different castes and communities in public rituals and ceremonies.
- SocialContactNorms: everyday inter-dining, inter-mixing, inter-marriage, and social trust.
- SyncretismHybridization: pluralistic cultural mixing vs hardened boundaries.
- NormativeHierarchyVsEquality: dominance of caste/religious hierarchy vs egalitarian norms.

IMPORTANT ABOUT POLARIZATION:
- If this region and period is marked by strong political or communal polarization,
  this should LOWER relevant indicators in:
  - D4 (Cohesion & ConflictManagement)
  - D5 (SocialContactNorms, FreedomOfWorship, NormativeHierarchyVsEquality)
  - sometimes D1 (StatusFluidity, IntergroupTransferability).
- Do NOT take sides. Just treat polarization as a factor that reduces cohesion.

You may assume that:
- 2000–2005: liberalization effects, IT growth, but uneven inclusion.
- 2005–2015: rapid growth + welfare expansion + rising identity politics.
- 2015–2025: stronger centralization, sharper ideological battles, digital penetration, visible polarization in some spaces.

TASK:
1. Assign 25 integer scores between 0 and 4 for this region and period.
2. Write a 3–6 sentence academic note summarizing:
   - social mobility and inclusion,
   - education and knowledge control,
   - economic structure and vulnerability,
   - political cohesion vs polarization,
   - cultural pluralism vs hardened hierarchy.
3. Suggest 6–12 key scholarly or official sources relevant to this region and time:
   - Examples: NSSO/PLFS reports, NFHS, Census, CSDS, well-known books or papers.
   - No Wikipedia or casual blogs.

OUTPUT FORMAT:
Return ONLY valid JSON with EXACTLY this structure (no prose outside JSON, no backticks):

{{
  "scores": [25 integers between 0 and 4, in this exact order:
    "{INDICATOR_COLS[0]}", "{INDICATOR_COLS[1]}", "{INDICATOR_COLS[2]}", "{INDICATOR_COLS[3]}", "{INDICATOR_COLS[4]}",
    "{INDICATOR_COLS[5]}", "{INDICATOR_COLS[6]}", "{INDICATOR_COLS[7]}", "{INDICATOR_COLS[8]}", "{INDICATOR_COLS[9]}",
    "{INDICATOR_COLS[10]}", "{INDICATOR_COLS[11]}", "{INDICATOR_COLS[12]}", "{INDICATOR_COLS[13]}", "{INDICATOR_COLS[14]}",
    "{INDICATOR_COLS[15]}", "{INDICATOR_COLS[16]}", "{INDICATOR_COLS[17]}", "{INDICATOR_COLS[18]}", "{INDICATOR_COLS[19]}",
    "{INDICATOR_COLS[20]}", "{INDICATOR_COLS[21]}", "{INDICATOR_COLS[22]}", "{INDICATOR_COLS[23]}", "{INDICATOR_COLS[24]}"
  ],
  "notes": "One concise academic paragraph (3–6 sentences).",
  "sources": [
    "Full reference 1",
    "Full reference 2",
    "... up to around 10 items"
  ]
}}
"""
    return prompt


def call_gemini(prompt: str, max_retries: int = 3):
    """Call Gemini API and parse the JSON response."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()

            text = data["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip()

            # Strip ```json ... ``` fences if present
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:].strip()

            parsed = json.loads(text)

            scores = parsed.get("scores", [])
            notes  = parsed.get("notes", "").strip()
            sources_list = parsed.get("sources", [])

            if len(scores) != len(INDICATOR_COLS):
                raise ValueError(f"Expected {len(INDICATOR_COLS)} scores, got {len(scores)}")

            scores_int = [int(round(float(s))) for s in scores]

            if not notes or len(notes) < 60:
                raise ValueError("Notes too short")

            if not isinstance(sources_list, list) or len(sources_list) < 3:
                raise ValueError("Too few sources")

            sources_str = "; ".join(s.strip() for s in sources_list)
            return scores_int, notes, sources_str

        except Exception as e:
            print(f"[Gemini attempt {attempt}] Error: {e}")
            if attempt == max_retries:
                print("  -> Giving up on Gemini for this row, using simple fallback scores.")
                return None, None, None
            time.sleep(2 * attempt)


# ================= MAIN =====================

def main():
    if GEMINI_API_KEY == "YOUR_GEMINI_KEY_HERE":
        print("ERROR: Please set your GEMINI_API_KEY at the top of the script.")
        return

    if not os.path.exists(BASE_FILE):
        print(f"ERROR: Base dataset '{BASE_FILE}' not found.")
        return

    print("=== CCSI Modern Extension: 2000–2025 for All Regions + West Bengal ===")
    print(f"Loading base dataset from: {BASE_FILE}")
    df = pd.read_excel(BASE_FILE)

    # If 'Interpolated' column exists, fine; if not, create it with 0
    if INTERPOLATED_COL not in df.columns:
        df[INTERPOLATED_COL] = 0

    added_rows = 0

    for era_id, start_year, end_year in MODERN_ERAS:
        for region in MODERN_REGIONS:
            if row_exists(df, era_id, region):
                print(f"Skipping {region} {era_id} (already exists).")
                continue

            print(f"\n=== Generating modern row: {region} | {era_id} ({start_year}-{end_year}) ===")
            prompt = build_gemini_prompt_modern(region, era_id, start_year, end_year)
            scores_int, notes, sources_str = call_gemini(prompt)

            if scores_int is None:
                # Basic neutral fallback: all 2 (moderate)
                scores_int = [2] * len(INDICATOR_COLS)
                notes = (
                    "Fallback: scores set to moderate (2) for all indicators; "
                    "Gemini JSON parsing failed after retries."
                )
                sources_str = (
                    "Fallback: generic reference to Census of India, NSSO/PLFS, NFHS, "
                    "and state development reports."
                )

            # Build new row
            row_data = {
                "Era_ID": era_id,
                "Era_Start_Year": start_year,
                "Era_End_Year": end_year,
                "Region": region,
            }

            for col, val in zip(INDICATOR_COLS, scores_int):
                row_data[col] = int(val)

            row_data[INTERPOLATED_COL] = 0  # this row comes directly from Gemini

            row_data[NOTE_COL] = notes
            row_data[SRC_COL]  = sources_str

            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
            added_rows += 1

            # Gentle delay to be nice to API
            time.sleep(1.5)

    print(f"\nAdded {added_rows} modern rows in total.")
    print("Recomputing totals for all rows...")
    df = recompute_totals(df)

    print(f"Saving updated dataset to: {OUTPUT_FILE}")
    df.to_excel(OUTPUT_FILE, index=False)

    csv_out = OUTPUT_FILE.replace(".xlsx", ".csv")
    df.to_csv(csv_out, index=False)
    print(f"Also saved CSV to: {csv_out}")

    print("\n=== Modern extension complete. You can now use CCSI_Dataset_WITH_MODERN.* for ML and analysis. ===")


if __name__ == "__main__":
    main()
