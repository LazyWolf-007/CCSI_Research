print(">>> PATCH SCRIPT HAS STARTED <<<")

import os
import json
import time
import math
import pandas as pd
import requests

# =============== CONFIG ===================

# <-- PUT YOUR GEMINI API KEY HERE -->
GEMINI_API_KEY = "AIzaSyDiox4aEL1F0lPBtkZDLGV6Lffae8gq-f0"

INPUT_FILE  = "CCSI_Dataset.xlsx"
OUTPUT_FILE = "CCSI_Dataset_FIXED.xlsx"

MODEL_NAME = "gemini-2.0-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
)

# Indicator columns in exact dataset order
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

# ================= UTILS ==================

def row_needs_fix(row):
    """Return True if row is obviously a failed/empty row."""
    # Check for "Parsing failed" in notes or sources
    notes = str(row.get(NOTE_COL, ""))
    srcs  = str(row.get(SRC_COL, ""))
    if "Parsing failed" in notes or "Parsing failed" in srcs:
        return True

    # Check if all indicators are zero or NaN
    zeros = True
    for col in INDICATOR_COLS:
        val = row.get(col, 0)
        if pd.notna(val) and float(val) != 0.0:
            zeros = False
            break
    return zeros


def era_number(era_id):
    """Convert 'E07' -> 7 (for sorting / neighbour search)."""
    try:
        return int(str(era_id).replace("E", "").strip())
    except Exception:
        return None


def interpolate_baseline(df, idx):
    """
    Build baseline scores for a failed row by:
    - weighting previous and next era in same region (0.4 + 0.4)
    - adding average of same era across other regions (0.2)
    """
    row = df.loc[idx]
    region = row["Region"]
    era_id = row["Era_ID"]
    e_num  = era_number(era_id)

    # Find previous and next era rows in same region
    same_region = df[df["Region"] == region].copy()
    same_region["EraNum"] = same_region["Era_ID"].apply(era_number)

    prev_rows = same_region[same_region["EraNum"] < e_num]
    next_rows = same_region[same_region["EraNum"] > e_num]

    prev_row = prev_rows.sort_values("EraNum").iloc[-1] if not prev_rows.empty else None
    next_row = next_rows.sort_values("EraNum").iloc[0]  if not next_rows.empty else None

    # Same-era rows in *other* regions
    others = df[df["Region"] != region].copy()
    others["EraNum"] = others["Era_ID"].apply(era_number)
    same_era_others = others[others["EraNum"] == e_num]

    baseline = {col: 0.0 for col in INDICATOR_COLS}
    weight_sum = 0.0

    def add_source(r, weight):
        nonlocal baseline, weight_sum
        if r is None:
            return
        for c in INDICATOR_COLS:
            val = r.get(c, 0)
            if pd.isna(val):
                val = 0
            baseline[c] += float(val) * weight
        weight_sum += weight

    # weights: 0.4 prev, 0.4 next, 0.2 avg others
    add_source(prev_row, 0.4)
    add_source(next_row, 0.4)

    if not same_era_others.empty:
        mean_others = same_era_others[INDICATOR_COLS].mean()
        temp_row = {c: mean_others[c] for c in INDICATOR_COLS}
        add_source(temp_row, 0.2)

    # If we somehow have no neighbours at all, fall back to zeros (Gemini will handle)
    if weight_sum == 0:
        return [0] * len(INDICATOR_COLS)

    # Normalize
    for c in INDICATOR_COLS:
        baseline[c] /= weight_sum

    # Round to nearest 0–4 integer but keep range in [0,4]
    baseline_scores = []
    for c in INDICATOR_COLS:
        val = baseline[c]
        val = max(0, min(4, round(val)))
        baseline_scores.append(int(val))

    return baseline_scores


def build_gemini_prompt(row, baseline_scores):
    """
    Build the structured instruction for Gemini.
    We ask for strict JSON output with scores, notes, sources.
    """
    era_id = row["Era_ID"]
    region = row["Region"]
    start_year = row["Era_Start_Year"]
    end_year   = row["Era_End_Year"]

    baseline_dict = {
        name: baseline_scores[i] for i, name in enumerate(INDICATOR_COLS)
    }

    prompt = f"""
You are an expert historian of the Indian subcontinent.

I am constructing a time–series dataset called the Civilizational Cohesion and Social Inclusivity Index (CCSI).
Each row describes one time period ("era") in one region of India and scores 25 indicators (0–4) across 5 dimensions:

D1 = Social Mobility (5 indicators)
D2 = Education & Knowledge Regime (5 indicators)
D3 = Economic Structure (5 indicators)
D4 = Polity & State Cohesion (5 indicators)
D5 = Culture, Religion & Hierarchy (5 indicators)

The row that needs to be filled is:

- Era_ID: {era_id}
- Region: {region}
- Period: {start_year} to {end_year} CE (negative = BCE)

You are given a baseline estimate for the 25 indicators, derived by interpolation from neighbouring eras in the same region
and same-era scores in other regions:

BASELINE_SCORES (indicator_name: baseline_integer_0_to_4):
{json.dumps(baseline_dict, indent=2)}

TASK:
1. Using your knowledge of Indian history AND the baseline, adjust the integer scores (0–4) so they are historically plausible and smoothly consistent with neighbouring eras.
2. Write a brief but academic note (3–5 sentences) describing the social structure, inclusivity, economy, political cohesion and cultural patterns in this era and region.
   - Tone: academic, but clear and narrative (not too dry).
3. Provide 6–12 key scholarly sources (books or peer-reviewed articles) relevant for this era and region.
   - Use full references: Author, Initials. (Year). Title. Publisher or journal.
   - No Wikipedia or non-scholarly blogs.

OUTPUT FORMAT:
Return ONLY valid JSON with this exact structure (no prose, no backticks):

{{
  "scores": [25 integers between 0 and 4, in this exact order:
    "{INDICATOR_COLS[0]}", "{INDICATOR_COLS[1]}", "{INDICATOR_COLS[2]}", "{INDICATOR_COLS[3]}", "{INDICATOR_COLS[4]}",
    "{INDICATOR_COLS[5]}", "{INDICATOR_COLS[6]}", "{INDICATOR_COLS[7]}", "{INDICATOR_COLS[8]}", "{INDICATOR_COLS[9]}",
    "{INDICATOR_COLS[10]}", "{INDICATOR_COLS[11]}", "{INDICATOR_COLS[12]}", "{INDICATOR_COLS[13]}", "{INDICATOR_COLS[14]}",
    "{INDICATOR_COLS[15]}", "{INDICATOR_COLS[16]}", "{INDICATOR_COLS[17]}", "{INDICATOR_COLS[18]}", "{INDICATOR_COLS[19]}",
    "{INDICATOR_COLS[20]}", "{INDICATOR_COLS[21]}", "{INDICATOR_COLS[22]}", "{INDICATOR_COLS[23]}", "{INDICATOR_COLS[24]}"
  ],
  "notes": "One concise academic paragraph (3–5 sentences).",
  "sources": [
    "Full reference 1",
    "Full reference 2",
    "... up to 12 items"
  ]
}}

Remember: respond with JSON only.
"""
    return prompt


def call_gemini(prompt, max_retries=3):
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

            # Strip code fences if Gemini wraps JSON in ```json ... ```
            text = text.strip()
            if text.startswith("```"):
                text = text.strip("`")
                # remove possible leading json\n
                if text.lower().startswith("json"):
                    text = text[4:].strip()

            parsed = json.loads(text)

            scores = parsed.get("scores", [])
            notes  = parsed.get("notes", "").strip()
            sources_list = parsed.get("sources", [])

            # Basic validation
            if len(scores) != len(INDICATOR_COLS):
                raise ValueError(f"Expected {len(INDICATOR_COLS)} scores, got {len(scores)}")
            scores_int = [int(round(float(s))) for s in scores]

            if not notes or len(notes) < 80:
                raise ValueError("Notes too short")

            if not isinstance(sources_list, list) or len(sources_list) < 3:
                raise ValueError("Too few sources")

            return scores_int, notes, "; ".join([s.strip() for s in sources_list])

        except Exception as e:
            print(f"[Gemini attempt {attempt}] Error: {e}")
            if attempt == max_retries:
                print("  -> Giving up on Gemini for this row; using baseline scores and placeholder text.")
                return None, None, None
            time.sleep(2 * attempt)  # backoff


def recompute_totals(df):
    """Recalculate D1–D5 totals and CCSI_Total for all rows."""
    # D1: indicators 0–4
    df["D1_Total"] = df[INDICATOR_COLS[0:5]].sum(axis=1)
    # D2: 5–9
    df["D2_Total"] = df[INDICATOR_COLS[5:10]].sum(axis=1)
    # D3: 10–14
    df["D3_Total"] = df[INDICATOR_COLS[10:15]].sum(axis=1)
    # D4: 15–19
    df["D4_Total"] = df[INDICATOR_COLS[15:20]].sum(axis=1)
    # D5: 20–24
    df["D5_Total"] = df[INDICATOR_COLS[20:25]].sum(axis=1)

    df["CCSI_Total"] = (
        df["D1_Total"]
        + df["D2_Total"]
        + df["D3_Total"]
        + df["D4_Total"]
        + df["D5_Total"]
    )
    return df


def main():
    if GEMINI_API_KEY == "YOUR_GEMINI_KEY_HERE":
        print("ERROR: Please set your GEMINI_API_KEY at the top of the script.")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Input file '{INPUT_FILE}' not found in current directory.")
        return

    print(f"Loading dataset from '{INPUT_FILE}' ...")
    df = pd.read_excel(INPUT_FILE)

    # Identify rows needing fix
    need_fix_idx = [idx for idx, row in df.iterrows() if row_needs_fix(row)]
    print(f"Found {len(need_fix_idx)} rows that need repair.")

    for idx in need_fix_idx:
        row = df.loc[idx]
        era_id = row["Era_ID"]
        region = row["Region"]
        print(f"\n=== Repairing row index {idx} | Era {era_id} | Region {region} ===")

        baseline_scores = interpolate_baseline(df, idx)
        print("Baseline scores:", baseline_scores)

        prompt = build_gemini_prompt(row, baseline_scores)
        scores_int, notes, sources_str = call_gemini(prompt)

        if scores_int is None:
            # Fallback: keep baseline scores, basic placeholders
            scores_int = baseline_scores
            notes = "Automatically interpolated row; Gemini JSON parsing failed after retries."
            sources_str = "Interpolated from neighbouring eras and regions; see surrounding Sources_List entries."

        # Write scores into row
        for col, val in zip(INDICATOR_COLS, scores_int):
            df.at[idx, col] = int(val)

        df.at[idx, NOTE_COL] = notes
        df.at[idx, SRC_COL]  = sources_str

    # Recompute totals for all rows
    df = recompute_totals(df)

    # Save new fixed file
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned dataset to '{OUTPUT_FILE}'")

    # Also save as CSV if you want
    csv_out = OUTPUT_FILE.replace(".xlsx", ".csv")
    df.to_csv(csv_out, index=False)
    print(f"Also saved CSV to '{csv_out}'")

    print("\nPatch complete. You can now use CCSI_Dataset_FIXED.* for analysis.")


if __name__ == "__main__":
    main()
