# INTERIM VERSION (TO BE UPDATED)

# KBA Market Analysis (2015–2025)

**Research goal**  
Analyse how the structure and sustainability of the German vehicle market evolved between 2015 and 2025 using open Kraftfahrt-Bundesamt data.

**Stack**  
- PostgreSQL (DBeaver)
- dbt (data modelling)
- Python3 + Jupyter (ETL & EDA)
- Tableau (dashboards)

**Folder layout**
.
├── data/
│   ├── raw/          # original XLSX/PDF/CSV
│   └── processed/    # helper CSVs for COPY
├── dbt_kba/          # dbt project
├── notebooks/        # Jupyter notebooks
├── scripts/          # fetch_kba.sh, helpers
└── docs/             # diagrams, screenshots
