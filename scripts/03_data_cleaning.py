from pathlib import Path
import pandas as pd


# -----------------------------------
# Load the Raw Dataset
# Purpose: start from the original full dataset before applying cleaning rules
# -----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "steam_large_dataset"
    / "games_march2025_full.csv"
)

df = pd.read_csv(FILE_PATH)


# -----------------------------------
# Create Cleaned Output Path
# Purpose: keep the cleaned dataset separate from the raw source file
# -----------------------------------

CLEANED_FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "steam_games_cleaned.csv"
)

# -----------------------------------
# Convert Release Date to Datetime
# Purpose: store release_date as a true date field instead of text
# -----------------------------------

# In Phase 2, we confirmed that all release_date values could be
# successfully converted to datetime.
#
# Since there were 0 failed conversions, we can safely convert
# the original field here.

df["release_date"] = pd.to_datetime(
    df["release_date"]
)
print("\n--- Release Date Cleaning ---")
print("release_date datatype:", df["release_date"].dtype)

# -----------------------------------
# Replace Review Sentinel Values
# Purpose: convert -1 values that represent unavailable review data to null
# -----------------------------------

review_sentinel_fields = [
    "pct_pos_total",
    "pct_pos_recent",
    "num_reviews_total",
    "num_reviews_recent"
]

for column in review_sentinel_fields:
    df[column] = df[column].replace(-1, pd.NA)


# Validate that the sentinel values were removed

print("\n--- Review Sentinel Cleaning ---")

for column in review_sentinel_fields:
    print(
        f"{column} remaining -1 values:",
        (df[column] == -1).sum()
    )

    print(
        f"{column} null values:",
        df[column].isnull().sum()
    )

# -----------------------------------
# Clean Invalid Required Age Values
# Purpose: replace impossible negative age requirements with null
# -----------------------------------

df.loc[
    df["required_age"] < 0,
    "required_age"
] = pd.NA

print("\n--- Required Age Cleaning ---")

print(
    "Negative required_age values remaining:",
    (df["required_age"] < 0).sum()
)

print(
    "Missing required_age values:",
    df["required_age"].isnull().sum()
)

# -----------------------------------
# Clean Missing Metacritic Scores
# Purpose: treat 0 as unavailable rather than as a true Metacritic score
# -----------------------------------

df["metacritic_score"] = (
    df["metacritic_score"]
    .replace(0, pd.NA)
)

print("\n--- Metacritic Cleaning ---")

print(
    "Metacritic scores equal to 0:",
    (df["metacritic_score"] == 0).sum()
)

print(
    "Missing Metacritic scores:",
    df["metacritic_score"].isnull().sum()
)

# -----------------------------------
# Inspect Missing Game Names
# Purpose: understand the two records with missing names before deciding how to clean them
# -----------------------------------

print("\n--- Missing Name Review ---")

missing_names = df[
    df["name"].isnull()
]

print(
    missing_names[
        [
            "appid",
            "name",
            "release_date",
            "developers",
            "publishers",
            "genres"
        ]
    ].to_string(index=False)
)
# -----------------------------------
# Handle Missing Game Names
# Purpose: preserve missing names while flagging records for later analysis
# -----------------------------------

# We found two records with missing names.
#
# We do not have enough information to safely assign a game title,
# so we will preserve the null values rather than inventing "Unknown"
# or deleting the records.

df["name_missing_flag"] = df["name"].isnull()

print("\n--- Missing Name Cleaning ---")

print(
    "Missing names:",
    df["name"].isnull().sum()
)

print(
    "Records flagged as missing name:",
    df["name_missing_flag"].sum()
)

# -----------------------------------
# Transform Estimated Owners
# Purpose: convert ownership ranges stored as text into usable numeric fields
# -----------------------------------

owner_ranges = (
    df["estimated_owners"]
    .str.split(" - ", expand=True)
)

df["owner_min"] = pd.to_numeric(
    owner_ranges[0],
    errors="coerce"
)

df["owner_max"] = pd.to_numeric(
    owner_ranges[1],
    errors="coerce"
)

df["owner_midpoint"] = (
    df["owner_min"]
    + df["owner_max"]
) / 2
print("\n--- Estimated Owners Transformation ---")

print(
    df[
        [
            "estimated_owners",
            "owner_min",
            "owner_max",
            "owner_midpoint"
        ]
    ].head(20)
)

print(
    "\nMissing owner_min values:",
    df["owner_min"].isnull().sum()
)

print(
    "Missing owner_max values:",
    df["owner_max"].isnull().sum()
)
# -----------------------------------
# Create Calculated Review Metrics
# Purpose: create transparent review measures based directly on
# positive and negative review counts
# -----------------------------------

# In Phase 2, we found that num_reviews_total does not consistently equal
# positive + negative.
#
# We also found that pct_pos_total does not always match the percentage
# calculated from positive and negative reviews.
#
# Instead of overwriting the source fields, we preserve them and create
# our own clearly named calculated fields.

df["calculated_review_total"] = (
    df["positive"]
    + df["negative"]
)

# Calculate positive review percentage only when there is at least one review.
# If there are no reviews, leave the value as null.

df["calculated_positive_pct"] = (
    df["positive"]
    .div(df["calculated_review_total"])
    .mul(100)
    .where(df["calculated_review_total"] > 0)
    .round(2)
)


# -----------------------------------
# Validate Calculated Review Metrics
# Purpose: confirm the new calculated fields behave as expected
# -----------------------------------

print("\n--- Calculated Review Metrics ---")

print(
    df[
        [
            "name",
            "positive",
            "negative",
            "calculated_review_total",
            "calculated_positive_pct",
            "num_reviews_total",
            "pct_pos_total"
        ]
    ].head(20).to_string(index=False)
)

print(
    "\nNegative calculated review totals:",
    (df["calculated_review_total"] < 0).sum()
)

print(
    "Calculated percentages below 0:",
    (df["calculated_positive_pct"] < 0).sum()
)

print(
    "Calculated percentages above 100:",
    (df["calculated_positive_pct"] > 100).sum()
)

print(
    "Games with no calculated review percentage:",
    df["calculated_positive_pct"].isnull().sum()
)
# -----------------------------------
# Inspect List-Like Fields
# Purpose: understand how multi-value categorical fields are stored
# before deciding how to transform them
# -----------------------------------

list_like_fields = [
    "genres",
    "categories",
    "developers",
    "publishers",
    "tags",
    "supported_languages",
    "full_audio_languages"
]

print("\n--- List-Like Field Review ---")

for column in list_like_fields:
    print(f"\n{column}:")
    print(df[column].head(5).to_string(index=False))

print("\n--- Empty List Checks ---")

for column in list_like_fields:
    empty_list_count = (df[column] == "[]").sum()

    print(
        f"{column} empty list values:",
        empty_list_count
    )

# -----------------------------------
# Clean Empty List Values
# Purpose: convert empty list strings into proper null values
# -----------------------------------

list_like_fields = [
    "genres",
    "categories",
    "developers",
    "publishers",
    "tags",
    "supported_languages",
    "full_audio_languages"
]

for column in list_like_fields:
    df[column] = df[column].replace("[]", pd.NA)


# -----------------------------------
# Validate Empty List Cleaning
# Purpose: confirm that empty list strings were converted to null
# -----------------------------------

print("\n--- Empty List Cleaning ---")

for column in list_like_fields:
    print(
        f"{column} remaining [] values:",
        (df[column] == "[]").sum()
    )

    print(
        f"{column} null values:",
        df[column].isnull().sum()
    )

# -----------------------------------
# Final Cleaning Validation
# Purpose: confirm that cleaning rules were applied correctly
# and that the dataset still preserves its original grain
# -----------------------------------

print("\n--- Final Cleaning Validation ---")

print("Total rows:", len(df))
print("Unique appids:", df["appid"].nunique())
print("Duplicate appids:", df["appid"].duplicated().sum())
print("Missing appids:", df["appid"].isnull().sum())

print(
    "Release date datatype:",
    df["release_date"].dtype
)

print(
    "Negative required_age values:",
    (df["required_age"] < 0).sum()
)

print(
    "Metacritic scores equal to 0:",
    (df["metacritic_score"] == 0).sum()
)

print(
    "pct_pos_total values equal to -1:",
    (df["pct_pos_total"] == -1).sum()
)

print(
    "pct_pos_recent values equal to -1:",
    (df["pct_pos_recent"] == -1).sum()
)

print(
    "num_reviews_total values equal to -1:",
    (df["num_reviews_total"] == -1).sum()
)

print(
    "num_reviews_recent values equal to -1:",
    (df["num_reviews_recent"] == -1).sum()
)
# -----------------------------------
# Save Cleaned Dataset
# Purpose: create a separate cleaned file while preserving the raw source
# -----------------------------------

CLEANED_FILE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    CLEANED_FILE_PATH,
    index=False
)

print(
    "\nCleaned dataset saved to:",
    CLEANED_FILE_PATH
)
# -----------------------------------
# Save Cleaned Dataset
# Purpose: save the cleaned version separately while preserving the raw source
# -----------------------------------

CLEANED_FILE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    CLEANED_FILE_PATH,
    index=False
)
