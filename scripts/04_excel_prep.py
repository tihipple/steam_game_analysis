from pathlib import Path
import pandas as pd


# -----------------------------------
# Load the Cleaned Dataset
# Purpose: use the cleaned output from Phase 3 as the source for Excel analysis
# -----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLEANED_FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "steam_games_cleaned.csv"
)

df = pd.read_csv(
    CLEANED_FILE_PATH,
    parse_dates=["release_date"]
)


# -----------------------------------
# Create Excel Output Folder
# Purpose: keep Excel practice files separate from raw and cleaned data
# -----------------------------------

EXCEL_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "excel"
)

EXCEL_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# -----------------------------------
# Create Game Lookup Table
# Purpose: create a descriptive lookup table that can be joined in Excel using appid
# -----------------------------------

game_lookup = df[
    [
        "appid",
        "name",
        "developers",
        "publishers",
        "genres",
        "categories",
        "windows",
        "mac",
        "linux"
    ]
].copy()

print("\n--- Game Lookup Table ---")
print("Rows:", len(game_lookup))
print("Unique appids:", game_lookup["appid"].nunique())

print(game_lookup.head())

# -----------------------------------
# Create Game Metrics Table
# Purpose: create the main numerical table used for Excel analysis
# -----------------------------------

game_metrics = df[
    [
        "appid",
        "release_date",
        "price",
        "discount",
        "required_age",
        "metacritic_score",
        "positive",
        "negative",
        "calculated_review_total",
        "calculated_positive_pct",
        "num_reviews_total",
        "pct_pos_total",
        "owner_min",
        "owner_max",
        "owner_midpoint",
        "average_playtime_forever",
        "average_playtime_2weeks",
        "median_playtime_forever",
        "peak_ccu",
        "recommendations",
        "dlc_count"
    ]
].copy()

# -----------------------------------
# Create Date Fields for Excel
# Purpose: make common time-based analysis easier in PivotTables
# -----------------------------------

game_metrics["release_year"] = (
    game_metrics["release_date"].dt.year
)

game_metrics["release_month"] = (
    game_metrics["release_date"].dt.month
)

game_metrics["release_quarter"] = (
    game_metrics["release_date"].dt.quarter
)

# -----------------------------------
# Save Excel Practice Files
# Purpose: create separate datasets for lookup and analysis exercises
# -----------------------------------

LOOKUP_FILE = (
    EXCEL_OUTPUT_DIR
    / "game_lookup.csv"
)

METRICS_FILE = (
    EXCEL_OUTPUT_DIR
    / "game_metrics.csv"
)

game_lookup.to_csv(
    LOOKUP_FILE,
    index=False
)

game_metrics.to_csv(
    METRICS_FILE,
    index=False
)

print("\nGame lookup saved to:", LOOKUP_FILE)
print("Game metrics saved to:", METRICS_FILE)