# KBA Market Analysis Pipeline – German Vehicle Registration Trends (2020–2025)

> *Comprehensive analysis of German automotive market evolution using official*
> *Kraftfahrt-Bundesamt (KBA) vehicle registration data across a decade of transformation.*

[![Python](https://img.shields.io/badge/Python-3.9.21-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Lab-orange.svg)](https://jupyter.org)
[![dbt](https://img.shields.io/badge/dbt-Not%20Implemented-red.svg)](https://getdbt.com)
![Pipeline Status](https://img.shields.io/badge/Pipeline-90%25%20Complete-yellow.svg)

---

## Executive Summary

This repository implements a comprehensive data processing pipeline for analyzing German automotive market data from the Kraftfahrt-Bundesamt (KBA). The system processes **822,248 vehicle registration records** across 15 statistical datasets, transforming complex Excel reports into structured analytics-ready datasets.

**Primary Use Case**: Strategic market analysis for **global manufacturers** evaluating entry into Germany's automotive market.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [Technology Stack](#technology-stack)
4. [Folder Structure](#folder-structure)
5. [Raw Data Sources](#raw-data-sources)
6. [Data Inventory](#data-inventory)
7. [Data Quality Framework](#data-quality-framework)
8. [Data Quality & Governance](#data-quality--governance)
9. [Business Applications](#business-applications)
10. [Usage Guide](#usage-guide)
11. [Command Reference](#command-reference)
12. [Prerequisites](#prerequisites)
13. [License & Data Attribution](#license--data-attribution)

---

## Problem Statement

The German automotive market underwent significant structural changes between 2020 
and 2025, driven by environmental regulations, electrification trends, and shifting 
consumer preferences. However, analyzing these trends requires processing complex, 
multi-format official registration data scattered across different KBA statistical 
series (FZ1, FZ2, FZ3, FZ8, FZ10, etc).

Key analytical challenges include:
- **Data fragmentation**: Multiple Excel formats across different time periods
- **Schema evolution**: Column structures changed between 2020-2022 and 2023-2025
- **German formatting**: Decimal separators, special characters, and encoding issues
- **Scale complexity**: Hundreds of thousands of records across 50+ monthly datasets

This project delivers a unified analytical framework for automotive market research, 
policy analysis, and sustainability assessment.

---

## Data Inventory

### Core Statistical Series (15 datasets, 822,248 records)

| Series | Description | Records | Key Dimensions / Business Value |
|--------|-------------|---------|---------------------------------|
| **FZ-8.2** | Monthly brand statistics | 2,950 | Market share trends, competitive analysis |
| **FZ-8.3** | Comprehensive vehicle analysis | 21,821 | Vehicle categories, technical specs / Product positioning insights |
| **FZ-8.6** | Regional vehicle distribution | 937 | Geographic distribution / Regional market opportunities |
| **FZ-8.7** | Age and usage analysis | 2,954 | Vehicle age, usage patterns / Replacement cycle insights |
| **FZ-8.8** | Engine specifications | 1,025 | Engine size, power / Technical positioning |
| **FZ-8.9** | Commercial vehicle analysis | 2,950 | Commercial categories / Fleet market opportunities |
| **FZ-8.16** | Special vehicle categories | 2,113 | Specialty vehicles / Niche market identification |
| **FZ-1.1** | Regional vehicle data | 2,397 | Geographic opportunity mapping |
| **FZ-1.2** | Administrative breakdown | 2,397 | Administrative units / Policy impact analysis |
| **FZ-10.1** | Brand/model analysis | 22,683 | Product portfolio gaps |
| **FZ-2.2** | New registrations by fuel | 77,913 | Electrification transition |
| **FZ-2.4** | Extended registration metrics | 77,870 | Federal state distribution / Geographic penetration analysis |
| **FZ-3.1** | Commercial vehicles | 64,657 | Fleet market opportunities |
| **Trade Names** | Manufacturer registry | 517,656 | Regulatory intelligence |
| **Model Series** | Vehicle model lookup | 21,925 | Product positioning |

---

### Raw Data Sources
- **FZ8 PDF Files**: 36 monthly files (2020-2022)
- **FZ8 Excel Files**: 29 monthly files (2023-2025)
- **FZ10 Excel Files**: 64 monthly files (2020-2025)
- **FZ1 Excel Files**: 6 annual files (2020-2025)
- **FZ2 Excel Files**: 5 annual files (2020-2025)
- **FZ3 Excel Files**: 7 annual files (2020-2025)

---

### Data Quality Framework
- **UTF-8 Encoding**: Full German character support (ä, ö, ü handling verified)
- **Schema Evolution**: Automated handling of format changes between 2020-2022 and 2023-2025 periods
- **Date Format Consistency**: Multiple formats handled (YYYYMM for FZ8/FZ10, YYYY for FZ1/FZ2/FZ3)
- **Validation Coverage**: 822,248 total records validated across all datasets

---

## Folder Structure

```
kba_market_analysis/
├── data/                      # Data storage (gitignored for size)
│   ├── raw/                   # Original Excel/PDF files from KBA
│   │   ├── fz1/               # Vehicle stock by make/model
│   │   ├── fz2/               # New registrations by fuel type
│   │   ├── fz3/               # Commercial vehicle registrations  
│   │   ├── fz8/               # Monthly registration statistics
│   │   └── fz10/              # Regional breakdown data
│   └── processed/             # Cleaned CSV files for analysis
├── dbt_kba/                   # dbt project for data modeling
│   ├── models/                # SQL transformation models
│   ├── macros/                # Reusable SQL functions
│   ├── seeds/                 # Reference data (lookup tables)
│   └── dbt_project.yml        # dbt project configuration
│   └── README.md              # dbt project README file
├── docs/                      # Project documentation
│   ├── data-dictionary.md     # field definitions and relationships
├── notebooks/                 # Jupyter analysis notebooks
│   ├── _1_*.ipynb             # Data extraction workflows
│   ├── _2_*.ipynb             # Data transformation processes
│   ├── ...                    # ...
│   └── _9_*.ipynb             # Database upload procedures
├── scripts/                   # Automation and utility scripts
│   └── old/                   # Deprecated/experimental code
├── environment.yml            # Defines the conda environment
├── LICENSE                    # The project’s license file
├── mkdocs.yml                 # Configuration file for generating project documentation
├── pyproject.toml             # Modern Python packaging configuration file
├── requirements.txt           # Standard list of Python dependencies for pip
└── README.md                  # This file
```

---

## Solution Overview

The KBA Market Analysis pipeline transforms raw government data into analytical-ready 
datasets through a multi-stage ETL process:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   KBA Excel     │    │   Python ETL     │    │   PostgreSQL    │    │   Business      │
│   Reports       │───▶│   (Jupyter)      │───▶│   Database      │───▶│   Intelligence  │
│                 │    │                  │    │                 │    │                 │
│ • 111 files     │    │ • pandas         │    │ • 822K records  │    │ • Tableau       │
│ • German format │    │ • openpyxl       │    │ • UTF-8         │    │ • Market Entry  │
│ • Multi-schema  │    │ • Date handling  │    │ • Indexed       │    │ • Competitive   │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────────┐
                       │   CSV Storage    │    │   dbt Models        │
                       │   (Processed)    │    │   NOT IMPLEMENTED   │
                       │                  │    └─────────────────────┘
                       │ • 15 CSV files   │
                       │ • 822K records   │                              ┌───────────────────────────┐
                       │ • Standardized   │────────────────────────────▶ │   Tableau visualization   │
                       └──────────────────┘                              └───────────────────────────┘
```

---

### Technology Stack
- **ETL Layer**: Python 3.9.21, pandas, openpyxl, SQLAlchemy
- **Storage**: PostgreSQL 13+ with UTF-8 collation, psycopg2-binary driver
- **Environment**: python-dotenv for configuration management
- **Transform**: dbt Core 1.0+ (**NOT IMPLEMENTED**)
- **Analysis**: Jupyter Lab (8 notebooks, 27,930 total lines)
- **Visualization**: Tableau Desktop (external integration)
- **Orchestration**: Manual execution (**TODO**: Implement Airflow/Prefect)

---

## Quickstart

### Prerequisites

- **Python 3.9.21+** with pip package manager
- **PostgreSQL 13+** database server (local or remote)
- **Jupyter Lab**
- **dbt Core 1.0+** for data transformation
- **Git** for version control

---

## Usage Guide

### Production Data Processing Workflow

#### Phase 1: Historical Brand Analysis
```bash
# 1. Legacy format processing (2020-2022)
jupyter lab notebooks/_1_fz8_2020-2022.ipynb
# Processes: Older Excel format, schema differences
# Output: Standardized monthly brand statistics

# 2. Modern format processing (2023-2025) 
jupyter lab notebooks/_2_fz8_2023-2025.ipynb
# Processes: Advanced Excel parsing, German formatting, 8 sheet types
# Output: FZ8.2, 8.3, 8.6, 8.7, 8.8, 8.9, 8.16 series (34,850 total records)
```

#### Phase 2: Market Intelligence
```bash
# 3. Brand & Model Intelligence
jupyter lab notebooks/_3_fz10.ipynb
# Processes: Manufacturer analysis, model series
# Output: 22,683 brand/model records, competitive positioning

# 4. Regional Market Analysis  
jupyter lab notebooks/_4_fz1.ipynb
# Processes: Federal states, administrative regions
# Output: 4,794 geographic records (2 datasets)
```

#### Phase 3: Advanced Analytics
```bash
# 5. Fuel Transition Analysis
jupyter lab notebooks/_5_fz2.ipynb
# Status: FULLY FUNCTIONAL - processes FZ2.2 and FZ2.4 sheets
# Output: 155,783 fuel/demographic records across 2 datasets
# Features: Layout validation, German text normalization, multi-file processing

# 6. Commercial Vehicle Analysis
jupyter lab notebooks/_6_fz3.ipynb
# Status: Simple processing, fully operational
# Output: 64,657 commercial vehicle distribution records
```

#### Phase 4: Data Warehouse Operations
```bash
# 7. Database Upload & Validation
jupyter lab notebooks/_9_push_processed_data.ipynb
# Processes: Bulk PostgreSQL upload, schema creation
# Uses: SQLAlchemy, dotenv_values for environment configuration

jupyter lab notebooks/_99_test_files_from_db.ipynb
# Processes: Database validation, comprehensive testing
# Uses: load_dotenv for environment configuration
# Shows: Data types, completeness, geographic distribution validation
```

---

### Command Reference

| Operation | Command | Output |
|-----------|---------|--------|
| **Legacy Processing** | `jupyter lab notebooks/_1_fz8_2020-2022.ipynb` | Historical brand data |
| **Modern Processing** | `jupyter lab notebooks/_2_fz8_2023-2025.ipynb` | 8 FZ8 series datasets |
| **Market Analysis** | `jupyter lab notebooks/_3_fz10.ipynb` | Brand/model intelligence |
| **Geographic Analysis** | `jupyter lab notebooks/_4_fz1.ipynb` | Regional opportunities |
| **Fuel Analysis** | `jupyter lab notebooks/_5_fz2.ipynb` | Fuel transition data |
| **Commercial Analysis** | `jupyter lab notebooks/_6_fz3.ipynb` | Commercial vehicle data | |
| **Database Upload** | `jupyter lab notebooks/_9_push_processed_data.ipynb` | PostgreSQL integration |
| **Data Validation** | `jupyter lab notebooks/_99_test_files_from_db.ipynb` | Quality assurance |
| **dbt Transformation** | `dbt run` | ❌ Not Available | **TODO**: No KBA models exist |

---

## Business Applications

### Market Entry Decision Support
- **Competitive Gap Analysis**: Identify underserved SUV segments and price points
- **Geographic Prioritization**: Target federal states with favorable EV adoption
- **Product Portfolio Planning**: Optimize model mix based on demand patterns
- **Timing Strategy**: Leverage 2025 policy tailwinds for market entry

### Sample Business Queries
```sql
-- Market share by brand (data available in fz_08.2_raw)
-- Note: FZ8 uses YYYYMM date format (e.g., 202212)
SELECT "MARKE" as brand, 
       SUM("ANZAHL") as total_registrations,
       AVG("CO2-EMISSION IN G/KM") as avg_co2_emissions,
       SUM("ELEKTRO (BEV)") as electric_vehicles,
       SUM("HYBRID") as hybrid_vehicles
FROM "fz_08.2_raw" 
WHERE "DATE" >= '202401'
GROUP BY "MARKE" 
ORDER BY total_registrations DESC;

-- EV adoption by federal state (data available in fz_1.1_raw)
-- Note: FZ1 uses YYYY date format (e.g., 2020)
SELECT "LAND" as federal_state,
       SUM(CAST("PERSONENKRAFTWAGEN" AS INTEGER)) as total_vehicles,
       AVG("PKW-DICHTE JE 1.000 EINWOHNER") as vehicle_density
FROM "fz_1.1_raw"
WHERE "DATE" = '2024'
GROUP BY "LAND"
ORDER BY total_vehicles DESC;

-- Fuel type analysis by manufacturer (data available in fz_2.2_raw)
-- Note: FZ2 uses YYYY date format (e.g., 2020)
SELECT "HERSTELLER" as manufacturer,
       "KRAFTSTOFFART" as fuel_type,
       SUM("INSGESAMT") as total_registrations,
       AVG("HALTERINNEN UND HALTER BIS 29 JAHRE") as young_owners
FROM "fz_2.2_raw"
WHERE "DATE" = '2024'
GROUP BY "HERSTELLER", "KRAFTSTOFFART"
ORDER BY total_registrations DESC;

-- Model analysis with electrification (data available in fz_10.1_raw)
-- Note: FZ10 uses YYYYMM date format (e.g., 202504)
SELECT "MARKE" as brand,
       "MODELLREIHE" as model_series,
       SUM("INSGESAMT") as total_registrations,
       SUM("MIT HYBRIDANTRIEB") as hybrid_vehicles,
       SUM("MIT ELEKTROANTRIEB") as electric_vehicles,
       SUM("MIT ALLRADANTRIEB") as awd_vehicles
FROM "fz_10.1_raw"
WHERE "DATE" >= '202401'
GROUP BY "MARKE", "MODELLREIHE"
ORDER BY total_registrations DESC;

-- Commercial vehicle distribution by region (data available in fz_3.1_raw)
-- Note: FZ3 uses YYYY date format (e.g., 2020)
SELECT "LAND" as federal_state,
       SUM("KRAFTRADER") as motorcycles,
       SUM("PERSONENKRAFTWAGEN") as passenger_cars,
       SUM("LASTKRAFTWAGEN") as trucks
FROM "fz_3.1_raw"
WHERE "DATE" = '2024'
GROUP BY "LAND"
ORDER BY passenger_cars DESC;
```

---

## Data Quality & Governance

### Automated Validation Framework
- **Schema Consistency**: Column types verified in database (object, int64, float64)
- **Date Format Handling**: Multiple formats supported (YYYYMM for monthly, YYYY for annual)
- **Business Rules**: Date ranges (2020-2025), registration count boundaries validated
- **Referential Integrity**: HSN/TSN code verification across 517,656 trade names
- **Data Freshness**: Monthly FZ8 updates through May 2025, annual series current

### Quality Metrics Dashboard
- **Completeness**: 822,248 / 822,248 records processed (100.0%)
- **Accuracy**: German character encoding validated across all datasets  
- **Consistency**: Schema evolution handled between time periods
- **Geographic Coverage**: 16 federal states, 806 administrative regions covered
- **Temporal Coverage**: 6 years (2020-2025) with monthly granularity where applicable

---

## License & Data Attribution

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

**Data Source**: Kraftfahrt-Bundesamt (KBA) - German Federal Motor Transport Authority  
**License**: German Government Open Data License (Datenlizenz Deutschland – Namensnennung – Version 2.0)  
**Update Frequency**: Monthly (FZ8, FZ10) and Annual (FZ1, FZ2, FZ3)  
**Data Coverage**: 2020-2025, 822,248 validated records across 15 statistical datasets