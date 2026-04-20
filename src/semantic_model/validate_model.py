from pathlib import Path
import pandas as pd

BASE_DIR = Path().resolve()
MODEL_DIR = BASE_DIR / "data" / "processed" / "model"


def load_table(name):
    path = MODEL_DIR / name
    if not path.exists():
        print(f"❌ Missing: {name}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    print(f"✅ Loaded {name} ({len(df)} rows)")
    return df


def check_empty_tables(tables):
    print("\n🔍 Checking for empty tables...")
    for name, df in tables.items():
        if df.empty:
            print(f"❌ {name} is EMPTY")
        else:
            print(f"✅ {name} has data")


def check_keys(dim_show, dim_date, dim_country, dim_category):
    print("\n🔑 Checking primary keys...")

    print("Dim_Show:", "✅" if dim_show["show_key"].is_unique else "❌ duplicates")
    print("Dim_Date:", "✅" if dim_date["date_key"].is_unique else "❌ duplicates")
    print("Dim_Country:", "✅" if dim_country["country_key"].is_unique else "❌ duplicates")
    print("Dim_Category:", "✅" if dim_category["category_key"].is_unique else "❌ duplicates")


def check_foreign_keys(fact_weekly):
    print("\n🔗 Checking foreign keys in fact_weekly...")

    for col in ["show_key", "country_key", "date_key", "category_key"]:
        nulls = fact_weekly[col].isna().sum()
        if nulls > 0:
            print(f"❌ {col} has {nulls} NULLS")
        else:
            print(f"✅ {col} OK")


def check_fact_grain(fact_weekly):
    print("\n📊 Checking fact table grain...")

    duplicates = fact_weekly.duplicated(
        subset=["show_key", "country_key", "date_key"]
    ).sum()

    if duplicates > 0:
        print(f"❌ Duplicate grain rows: {duplicates}")
    else:
        print("✅ Grain is clean (no duplicates)")


def check_enrichment(dim_show):
    print("\n🎬 Checking enrichment (IMDb + Genre)...")

    imdb_rate = dim_show["imdb_rating"].notna().mean()
    genre_rate = dim_show["genre"].notna().mean()

    print(f"IMDb match rate: {imdb_rate:.2%}")
    print(f"Genre match rate: {genre_rate:.2%}")

    if imdb_rate < 0.5:
        print("⚠️ Low IMDb match rate")
    if genre_rate < 0.5:
        print("⚠️ Low genre match rate")


def check_relationship_coverage(dim_show, fact_weekly):
    print("\n🔗 Checking relationship coverage...")

    missing = fact_weekly["show_key"].isin(dim_show["show_key"]).mean()

    print(f"Show_key coverage: {missing:.2%}")

    if missing < 1:
        print("❌ Some fact rows not linked to dimension")
    else:
        print("✅ All fact rows linked correctly")


def run_all_checks():
    print("\n🚀 MODEL VALIDATION STARTED\n")

    dim_show = load_table("dim_show.csv")
    dim_date = load_table("dim_date.csv")
    dim_country = load_table("dim_country.csv")
    dim_category = load_table("dim_category.csv")
    fact_weekly = load_table("fact_weekly_performance.csv")
    fact_alltime = load_table("fact_alltime.csv")

    tables = {
        "dim_show": dim_show,
        "dim_date": dim_date,
        "dim_country": dim_country,
        "dim_category": dim_category,
        "fact_weekly": fact_weekly,
        "fact_alltime": fact_alltime,
    }

    check_empty_tables(tables)
    check_keys(dim_show, dim_date, dim_country, dim_category)

    if not fact_weekly.empty:
        check_foreign_keys(fact_weekly)
        check_fact_grain(fact_weekly)
        check_relationship_coverage(dim_show, fact_weekly)

    if not dim_show.empty:
        check_enrichment(dim_show)

    print("\n✅ VALIDATION COMPLETE\n")


if __name__ == "__main__":
    run_all_checks()