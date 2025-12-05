import os
import pandas as pd
import matplotlib.pyplot as plt

# ----------------- CONFIG -----------------
DATA_FILE = os.path.join("output", "CCSI_Dataset_FINAL.xlsx")
FIG_DIR   = "figures"

REGION_COL = "Region"
ERA_ID_COL = "Era_ID"
ERA_NUM_COL = "Era_Num"
CCSI_COL = "CCSI_Total"

DIM_COLS = ["D1_Total", "D2_Total", "D3_Total", "D4_Total", "D5_Total"]


# --------------- LOADING ------------------

def load_dataset():
    """Load dataset and enforce numeric Era ordering (always recompute Era_Num)."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Could not find dataset at: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE)

    # ALWAYS recompute Era_Num from Era_ID, ignore whatever is in the file
    def era_to_num(eid):
        try:
            return int(str(eid).replace("E", "").strip())
        except Exception:
            return None

    df[ERA_NUM_COL] = df[ERA_ID_COL].apply(era_to_num)

    # quick sanity print (optional – you can delete later)
    print(df[[ERA_ID_COL, ERA_NUM_COL]].drop_duplicates().sort_values(ERA_NUM_COL).head(10))

    # sort by Region then Era_Num
    df = df.sort_values([REGION_COL, ERA_NUM_COL]).reset_index(drop=True)
    return df



def ensure_fig_dir():
    if not os.path.exists(FIG_DIR):
        os.makedirs(FIG_DIR)


# --------------- PLOTS --------------------

def plot_region_ccsi(df, region):
    """Single region timeline (e.g. Gangetic North)."""
    sub = df[df[REGION_COL] == region].sort_values(ERA_NUM_COL)

    plt.figure(figsize=(12, 5))
    plt.plot(sub[ERA_NUM_COL], sub[CCSI_COL], marker="o", label=f"{region} CCSI")

    # axis ticks: E01...E28
    xticks = sub[ERA_NUM_COL].tolist()
    xlabels = [f"E{int(e):02d}" for e in xticks]
    plt.xticks(xticks, xlabels, rotation=45)

    plt.xlabel("Era")
    plt.ylabel("CCSI_Total")
    plt.title(f"CCSI over Time – {region}")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    fname = os.path.join(FIG_DIR, f"ccsi_timeline_{region.replace(' ', '_').replace('–','-')}.png")
    plt.savefig(fname, dpi=300)
    plt.close()
    print(f"[OK] Saved regional CCSI plot for {region} -> {fname}")


def plot_all_regions_ccsi(df):
    """All regions on one correctly ordered timeline."""
    plt.figure(figsize=(14, 6))

    regions = sorted(df[REGION_COL].unique())
    all_eras = sorted(df[ERA_NUM_COL].dropna().unique())

    for region in regions:
        sub = df[df[REGION_COL] == region].sort_values(ERA_NUM_COL)
        plt.plot(sub[ERA_NUM_COL], sub[CCSI_COL], marker="o", label=region)

    # force full E01–E28 axis
    xticks = all_eras
    xlabels = [f"E{int(e):02d}" for e in xticks]
    plt.xticks(xticks, xlabels, rotation=45)

    plt.xlabel("Era")
    plt.ylabel("CCSI_Total")
    plt.title("CCSI over Time – All Regions")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    fname = os.path.join(FIG_DIR, "ccsi_all_regions_comparison.png")
    plt.savefig(fname, dpi=300)
    plt.close()
    print(f"[OK] Saved all-regions CCSI plot -> {fname}")


def plot_region_dim_heatmap(df, region):
    """Heatmap of D1–D5 for one region."""
    sub = df[df[REGION_COL] == region].sort_values(ERA_NUM_COL)

    data = sub[DIM_COLS].values
    eras = [f"E{int(e):02d}" for e in sub[ERA_NUM_COL].tolist()]

    plt.figure(figsize=(8, 10))
    plt.imshow(data, aspect="auto", cmap="viridis", origin="upper")
    plt.colorbar(label="Score")
    plt.yticks(range(len(eras)), eras)
    plt.xticks(range(len(DIM_COLS)), DIM_COLS, rotation=45)

    plt.title(f"D1–D5 Dimension Heatmap – {region}")
    plt.tight_layout()

    fname = os.path.join(FIG_DIR, f"dimensions_heatmap_{region.replace(' ', '_').replace('–','-')}.png")
    plt.savefig(fname, dpi=300)
    plt.close()
    print(f"[OK] Saved dimension heatmap for {region} -> {fname}")

def plot_timeline_all_regions(df):
    """
    Plot CCSI over time for all regions on a single timeline.
    Uses Era_Num for proper ordering and labels x-axis as E01..E28.
    """
    plt.figure(figsize=(18, 6))

    region_col = "Region"
    era_num_col = "Era_Num"
    ccsi_col = "CCSI_Total"

    regions = sorted(df[region_col].unique())
    all_eras = sorted(df[era_num_col].dropna().unique())

    for region in regions:
        sub = df[df[region_col] == region].sort_values(era_num_col)
        plt.plot(
            sub[era_num_col],
            sub[ccsi_col],
            marker="o",
            linewidth=2,
            label=region,
        )

    # Nice, ordered era labels
    xticks = all_eras
    xlabels = [f"E{int(e):02d}" for e in all_eras]
    plt.xticks(xticks, xlabels, rotation=45)

    plt.title("CCSI Evolution Over Time Across All Regions", fontsize=16)
    plt.xlabel("Era", fontsize=13)
    plt.ylabel("CCSI_Total", fontsize=13)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "ccsi_timeline_all_regions.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved timeline of all regions -> {out_path}")




# --------------- MAIN ---------------------

def main():
    print(">>")
    print("=== CCSI Step 1: Exploratory Visualizations (fixed ordering) ===")
    ensure_fig_dir()

    df = load_dataset()
    print(f"Loaded {len(df)} rows.")

    # Choose one key region for focused plots
    focus_region = "Gangetic North"
    if focus_region not in df[REGION_COL].unique():
        focus_region = sorted(df[REGION_COL].unique())[0]

    plot_region_ccsi(df, focus_region)
    plot_all_regions_ccsi(df)
    plot_region_dim_heatmap(df, focus_region)
    plot_timeline_all_regions(df)



if __name__ == "__main__":
    main()
