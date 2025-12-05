# Cultural Cohesion and Social Inclusivity Index (CCSI)

**Author:** Tejas Pradip Pawar  
**Contact:** tejaspawar1743@gmail.com  

This repository contains the code and data used for the paper:

> **“Quantifying India’s Civilizational Trajectories using the CCSI Framework to Uncover Civilizational Patterns: A Data-Driven Study of Social Mobility, Cultural Pluralism and State Stability for Future Policy Insights.”**

The project builds a long-run **Cultural Cohesion and Social Inclusivity Index (CCSI)** for the Indian subcontinent, covering 130 historical eras and 45 modern eras across multiple regions.  
It includes:

- Structured **historical and modern datasets** (Excel)
- Scripts to **clean, extend and analyse** the dataset
- Scripts to **generate all figures** used in the paper
- A basic **ML pipeline (PCA + KMeans)** to compare modern India with historical eras
- An optional **automation script** that talks to an LLM API to help with drafting text (API key required, not included)

---

## Repository structure

Suggested layout (what this repo currently exposes):

```text
.
├── data/
│   ├── CCSI_Dataset_FINAL.xlsx          # original historical dataset (E-eras)
│   ├── CCSI_Dataset_MODERN.xlsx         # modern M01–M05 rows (2000–2025)
│   ├── CCSI_Dataset_WORKING.xlsx        # combined E + M dataset used for ML
│   └── (optional) other intermediate files
├── figures/
│   ├── ccsi_all_regions_comparison.png
│   ├── ccsi_rolling_means_regions.png
│   ├── ccsi_timeline_all_regions.png
│   ├── ccsi_timeline_Deccan.png
│   ├── ccsi_timeline_Gangetic_North.png
│   ├── ccsi_timeline_Northeast.png
│   ├── ccsi_timeline_Northwest_Punjab-Gandhāra.png
│   ├── ccsi_timeline_Tamilakam.png
│   ├── dimensions_heatmap_Deccan.png
│   ├── dimensions_heatmap_Gangetic_North.png
│   ├── dimensions_heatmap_Northeast.png
│   ├── dimensions_heatmap_Northwest_Punjab-Gandhāra.png
│   └── dimensions_heatmap_Tamilakam.png
├── figures_ml/
│   ├── pca_E_vs_M.png
│   ├── pca_clusters_modern_highlight.png
│   ├── pca_d1_d5_scatter.png
│   └── kmeans_clusters_d1_d5.png
├── scripts/
│   ├── ccsi_add_modern_rows.py      # builds modern rows M01–M05 into MODERN file
│   ├── ccsi_dataset_working.py      # merges E + M and does consistency checks
│   ├── ccsi_analysis_step1.py       # historical visualisations (timelines, heatmaps)
│   ├── ccsi_analysis_step2.py       # dimension-level plots, rolling means, etc.
│   ├── ccsi_ml_analysis.py          # PCA + KMeans + nearest historical analogues
│   ├── ccsi_automation.py           # OPTIONAL: LLM-based helper (requires API key)
│   └── auto_image_insertion.py      # OPTIONAL: insert images into Word/LaTeX docs
├── CCSI_Appendix_COMPACT.docx       # graphical appendix with key figures
├── requirements.txt
└── README.md
