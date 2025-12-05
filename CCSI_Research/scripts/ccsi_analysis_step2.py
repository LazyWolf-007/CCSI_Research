"""
ccsi_analysis_step2.py

Step 2: Deeper statistical / ML analysis on the final CCSI dataset.

Outputs (saved under figures/):

1. ccsi_rolling_means_regions.png
   - 3-era rolling average of CCSI_Total for each region
2. pca_d1_d5_scatter.png
   - PCA of D1–D5 totals (all rows), colored by region
3. kmeans_clusters_d1_d5.png
   - K-means clusters in the same PCA space

Dataset used: output/CCSI_Dataset_FINAL.xlsx
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# ---------- CONFIG ----------

DATA_FILE = os.path.join("output", "CCSI_Dataset_FINAL.xlsx")
FIG_DIR = "figures"

REGION_COL = "Region"
ERA_COL = "Era_ID"
ERA_NUM_COL = "Era_Num"

D_TOTAL_COLS = ["D1_Total", "D2_Total", "D3_Total", "D4_Total", "D5_Total"]
CCSI_COL = "CCSI_Total"


# ---------- HELPERS ----------

def ensure_fig_dir():
    if not os.path.exists(FIG_DIR):
        os.makedirs(FIG_DIR)


def load_dataset():
    """Load and consistently sort the final CCSI dataset."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Could not find dataset at: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE)

    # robust Era sorting
    def era_to_num(eid):
        try:
            return int(str(eid).replace("E", "").strip())
        except Exception:
            return None

    df[ERA_NUM_COL] = df[ERA_COL].apply(era_to_num)

    # Sort by Region then Era_Num
    df = df.sort_values([REGION_COL, ERA_NUM_COL]).reset_index(drop=True)

    # small sanity check
    if df[ERA_NUM_COL].isna().any():
        print("[WARN] Some Era_Num values are NaN – please check Era_ID formatting.")

    return df


# ---------- 1. Rolling averages of CCSI ----------

def plot_rolling_means(df, window=3):
    """
    Plot 3-era rolling average of CCSI_Total for each region.
    Uses Era_Num as the common x-axis so eras line up correctly.
    """
    plt.figure(figsize=(14, 6))

    regions = sorted(df[REGION_COL].unique())

    for region in regions:
        sub = df[df[REGION_COL] == region].sort_values(ERA_NUM_COL)
        sub = sub[[ERA_COL, ERA_NUM_COL, CCSI_COL]].copy()
        sub["CCSI_roll"] = sub[CCSI_COL].rolling(window=window, min_periods=1).mean()

        # Use Era_Num on x-axis (shared across regions)
        plt.plot(
            sub[ERA_NUM_COL],
            sub["CCSI_roll"],
            marker="o",
            label=region,
        )

    # Build global era tick positions and labels
    all_era_nums = sorted(df[ERA_NUM_COL].dropna().unique())
    xticks = all_era_nums
    xlabels = [f"E{int(n):02d}" for n in all_era_nums]

    plt.xticks(xticks, xlabels, rotation=45)

    plt.title(f"{window}-Era Rolling Average of CCSI_Total – All Regions", fontsize=14)
    plt.xlabel("Era", fontsize=12)
    plt.ylabel("Rolling CCSI_Total", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "ccsi_rolling_means_regions.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved rolling means plot -> {out_path}")



# ---------- 2. PCA on D1–D5 totals ----------

def run_pca_d_totals(df, n_components=2):
    """
    Run PCA on D1–D5 totals to see which dimensions drive differences.
    """
    # Ensure no missing values
    pca_df = df.dropna(subset=D_TOTAL_COLS).copy()

    X = pca_df[D_TOTAL_COLS].values
    regions = pca_df[REGION_COL].values

    pca = PCA(n_components=n_components, random_state=42)
    X_pca = pca.fit_transform(X)

    # Explained variance
    expl = pca.explained_variance_ratio_
    print(f"[INFO] PCA explained variance ratios: {expl}")

    # Scatter plot in PC1–PC2 space
    plt.figure(figsize=(8, 7))
    unique_regions = sorted(set(regions))

    for region in unique_regions:
        mask = regions == region
        plt.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            label=region,
            alpha=0.7
        )

    plt.xlabel(f"PC1 ({expl[0]*100:.1f}% var)")
    plt.ylabel(f"PC2 ({expl[1]*100:.1f}% var)")
    plt.title("PCA of D1–D5 Totals (all eras & regions)")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "pca_d1_d5_scatter.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved PCA scatter -> {out_path}")

    # Also return components + scores if we want tables later
    pca_components = pd.DataFrame(
        pca.components_,
        columns=D_TOTAL_COLS,
        index=[f"PC{i+1}" for i in range(n_components)]
    )
    return X_pca, pca_components, expl


# ---------- 3. K-means clustering ----------

def run_kmeans_clustering(df, X_pca, k=4):
    """
    Cluster era×region rows based on D1–D5 totals
    (applied in PCA space for nicer visualization).
    """
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_pca)

    df_clustered = df.copy()
    df_clustered["Cluster"] = labels

    # Plot clusters in PC1–PC2 again
    plt.figure(figsize=(8, 7))
    for c in range(k):
        mask = labels == c
        plt.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            label=f"Cluster {c}",
            alpha=0.7
        )

    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title(f"K-Means Clusters (k={k}) on D1–D5 totals (PCA space)")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "kmeans_clusters_d1_d5.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved K-means cluster plot -> {out_path}")

    # Save cluster assignments for reference
    out_csv = os.path.join("output", "CCSI_with_clusters.csv")
    df_clustered.to_csv(out_csv, index=False)
    print(f"[OK] Saved dataset with cluster labels -> {out_csv}")

    return df_clustered


# ---------- MAIN ----------

def main():
    print("=== CCSI Step 2: Advanced Analysis ===")
    ensure_fig_dir()

    df = load_dataset()
    print(f"Loaded {len(df)} rows from {DATA_FILE}")

    # 1. Rolling averages of CCSI over time
    plot_rolling_means(df, window=3)

    # 2. PCA on D1–D5 totals
    X_pca, pca_components, expl = run_pca_d_totals(df)

    # Save PCA loadings as a table
    pca_table_path = os.path.join("output", "PCA_D_totals_components.csv")
    pca_components.to_csv(pca_table_path)
    print(f"[OK] Saved PCA loadings table -> {pca_table_path}")

    # 3. K-means clustering in PCA space
    _ = run_kmeans_clustering(df, X_pca, k=4)

    print("=== Step 2 analysis complete. Check 'figures/' and 'output/' ===")


if __name__ == "__main__":
    main()
