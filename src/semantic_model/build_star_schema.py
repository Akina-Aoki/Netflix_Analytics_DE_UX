from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path().resolve()
DATA_DIR = BASE_DIR / "data" / "raw"
MODEL_DIR = BASE_DIR / "data" / "processed" / "model"


# ----------------------------
# Helpers
# ----------------------------

def clean_cols(df):
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def norm(series):
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )


# ----------------------------
# Load
# ----------------------------

def load():
    gw = clean_cols(pd.read_excel(DATA_DIR / "global_weekly.xlsx"))
    ga = clean_cols(pd.read_excel(DATA_DIR / "global_alltime.xlsx"))
    cw = clean_cols(pd.read_excel(DATA_DIR / "country_weekly.xlsx"))
    imdb = clean_cols(pd.read_csv(DATA_DIR / "imdb_deduped.csv"))
    genre = clean_cols(pd.read_csv(DATA_DIR / "genre.csv"))

    return gw, ga, cw, imdb, genre


# ----------------------------
# Keys
# ----------------------------

def add_keys(df):
    df["season_title"] = df["season_title"].fillna("No Season")

    df["show_title_key"] = norm(df["show_title"])

    df["show_business_key"] = (
        norm(df["show_title"])
        + "|"
        + norm(df["category"])
        + "|"
        + norm(df["season_title"])
    )

    return df


# ----------------------------
# Build
# ----------------------------

def build():

    gw, ga, cw, imdb, genre = load()

    # ---- Prep ----
    gw["week"] = pd.to_datetime(gw["week"])
    ga["week"] = pd.to_datetime(ga["week"])

    gw = add_keys(gw)
    ga = add_keys(ga)
    cw = add_keys(cw)

    # ----------------------------
    # DIM SHOW
    # ----------------------------
    dim_show = pd.concat([
        gw[["show_business_key", "show_title", "season_title", "category", "show_title_key"]],
        ga[["show_business_key", "show_title", "season_title", "category", "show_title_key"]],
        cw[["show_business_key", "show_title", "season_title", "category", "show_title_key"]],
    ]).drop_duplicates("show_business_key")

    # IMDb enrichment
    imdb["show_title_key"] = norm(imdb["show_title"])
    imdb["imdb_rating"] = pd.to_numeric(imdb["rating"], errors="coerce")

    dim_show = dim_show.merge(
        imdb[[
            "show_title_key",
            "imdb_rating",
            "trailer",
            "image",
            "imdb_url",
            "cast_members",
            "description"
        ]],
        on="show_title_key",
        how="left"
    )

    # Genre enrichment
    genre["show_title_key"] = norm(genre["show_title"])

    genre_grouped = (
        genre.groupby("show_title_key")["genre"]
        .apply(lambda x: ", ".join(sorted(set(x))))
        .reset_index()
    )

    dim_show = dim_show.merge(genre_grouped, on="show_title_key", how="left")

    dim_show = dim_show.reset_index(drop=True)
    dim_show["show_key"] = np.arange(1, len(dim_show) + 1)

    # ----------------------------
    # DIM DATE
    # ----------------------------
    dim_date = gw[["week"]].drop_duplicates()
    dim_date = dim_date.rename(columns={"week": "week_start_date"})
    dim_date["date_key"] = dim_date["week_start_date"].dt.strftime("%Y%m%d").astype(int)

    # ----------------------------
    # DIM COUNTRY
    # ----------------------------
    dim_country = gw[["country_name", "country_iso2"]].drop_duplicates()
    dim_country["country_key"] = np.arange(1, len(dim_country) + 1)

    # ----------------------------
    # DIM CATEGORY
    # ----------------------------
    dim_category = gw[["category"]].drop_duplicates()
    dim_category["category_key"] = np.arange(1, len(dim_category) + 1)

    # ----------------------------
    # FACT WEEKLY (🔥 FIXED)
    # ----------------------------
    fact_weekly = (
        gw
        .merge(dim_show[["show_key", "show_business_key"]], on="show_business_key")
        .merge(dim_date, left_on="week", right_on="week_start_date")
        .merge(dim_country, on="country_name")
        .merge(dim_category, on="category")
    )

    # 🔥 IMPORTANT: ensure key exists
    # (comes from gw, not dim_show)
    assert "show_title_key" in fact_weekly.columns

    # Join global_alltime metrics correctly
    ga_small = ga[[
        "show_title_key",
        "week",
        "weekly_hours_viewed",
        "weekly_views",
        "runtime"
    ]]

    fact_weekly = fact_weekly.merge(
        ga_small,
        on=["show_title_key", "week"],
        how="left"
    )

    # KPI
    fact_weekly["performance_score"] = (
        (11 - fact_weekly["weekly_rank"])
        * np.log1p(fact_weekly["cumulative_weeks_in_top_10"])
    )

    # Enforce grain
    fact_weekly = fact_weekly.drop_duplicates(
        subset=["show_key", "country_key", "date_key"]
    )

    # ----------------------------
    # FACT ALLTIME
    # ----------------------------
    fact_alltime = cw.merge(
        dim_show[["show_key", "show_business_key"]],
        on="show_business_key"
    )

    # ----------------------------
    # SAVE
    # ----------------------------
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    dim_show.to_csv(MODEL_DIR / "dim_show.csv", index=False)
    dim_date.to_csv(MODEL_DIR / "dim_date.csv", index=False)
    dim_country.to_csv(MODEL_DIR / "dim_country.csv", index=False)
    dim_category.to_csv(MODEL_DIR / "dim_category.csv", index=False)
    fact_weekly.to_csv(MODEL_DIR / "fact_weekly_performance.csv", index=False)
    fact_alltime.to_csv(MODEL_DIR / "fact_alltime.csv", index=False)

    print("✅ CLEAN STAR SCHEMA BUILT")


if __name__ == "__main__":
    build()