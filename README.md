📌 CCSI Research — Quantifying India’s Civilizational Trajectories (4500 years)

Author: Tejas Pradip Pawar
📧 tejaspawar1743@gmail.com

🧾 Independent research — no institutional or supervisory support involved

🔍 Overview

This repository contains all datasets, scripts and visualizations developed for the research titled:

“Quantifying India’s Civilizational Trajectories using the CCSI Framework to uncover civilizational patterns:
A Data-Driven Study of Social Mobility, Cultural Pluralism and State Stability for Future Policy Insights.”

The project builds the Cultural Cohesion and Social Inclusivity Index (CCSI) — a 0–100 composite measure that quantifies civilizational strength across five structural dimensions:

1️⃣ Social Mobility
2️⃣ Education & Knowledge Access
3️⃣ Economic Structure
4️⃣ Polity & Institutional Cohesion
5️⃣ Cultural Pluralism & Norms

💡 Scope of data inside this repository

Dataset category	Time span	Rows	Notes
Historical (E01–E22)	1500 BCE – 2000 CE	100	Fully validated & cleaned
Modern (M01–M05)	2000 – 2025	45	Constructed using measurable contemporary proxies
Combined Working Dataset	E + M	145	Used for PCA, K-Means & regional analysis
📁 Repository Structure (Human-friendly)
📂 CCSI_Research/
   ├── data/                <-- All datasets (CSV + XLSX)
   ├── scripts/             <-- Every script used for analysis / ML / dataset prep
   ├── figures/             <-- All CCSI visualizations (timelines, heatmaps etc.)
   ├── figures_ml/          <-- PCA, KMeans & clustering plots
   ├── output/              <-- Automatically saved results from ML + scripts
   ├── ccsi_graphical_appendix/   <-- Printable graphical appendix (DOCX/PDF)
   └── README.md


You can run almost everything with:

python scripts/ccsi_analysis_step1.py
python scripts/ccsi_analysis_step2.py
python scripts/ccsi_ml_analysis.py


No API key is needed and no internet access is required.

🧠 CCSI Indicator Glossary (for interpretability)

Each era is rated on 25 indicators, grouped into 5 dimensions.
Scores range 0 = absent / extremely weak → 4 = highly present & embedded.

Dimension	What it measures
D1	Social mobility & access to institutions
D2	Knowledge & education accessibility
D3	Economic structure & integration
D4	State cohesion & institutional stability
D5	Cultural pluralism & hierarchy norms

📌 Full 25-indicator glossary included in /Indicator_Glossary.md and Appendix
(also included inside this README for convenience)

<details> <summary>Click to expand full glossary (25 indicators)</summary>

[ 💬 Expand if you want to paste the full table here – you already have it from previous message ]

</details>
🔧 Reproducibility & Transparency Notes

This repository prioritizes reproducibility and clarity over perfection, so:

✔️ What is fully reproducible
Component	Status
Loading and exploring the dataset	✔️ Works
Historical & modern CCSI graphs	✔️ Works
Heatmaps per region	✔️ Works
PCA dimension reduction	✔️ Works
K-means clustering	✔️ Works
Export of ML comparison table	✔️ Works
⚠️ Minor notes (for transparency)

To repair a small number of early rows, a Gemini-assisted interpolation script (ccsi_patch_missing_rows.py) was used during initial development.
The repaired values were manually validated and merged into the final dataset.

💡 Because the WORKING dataset already contains the corrected values, running the early script is not required.
All current analyses run entirely offline and without APIs.

▶ How to Run the Project
1️⃣ Install requirements
pip install -r requirements.txt

2️⃣ Run historical + regional visualizations
python scripts/ccsi_analysis_step1.py

3️⃣ Run advanced figures
python scripts/ccsi_analysis_step2.py

4️⃣ Run ML comparisons (PCA + KMeans + nearest historical analogues)
python scripts/ccsi_ml_analysis.py


Results are saved automatically in /output/.

📌 Research Insight Summary

Complete summaries are included in the paper, but the key findings are below:

Finding	Evidence
Cohesion rises when mobility & knowledge open up	Seen in Mauryan, Tamilakam Classical, Early Republic
Decline always begins with gatekeeping	Late Vedic, Early Medieval, Colonial
Recovery always begins with education reform	Gupta, Bhakti-urbanization, Post-1950
Economic growth without pluralism is unstable	Colonial & late-20th friction eras
Modern India resembles “reform without emotional synchronisation” eras	ML mapping to E18–E20
🔗 Related Resources
Resource	File
Main Full Paper (IEEE format)	(submitted via email)
Graphical Appendix	/ccsi_graphical_appendix/
Supplementary ML Results	/output/CCSI_ML_RESULTS.csv
🤝 Citation

If you use this dataset or analysis, please cite:

Pawar, Tejas P. (2025). Quantifying India’s Civilizational Trajectories using the CCSI Framework: A Data-Driven Study of Social Mobility, Cultural Pluralism and State Stability for Future Policy Insights. Independent research.

💬 Contact

For collaboration, reproductions or presentations:
📧 tejaspawar1743@gmail.com

🏁 Final note from the author

This work was conducted independently, without funding or supervision, and involved the construction of a large-scale dataset, statistical scoring framework, and machine-learning validation from scratch. There may be minor formatting inconsistencies in the repository — they are not obstacles to reproduction, and every major component of the research is fully available and functional.
