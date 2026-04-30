# Netflix Analytics | Data Engineer + UX Desdigners

## Project Overview
This project is a collaboration between the Data Engineering and UX teams to build a user centered analytics product for Netflix Trends. The team combines data modeling (semantic model), exploratory analysis, storytelling visuals, and dashboard design in PowerBI and Streamlit so stakeholders can make data-driven decisions. 

- **Primary data source:**  https://www.netflix.com/tudum/top10
- **Course Repository Used:** https://github.com/AIgineerAB/data_visualisation_bi_course

---

## Repository Setup
- [Repository Setup](documentation/repo_setup.md)
- [Netflix Schema Documentation / RAW](documentation/netflix_schema.md)
- [Semantic Model Version 2 Documentation](documentation/semantic_doc.md)
---

## Repository Structure

```text
Netflix_Analytics_DE_UX/
├── assets/                           # Storytelling and dashboard image assets
├── documentation/                    # Project docs, grading criteria, schema, workflow guides
│   ├── grade_criteria.md
│   ├── netflix_schema.md
│   ├── repo_setup.md
│   ├── semantic_doc.md
│   └── workflow_guide.md
├── eda/                               # Individual EDA notebooks (one folder per contributor pattern)
    └── Yousif/
    └── Christophe/
    └── Gavin/
    └── Marcus/
│   └── aira_eda/                     
│       ├── 00_eda_with_star_schema.ipynb
│       ├── 01_global_weekly_eda_aira.ipynb
│       ├── 02_global_alltime_eda_aira.ipynb
│       ├── 03_country_weekly.ipynb
│       ├── 04_netflix_merge_aira.ipynb
│       ├── 05_day_and_a_half.ipynb
│       └── 06_nordic_global_weekly.ipynb
├── sql/
│   └── init.sql                      # SQL initialization scripts (Not used)
├── src/
│   ├── filter_nordics.py             # Script to filter nordic countries from raw dataset
│   ├── merge_netflix_data.ipynb      # 1st model build: Merge/JOINS
│   └── semantic_model/               # 2nd model build: Star-schema build/validation logic
│       ├── build_star_schema.py
│       └── validate_model.py
├── main.py                           # Streamlit app entrypoint
├── pyproject.toml
└── uv.lock
```

---

## Project Architecture
```text
Netflix Tudum (Source)
        │
        ▼
Data export & consolidation
        │
        ▼
Exploratory Data Analysis (individual EDA notebooks)
        │
        ├──► Data understanding (patterns, rank behavior, country/week trends)
        └──► Matplotlib storytelling charts for insights communication
        │
        ▼
Semantic modeling (star schema preparation + validation)
        │
        ▼
Dashboard delivery tracks
        ├──► Power BI dashboards (co-created with UX designers)
        └──► Streamlit dashboard application (implementation/deployment)
```

### Architecture Notes
- **Source origin:** All core Netflix ranking data comes from **Netflix Tudum Top 10**.
- **EDA role:** Each contributor runs EDA in their own notebooks/folders to validate assumptions and identify insights.
- **Storytelling layer:** Matplotlib visuals are produced for narrative reporting and presentation.
- **UX + BI collaboration:** Power BI dashboards are designed with UX input for usability and decision support.
- **Application layer:** Streamlit is used as the deployable analytics frontend.



