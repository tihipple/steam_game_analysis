# -----------------------------------
# Imports
# Purpose: Load tools needed to build
#          the publisher bridge table.
# -----------------------------------

from pathlib import Path
import pandas as pd
import ast


# -----------------------------------
# File Paths
# Purpose: Define project input/output
#          locations.
# -----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "steam_games_cleaned.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "excel"
    / "publisher_bridge.csv"
)


# -----------------------------------
# Load Data
# Purpose: Start from the cleaned
#          Steam dataset.
# -----------------------------------

df = pd.read_csv(INPUT_FILE)

print("Rows in source:", len(df))
print("Unique appids:", df["appid"].nunique())

# -----------------------------------
# Parse Publisher Lists
# Purpose: Convert publisher strings
#          into actual Python lists.
# -----------------------------------

def parse_list(value):
    if pd.isna(value):
        return []

    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []


df["publisher_list"] = df["publishers"].apply(parse_list)


# -----------------------------------
# Create Publisher Bridge
# Purpose: Create one row per
#          appid + publisher.
# -----------------------------------

publisher_bridge = (
    df[["appid", "publisher_list"]]
    .explode("publisher_list")
    .rename(columns={"publisher_list": "publisher"})
)


# -----------------------------------
# Remove Missing Publishers
# Purpose: Keep only valid publisher
#          relationships.
# -----------------------------------

publisher_bridge = publisher_bridge[
    publisher_bridge["publisher"].notna()
    & (publisher_bridge["publisher"] != "")
]
# -----------------------------------
# Inspect Duplicate Relationships
# Purpose: Review repeated appid +
#          publisher combinations
#          before removing them.
# -----------------------------------

duplicate_pairs = publisher_bridge[
    publisher_bridge.duplicated(
        subset=["appid", "publisher"],
        keep=False
    )
].sort_values(["appid", "publisher"])

print("\nDuplicate publisher relationships:")
print(duplicate_pairs)

# -----------------------------------
# Remove Duplicate Relationships
# Purpose: Keep one unique row per
#          appid + publisher.
# -----------------------------------

publisher_bridge = publisher_bridge.drop_duplicates(
    subset=["appid", "publisher"]
)

# -----------------------------------
# Validation
# Purpose: Check bridge-table grain
#          and basic data quality.
# -----------------------------------

print("\nPublisher bridge rows:", len(publisher_bridge))
print(
    "Unique appids with publishers:",
    publisher_bridge["appid"].nunique()
)

print(
    "Duplicate appid + publisher pairs:",
    publisher_bridge.duplicated(
        subset=["appid", "publisher"]
    ).sum()
)

print("\nSample:")
print(publisher_bridge.head(10))


# -----------------------------------
# Save Output
# Purpose: Export bridge table for
#          spreadsheet analysis.
# -----------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

publisher_bridge.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    "\nSaved publisher bridge to:",
    OUTPUT_FILE
)