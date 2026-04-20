from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd

# 🔥 FIXED: robust base dir
BASE_DIR = Path().resolve()
DATA_DIRS = [BASE_DIR / "data" / "raw", BASE_DIR / "data" / "processed"]
MODEL_DIR = BASE_DIR / "data" / "processed" / "model"

REQUIRED_FILES = [
    "global_weekly.xlsx",
    "country_weekly.xlsx",
    "global_alltime.xlsx",
    "imdb_deduped.csv",
    "genre.csv",
]


# ----------------------------
# Helpers
# ----------------------------

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def normalize_text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )


def coalesce_columns(df: pd.DataFrame, aliases: list[str], default: Any = np.nan) -> pd.Series:
    for col in aliases:
        if col in df.columns:
            return df[col]
    return pd.Series([default] * len(df), index=df.index)


def read_dataset(path: Path | None) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame()
    if path.suffix.lower() == ".xlsx":
        return standardize_columns(pd.read_excel(path))
    if path.suffix.lower() == ".csv":
        return standardize_columns(pd.read_csv(path))
    raise ValueError(f"Unsupported file format: {path}")


# ----------------------------
# 🔥 NEW: Smart dataset selection
# ----------------------------

def locate_files() -> dict[str, Path | None]:
    located = {}
    for name in REQUIRED_FILES:
        found = None
        for d in DATA_DIRS:
            candidate = d / name
            if candidate.exists():
                found = candidate
                break
        located[name] = found
    return located


def choose_weekly_dataset(file_locations) -> pd.DataFrame:
    candidates = [
        file_locations["country_weekly.xlsx"],
        file_locations["global_weekly.xlsx"],
    ]

    for path in candidates:
        if path is None:
            continue

        df = read_dataset(path)

        # 🔥 Detect real weekly dataset
        if "week" in df.columns and ("weekly_rank" in df.columns or "rank" in df.columns):
            print(f"✅ Using weekly dataset: {path}")
            return df

    raise ValueError("❌ No valid weekly dataset found (missing week + rank columns)")


# ----------------------------
# Business keys
# ----------------------------

def add_business_keys(df: pd.DataFrame) -> pd.DataFrame:
    df["show_title"] = df.get("show_title", "").fillna("").astype(str).str.strip()
    df["category"] = df.get("category", "Unknown").fillna("Unknown").astype(str).str.strip()
    df["season_title"] = df.get("season_title", "No Season").fillna("No Season").astype(str).str.strip()

    df["show_title_key"] = normalize_text(df["show_title"])

    df["show_business_key"] = (
        normalize_text(df["show_title"])
        + "|"
        + normalize_text(df["category"])
        + "|"
        + normalize_text(df["season_title"])
    )

    return df


# ----------------------------
# Prepare datasets
# ----------------------------

def prepare_weekly(df: pd.DataFrame) -> pd.DataFrame:
    df["country_name"] = coalesce_columns(df, ["country_name", "country"])
    df["country_iso2"] = coalesce_columns(df, ["country_iso2"], default="")

    df["week"] = pd.to_datetime(coalesce_columns(df, ["week"]), errors="coerce")
    df["weekly_rank"] = pd.to_numeric(coalesce_columns(df, ["weekly_rank", "rank"]), errors="coerce")

    df["show_title"] = coalesce_columns(df, ["show_title"])
    df["season_title"] = coalesce_columns(df, ["season_title"], default="No Season")
    df["category"] = coalesce_columns(df, ["category"], default="Unknown")

    df["cumulative_weeks_in_top_10"] = pd.to_numeric(
        coalesce_columns(df, ["cumulative_weeks_in_top_10"]), errors="coerce"
    )

    df["weekly_hours_viewed"] = pd.to_numeric(
        coalesce_columns(df, ["weekly_hours_viewed"]), errors="coerce"
    )

    df["weekly_views"] = pd.to_numeric(
        coalesce_columns(df, ["weekly_views"]), errors="coerce"
    )

    df = add_business_keys(df)

    df = df[df["week"].notna()]

    df["performance_score"] = (
        (11 - df["weekly_rank"].fillna(10)).clip(lower=0)
        * (1 + np.log1p(df["cumulative_weeks_in_top_10"].fillna(0)))
    )

    return df


def prepare_alltime(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df["show_title"] = coalesce_columns(df, ["show_title"])
    df["category"] = coalesce_columns(df, ["category"])
    df["season_title"] = coalesce_columns(df, ["season_title"], default="No Season")

    df["hours_viewed_first_91_days"] = pd.to_numeric(
        coalesce_columns(df, ["hours_viewed_first_91_days"]), errors="coerce"
    )

    df["views_first_91_days"] = pd.to_numeric(
        coalesce_columns(df, ["views_first_91_days"]), errors="coerce"
    )

    df["runtime"] = pd.to_numeric(
        coalesce_columns(df, ["runtime"]), errors="coerce"
    )

    return add_business_keys(df)


def prepare_imdb(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df["show_title_key"] = normalize_text(coalesce_columns(df, ["show_title"]))
    df["imdb_rating"] = pd.to_numeric(coalesce_columns(df, ["rating"]), errors="coerce")
    df["imdb_votes"] = pd.to_numeric(coalesce_columns(df, ["votes"]), errors="coerce")

    return df[["show_title_key", "imdb_rating", "imdb_votes"]].drop_duplicates("show_title_key")


def prepare_genre(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df["show_title_key"] = normalize_text(coalesce_columns(df, ["show_title"]))
    df["genre"] = coalesce_columns(df, ["genre"])

    return df[["show_title_key", "genre"]].drop_duplicates("show_title_key")


# ----------------------------
# Build model
# ----------------------------

def build_model():
    files = locate_files()

    weekly_raw = choose_weekly_dataset(files)
    alltime_raw = read_dataset(files["global_alltime.xlsx"])
    imdb_raw = read_dataset(files["imdb_deduped.csv"])
    genre_raw = read_dataset(files["genre.csv"])

    weekly = prepare_weekly(weekly_raw)
    alltime = prepare_alltime(alltime_raw)
    imdb = prepare_imdb(imdb_raw)
    genre = prepare_genre(genre_raw)

    # DIM SHOW
    dim_show = (
        pd.concat([
            weekly[["show_business_key", "show_title", "season_title", "category", "show_title_key"]],
            alltime[["show_business_key", "show_title", "season_title", "category", "show_title_key"]],
        ])
        .drop_duplicates("show_business_key")
        .merge(imdb, on="show_title_key", how="left")
        .merge(genre, on="show_title_key", how="left")
        .reset_index(drop=True)
    )

    dim_show["show_key"] = np.arange(1, len(dim_show) + 1)

    # DIM DATE
    dim_date = weekly[["week"]].drop_duplicates().rename(columns={"week": "week_start_date"})
    dim_date["date_key"] = dim_date["week_start_date"].dt.strftime("%Y%m%d").astype(int)

    # DIM COUNTRY
    dim_country = weekly[["country_name", "country_iso2"]].drop_duplicates()
    dim_country["country_key"] = np.arange(1, len(dim_country) + 1)

    # DIM CATEGORY
    dim_category = weekly[["category"]].drop_duplicates()
    dim_category["category_key"] = np.arange(1, len(dim_category) + 1)

    # FACT WEEKLY
    fact_weekly = (
        weekly
        .merge(dim_show[["show_key", "show_business_key"]], on="show_business_key")
        .merge(dim_date, left_on="week", right_on="week_start_date")
        .merge(dim_country, on="country_name")
        .merge(dim_category, on="category")
    )

    # 🔥 FIX: enforce correct grain (1 row per show-country-week)
    fact_weekly = fact_weekly.drop_duplicates(
        subset=["show_key", "country_key", "date_key"],
        keep="first"
    )

    # FACT ALLTIME
    fact_alltime = alltime.merge(dim_show[["show_key", "show_business_key"]], on="show_business_key")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    dim_show.to_csv(MODEL_DIR / "dim_show.csv", index=False)
    dim_date.to_csv(MODEL_DIR / "dim_date.csv", index=False)
    dim_country.to_csv(MODEL_DIR / "dim_country.csv", index=False)
    dim_category.to_csv(MODEL_DIR / "dim_category.csv", index=False)
    fact_weekly.to_csv(MODEL_DIR / "fact_weekly_performance.csv", index=False)
    fact_alltime.to_csv(MODEL_DIR / "fact_alltime.csv", index=False)

    print("✅ Model built successfully")


if __name__ == "__main__":
    build_model()