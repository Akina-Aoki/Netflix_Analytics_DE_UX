# 📊 Dataset: netflix.csv (Unified & Validated Schema)

## 🎯 Purpose
This document defines the **single source of truth** for `netflix.csv`, combining:
- Actual dataset structure (validated via schema)
- Intended analytical model (from source documentation)

**It ensures:**
- Correct SQL generation (DuckDB / Pandas)
- No schema hallucination in LLMs (e.g. Codex)
- Safe, grain-aware analytics

---

## 🧠 Grain (CRITICAL)
ONE ROW = (show_title, week, country_name)


### Interpretation:
- Weekly dataset
- Country-level ranking
- Each row = one appearance in Top 10

---

## ⚠️ Key Reality Check

### ✅ This dataset IS:
- Rank-based (Top 10)
- Observational (appearances per week per country)

### ❌ This dataset is NOT:
- Viewership-based (no `hours_viewed`)
- Revenue-based

👉 Metrics like `hours_viewed_first_91_days` belong to **other datasets**  
(e.g. `global_alltime`, `global_weekly`) and are NOT included here

---

## 📦 Column Definitions

### 🔹 Core Dimensions

- `show_title` (string)  
  Primary entity (movie or series)

- `season_title` (string, nullable)  
  Season-level detail (for TV content)

- `week` (date/string)  
  Weekly time dimension

- `country_name` (string)  
  Country where the title appears in Top 10

- `country_iso2` (string)  
  ISO country code (e.g. SE, NO, DK)

---

### 🔹 Classification

- `global_category` (string)  
  Content type (Film / TV)

- `country_category` (string)  
  Country-specific classification

---

### 🔹 Ranking Metrics (PRIMARY KPIs)

- `country_weekly_rank` (int)  
  Rank within Top 10 (1 = best)

- `country_cumulative_weeks_in_top_10` (int)  
  Total lifetime weeks in Top 10

---

### 🔹 Technical Column

- `Unnamed: 0` (int)  
  Index column from CSV export  
  ⚠️ Ignore in analysis

---

## 🧩 Data Model Classification

| Layer        | Type        | Column |
|-------------|------------|--------|
| Temporal     | Weekly     | `week` |
| Dimensional  | Title      | `show_title` |
| Geographic   | Country    | `country_name` |

---

## ⚠️ Data Characteristics

### 1. Rank-Based Dataset
This dataset measures:
- Popularity → via rank
- Persistence → via weeks in Top 10

---

### 2. Mixed Granularity (Important)

- `show_title` → main entity
- `season_title` → sub-level entity

👉 Be careful when aggregating (risk of duplication)

---

### 3. Repeated Rows Are Expected

Titles appear:
- Across multiple weeks
- Across multiple countries

👉 This is correct behavior

---

## 🔗 Analytical Constraints

### ❌ DO NOT:
- Use `country` → use `country_name`
- Use `Unnamed: 0`
- Assume viewership metrics exist
- Aggregate blindly across seasons

---

### ✅ DO:

| Use Case | Column |
|---------|--------|
| Popularity | `country_weekly_rank` |
| Longevity | `country_cumulative_weeks_in_top_10` |
| Geography | `country_name` |
| Time Series | `week` |

---
