# 📊 Semantic Model Documentation - Aira

## 🎯 Overview

This semantic model is designed to support analytical reporting on Netflix content performance across two distinct grains:

- **Weekly performance (trend analysis)**
- **All-time performance (aggregate KPIs)**

The model follows a **star schema design** with conformed dimensions, enabling consistent filtering and scalable reporting.

---

# 🧱 Model Architecture

## Fact Tables
- `fact_weekly_performance` → granular weekly data
- `fact_alltime` → aggregated lifetime metrics

## Dimension Tables
- `dim_show` → central conformed dimension
- `dim_date` → time dimension
- `dim_country` → geography
- `dim_category` → content classification

---

# 🔑 Core Design Principle

`dim_show` is a **conformed dimension** used to filter multiple fact tables.

All fact tables must align with: `dim_show[show_key]`

---


---

# 📦 DIMENSION TABLES

---

## 🎬 dim_show

### Purpose
Central entity representing Netflix titles (films and TV shows).

### Grain
1 row = show_title + season_title + category


### Columns

| Column | Type | Description |
|------|------|------------|
| show_key | Integer (PK) | Surrogate key (unique identifier) |
| show_business_key | Text | Composite key: `show_title \| category \| season_title` |
| show_title | Text | Display title |
| season_title | Text | Season info ("No Season" for films) |
| category | Text | Films / TV |
| genre | Text | Content genre |
| imdb_rating | Decimal | IMDb score |
| cast_members | Text | Cast list |
| description | Text | Show synopsis |
| image | URL | Poster image |
| trailer | URL | Trailer link |

---

## 🌍 dim_country

### Purpose
Standardized country dimension.

### Columns

| Column | Type | Description |
|------|------|------------|
| country_key | Integer (PK) | Surrogate key |
| country_iso2 | Text | ISO country code |
| country_name | Text | Country name |

---

## 📅 dim_date

### Purpose
Time-based filtering and aggregation.

### Columns

| Column | Type | Description |
|------|------|------------|
| date_key | Integer (PK) | YYYYMMDD format |
| week_start_date | Date | Start of week |

---

## 🎭 dim_category

### Purpose
Content classification.

### Columns

| Column | Type | Description |
|------|------|------------|
| category_key | Integer (PK) | Surrogate key |
| category | Text | Films / TV |

---

# 📊 FACT TABLES

---

## 📈 fact_weekly_performance

### Purpose
Tracks weekly ranking and performance of shows per country.

### Grain
1 row = (show, country, week)


---

### Columns

| Column | Type | Description |
|------|------|------------|
| show_key | Integer (FK) | → dim_show |
| date_key | Integer (FK) | → dim_date |
| country_key | Integer (FK) | → dim_country |
| category_key | Integer (FK) | → dim_category |
| weekly_rank | Integer | Rank (1–10) |
| cumulative_weeks_in_top_10 | Integer | Longevity metric |
| weekly_hours_viewed | Integer | Hours viewed |
| weekly_views | Integer | Views count |
| runtime | Decimal | Runtime |
| performance_score | Decimal | Composite metric |

---

## 🏆 fact_alltime

### Purpose
Stores aggregated lifetime performance metrics.

### Grain
1 row = (show)


---

### Columns

| Column | Type | Description |
|------|------|------------|
| show_key | Integer (FK) | → dim_show |
| show_title | Text | Title (reference only) |
| season_title | Text | Season info |
| category | Text | Films / TV |
| hours_viewed_first_91_days | Integer | Total hours viewed |
| rank | Integer | Global rank |
| runtime | Decimal | Runtime |

---

# 🔗 RELATIONSHIPS

---

## Primary Relationships

| From | To | Type |
|------|----|------|
| dim_show[show_key] | fact_weekly_performance[show_key] | 1 → many |
| dim_show[show_key] | fact_alltime[show_key] | 1 → many |
| dim_date[date_key] | fact_weekly_performance[date_key] | 1 → many |
| dim_country[country_key] | fact_weekly_performance[country_key] | 1 → many |
| dim_category[category_key] | fact_weekly_performance[category_key] | 1 → many |

---

## Filter Direction
Single direction (dimension → fact)


---

# 🔄 DATA INTEGRATION LOGIC

---

## Business Key Mapping

To align fact tables with `dim_show`, a composite key is used:
show_business_key = show_title | category | season_title



### Usage
1. Merge fact tables with `dim_show`  
2. Retrieve `show_key`  
3. Enable consistent relationships  

---

# 🧪 VALIDATION RULES

---

## Relationship Validation

- Slicer on `dim_show[show_title]` should:
  - Filter `fact_weekly_performance` ✅  
  - Filter `fact_alltime` ✅  

---

## Data Integrity Checks

- No unexpected NULLs in `show_key`  
- Row count unchanged after merges  
- Measures aggregate correctly  

---

# ⚠️ KNOWN LIMITATIONS

---

- Some rows may not match `dim_show` due to:
  - inconsistent naming  
  - missing category/season alignment  

- Joins are handled in Power Query (not upstream ETL)

---

# 🚀 ANALYTICAL CAPABILITIES

---

## 📊 Trend Analysis
- Weekly ranking evolution  
- Performance over time  

## 🏆 Top Content
- Top shows by hours viewed  
- Longest-running shows in Top 10  

## 🌍 Regional Insights
- Country-level performance  
- Content popularity by geography  

## 🎬 Content Insights
- Genre performance  
- Film vs TV comparisons  

---

# 💼 DESIGN PATTERN
Star Schema + Conformed Dimensions

---

### Characteristics
- Surrogate keys  
- Single-direction filtering  
- Fact/dimension separation  
- Reusable dimensions across facts  

---

# 🧠 LLM USAGE CONTEXT

---

This model is optimized for:

- Power BI dashboard generation  
- KPI design  
- Data storytelling  
- DAX / SQL query generation  

---

