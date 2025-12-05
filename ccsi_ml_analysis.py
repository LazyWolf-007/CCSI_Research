import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# ================== CONFIG ==================

DATA_FILE = os.path.join("output", "CCSI_Dataset_WORKING.xlsx")
FIG_DIR   = "figures_ml"
OUT_CSV   = os.path.join("output", "CCSI_ML_RESULTS.csv")

os.makedirs(FIG_DIR, exist_ok=True)

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

# ============== HELPER FUNCTIONS ==============

def era_to_num(eid):
    """Convert 'E01' or 'M03' -> integer 1, 3 etc."""
    try:
        return int(str(eid)[1:])
    except Exception:
        return None

def load_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Cannot find {DATA_FILE}")
    df = pd.read_excel(DATA_FILE)

    # Era_Type: E or M
    df["Era_Type"] = df["Era_ID"].astype(str).str[0]

    # Era_Num: 01 -> 1
    df["Era_Num"] = df["Era_ID"].apply(era_to_num)

    # Sort for sanity: historical first by region+era, then modern by region+era
    df = df.sort_values(["Era_Type", "Region", "Era_Num"]).reset_index(drop=True)

    # Just in case there are NaNs in indicators:
    df[INDICATOR_COLS] = df[INDICATOR_COLS].fillna(0)

    print(f"Loaded {len(df)} rows from {DATA_FILE}")
    print("Era_Type counts:\n", df["Era_Type"].value_counts())
    return df

def run_pca_kmeans(df, n_clusters=5):
    """
    Run PCA + KMeans on the 25 indicators.
    Returns updated df with PCA1, PCA2, Cluster, and the fitted objects.
    """
    X = df[INDICATOR_COLS].values

    # 1) Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2) PCA
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df["PCA1"] = X_pca[:, 0]
    df["PCA2"] = X_pca[:, 1]

    print("\nPCA explained variance (2 components):")
    print(pca.explained_variance_ratio_)
    print("Total variance explained:", pca.explained_variance_ratio_.sum())

    # 3) KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["Cluster"] = kmeans.fit_predict(X_scaled)

    print(f"\nKMeans with k={n_clusters}")
    print(df.groupby(["Era_Type", "Cluster"]).size().unstack(fill_value=0))

    return df, scaler, pca, kmeans

def plot_pca_by_type(df):
    """Scatter plot in PCA space: historical vs modern."""
    plt.figure(figsize=(8, 6))

    mask_E = df["Era_Type"] == "E"
    mask_M = df["Era_Type"] == "M"

    plt.scatter(df.loc[mask_E, "PCA1"],
                df.loc[mask_E, "PCA2"],
                alpha=0.6, label="Historical (E)", marker="o")
    plt.scatter(df.loc[mask_M, "PCA1"],
                df.loc[mask_M, "PCA2"],
                alpha=0.9, label="Modern (M)", marker="^")

    plt.xlabel("PCA1")
    plt.ylabel("PCA2")
    plt.title("CCSI PCA: Historical vs Modern Eras")
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "pca_E_vs_M.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved PCA plot (E vs M) -> {out_path}")

def plot_pca_clusters(df):
    """Scatter plot in PCA space colored by cluster, highlight modern eras."""
    plt.figure(figsize=(9, 7))

    clusters = sorted(df["Cluster"].unique())
    for c in clusters:
        subset = df[df["Cluster"] == c]
        plt.scatter(subset["PCA1"], subset["PCA2"],
                    alpha=0.6, label=f"Cluster {c}")

    # Highlight modern points with black edge
    modern = df[df["Era_Type"] == "M"]
    plt.scatter(modern["PCA1"], modern["PCA2"],
                facecolors="none", edgecolors="black",
                s=100, linewidths=1.5, label="Modern (M) highlight")

    plt.xlabel("PCA1")
    plt.ylabel("PCA2")
    plt.title("CCSI PCA: KMeans Clusters (modern eras circled)")
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(FIG_DIR, "pca_clusters_modern_highlight.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Saved PCA cluster plot -> {out_path}")

def compute_nearest_historical(df, k=3):
    """
    For each modern row, find k nearest historical eras
    in PCA space (Euclidean distance).
    Adds a column 'Nearest_Historical' with a short text summary.
    """
    hist = df[df["Era_Type"] == "E"].copy()
    modern = df[df["Era_Type"] == "M"].copy()

    hist_coords = hist[["PCA1", "PCA2"]].values
    modern_coords = modern[["PCA1", "PCA2"]].values

    nearest_texts = []

    for i, (idx_m, mrow) in enumerate(modern.iterrows()):
        vec = modern_coords[i]
        dists = np.linalg.norm(hist_coords - vec, axis=1)
        nearest_idx = np.argsort(dists)[:k]

        nearest_rows = hist.iloc[nearest_idx]
        summaries = []
        for j, (_, hrow) in enumerate(nearest_rows.iterrows()):
            summaries.append(
                f"{j+1}) {hrow['Era_ID']} {hrow['Era_Start_Year']}-{hrow['Era_End_Year']} "
                f"({hrow['Region']}), CCSI={hrow.get('CCSI_Total', 'NA')}"
            )
        nearest_texts.append(" | ".join(summaries))

    # Attach back to df (only modern rows)
    df_modern = modern.copy()
    df_modern["Nearest_Historical"] = nearest_texts

    # Merge back into full df
    df = df.merge(
        df_modern[["Era_ID", "Region", "Nearest_Historical"]],
        on=["Era_ID", "Region"],
        how="left"
    )

    return df

# ===================== MAIN =====================

def main():
    print("=== CCSI ML Analysis: PCA + KMeans ===")
    df = load_data()

    # Choose number of clusters (you can tweak this):
    N_CLUSTERS = 5

    df, scaler, pca, kmeans = run_pca_kmeans(df, n_clusters=N_CLUSTERS)

    # Plots
    plot_pca_by_type(df)
    plot_pca_clusters(df)

    # Nearest historical analogues for modern rows
    df = compute_nearest_historical(df, k=3)

    # Save results CSV
    cols_to_save = [
        "Era_ID", "Era_Start_Year", "Era_End_Year",
        "Region", "Era_Type", "Era_Num",
        "CCSI_Total", "Cluster", "PCA1", "PCA2",
        "Nearest_Historical"
    ]
    # Include indicators as well for convenience
    cols_to_save = cols_to_save + INDICATOR_COLS

    df[cols_to_save].to_csv(OUT_CSV, index=False)
    print(f"\n[OK] Saved ML results -> {OUT_CSV}")

    # Print a quick sample for you to see in terminal
    print("\nSample modern rows with nearest historical analogues:")
    print(df[df["Era_Type"] == "M"][[
        "Era_ID", "Region", "Cluster", "CCSI_Total", "Nearest_Historical"
    ]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
