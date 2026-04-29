import pandas as pd
from pathlib import Path

# 📍 Base path
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = BASE_DIR / "data" / "raw" / "global_weekly.xlsx"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "nordic_weekly.xlsx"

# Load
df = pd.read_excel(RAW_PATH)

# Filter Nordic countries
nordic_countries = ["Sweden", "Norway", "Denmark", "Finland", "Iceland"]
df_nordic = df[df["country_name"].isin(nordic_countries)].copy()

# Convert week to datetime
df_nordic["week"] = pd.to_datetime(df_nordic["week"])

# Create clean year + month
df_nordic["year"] = df_nordic["week"].dt.year.astype(int)
df_nordic["month"] = df_nordic["week"].dt.month.astype(int)

#  Remove month_start
# (do not create it at all OR drop if already exists)
if "month_start" in df_nordic.columns:
    df_nordic = df_nordic.drop(columns=["month_start"])

# ✅ Ensure clean column order (optional but clean)
columns_order = [
    "country_name",
    "country_iso2",
    "week",
    "category",
    "weekly_rank",
    "show_title",
    "season_title",
    "cumulative_weeks_in_top_10",
    "year",
    "month"
]

df_nordic = df_nordic[columns_order]

# Save
df_nordic.to_excel(PROCESSED_PATH, index=False, engine="openpyxl")

print("✅ Clean Nordic dataset saved!")