CCSI Research — Cultural Cohesion & Social Inclusivity Index

This repository contains the complete dataset, scripts and visualizations for the research project:

“Quantifying India’s Civilizational Trajectories using the Cultural Cohesion & Social Inclusivity Index (CCSI)”
Author: Tejas Pradip Pawar
Email: tejaspawar1743@gmail.com

📌 Project Overview

The CCSI framework quantifies civilizational development across 130 historical eras and 45 modern eras using five measurable dimensions:

Code	Dimension
D1	Social Mobility
D2	Education & Knowledge Systems
D3	Economic Capacity
D4	Polity & State Cohesion
D5	Cultural & Religious Inclusivity

Scores were compiled region-wise across Deccan, Gangetic North, Tamilakam, Northeast, Northwest (Punjab–Gandhāra) and then extended to modern India.

The analysis includes:

Time-series trends

Cross-regional comparisons

PCA dimensionality reduction

K-Means clustering

Historical–modern similarity mapping

📂 Repository Structure
CCSI_Research/
│── data/                 # CSV datasets (cleaned & modern)
│── output/               # Analysis results & processed datasets
│── figures/              # All graphs used in the research
│── scripts/              # Python scripts used for full pipeline
│── README.md             # Documentation

📊 Dataset Files
File	Description
CCSI_Dataset_WORKING.csv	Clean full dataset used for final analysis
CCSI_Dataset_MODERN.csv	Only M-series (modern) eras
CCSI_Dataset_WITH_MODERN.xlsx	Combined historical + modern before filtering
🧠 Scripts
Script	Purpose
ccsi_build_working_dataset.py	Generates clean dataset for analysis
ccsi_analysis_step1.py	Trend visualizations (time series, heatmaps)
ccsi_analysis_step2.py	PCA + K-Means clustering
ccsi_add_modern_rows.py	Inserts M-series eras
ccsi_ml_analysis.py	Modern–historical similarity mapping
▶ How to Reproduce Full Analysis
pip install pandas numpy matplotlib seaborn scikit-learn openpyxl


Run in order:

python scripts/ccsi_build_working_dataset.py
python scripts/ccsi_analysis_step1.py
python scripts/ccsi_analysis_step2.py
python scripts/ccsi_ml_analysis.py


All figures will be saved in figures/
Generated ML tables will appear in output/

📥 Use in Research

If this repository helps your work, please cite:

Pawar, Tejas (2025). Quantifying India’s Civilizational Trajectories using the Cultural Cohesion & Social Inclusivity Index (CCSI). GitHub Repository. https://github.com/LazyWolf-007/CCSI_Research

📫 Contact

For queries or collaboration:
📧 tejaspawar1743@gmail.com
