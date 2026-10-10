# ----------------------
# Phase 2: Data Quality Validation
# ----------------------

import pandas as pd
from pathlib import Path


# -----------------------------------
# Define the project root and file path
# Purpose: create a reliable path to the raw Steam dataset
# -----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "steam_large_dataset"
    / "games_march2025_full.csv"
)


# -----------------------------------
# Read the full dataset
# Purpose: load the raw dataset so we can profile and validate it
# -----------------------------------

df = pd.read_csv(FILE_PATH)


# -----------------------------------
# Column Profile
# Purpose: understand the columns and identify likely data-quality risks
# -----------------------------------

# Here we move onto understanding the columns and identifying likely
# data-quality risks.

print("\n--- Column Profile ---")

profile = pd.DataFrame({
    "column": df.columns,
    "data_type": df.dtypes.astype(str).values,
    "null_count": df.isnull().sum().values,
    "null_percent": (df.isnull().mean() * 100).round(2).values,
    "unique_values": df.nunique(dropna=False).values
})

print(profile.to_string(index=False))


# -----------------------------------
# Suspicious / Important Field Review
# Purpose: inspect fields that may contain data-quality issues
# -----------------------------------

# Now we can move into inspecting the data for suspicious or important fields.
# This is where we start to look for potential data-quality issues, such as
# missing values, duplicates, or unexpected data types.
#
# We also want to identify any fields that are particularly important for our
# analysis, such as primary keys or measures.

print("\n--- Suspicious / Important Field Review ---")


# -----------------------------------
# Missing Names
# Purpose: inspect the actual records that have missing names
# -----------------------------------

# We don't want to automatically delete them.
# We start by understanding them.

print("\nRows with missing names:")

print(
    df[df["name"].isnull()][
        ["appid", "name", "release_date", "developers", "publishers"]
    ].to_string(index=False)
)


# -----------------------------------
# Release Date Validation
# Purpose: determine whether all release_date values can be interpreted as dates
# -----------------------------------

print("\nRelease date sample:")

print(df["release_date"].head(20))

# Here we convert the column into a datetime object.
#
# errors="coerce" means that if a value cannot be converted to a datetime,
# it will be set to NaT (Not a Time), which is the datetime equivalent of
# NaN (Not a Number).
#
# This is useful for identifying invalid or missing dates in the dataset.

release_date_test = pd.to_datetime(
    df["release_date"],
    errors="coerce"
)

print(
    "\nRelease dates that could not be converted:",
    release_date_test.isnull().sum()
)


# -----------------------------------
# Estimated Owners Review
# Purpose: understand what kind of field estimated_owners actually is
# -----------------------------------

# Here we ask, what kind of field is this actually?
#
# We saw 15 different values, but there are almost 95,000 rows.
# 0-20000, 20000-50000, and 50000-100000 are bucketed ranges stored as text.
#
# So we know that estimated_owners is a categorical range that represents
# a numeric concept.

print("\nEstimated owner values:")

print(
    df["estimated_owners"]
    .value_counts()
    .sort_index()
)


# -----------------------------------
# Positive Review Percentage Validation
# Purpose: check whether percentage values stay within the expected 0-100 range
# -----------------------------------

# Now we're finding out the statistical boundaries of these percentage fields.
#
# We saw min = -1 and max = 100, which is odd because -1% doesn't make sense
# as a positive-review percentage.
#
# So we filter and find the rows that are below zero OR above 100.

print("\nPositive review percentage range:")

print(
    df[
        ["pct_pos_total", "pct_pos_recent"]
    ].describe()
)

print("\nValues outside expected 0-100 range:")

print(
    df[
        (df["pct_pos_total"] < 0)
        | (df["pct_pos_total"] > 100)
    ][
        ["appid", "name", "pct_pos_total"]
    ].head(20)
)


# -----------------------------------
# Numeric Field Summary
# Purpose: identify impossible or extreme values across important numeric fields
# -----------------------------------

numeric_fields = [
    "price",
    "required_age",
    "dlc_count",
    "metacritic_score",
    "recommendations",
    "positive",
    "negative",
    "average_playtime_forever",
    "discount",
    "peak_ccu"
]

# Here we're trying to find the rows that have impossible or extreme values.
#
# We noticed things like:
# required_age min = -1
#   - logically suspicious because age cannot be negative
#
# price max = 999.98
#   - extreme, but it could still be valid
#
# dlc_count max = 3427
#
# average_playtime_forever max = 1462997

print("\n--- Numeric Field Summary ---")

print(
    df[numeric_fields]
    .describe()
    .T
)


# -----------------------------------
# Check -1 Percentage Values
# Purpose: understand what pct_pos_total = -1 actually represents
# -----------------------------------

# Here we only want to see the records where pct_pos_total equals -1.

print("\n--- Checking -1 percentage values ---")

pct_negative_one = df[
    df["pct_pos_total"] == -1
]

print(
    "Rows with pct_pos_total = -1:",
    len(pct_negative_one)
)

# len(pct_negative_one) showed 39,575, so this is not a weird one-off.
# It affects a huge portion of the dataset.
#
# Now we need to try and infer what -1 actually means.

print(
    pct_negative_one[
        [
            "appid",
            "name",
            "positive",
            "negative",
            "num_reviews_total",
            "pct_pos_total"
        ]
    ].head(20).to_string(index=False)
)

# -1 likely means the derived percentage metric was unavailable or not
# populated, not necessarily that the game had no reviews.


# -----------------------------------
# Required Age Validation
# Purpose: identify impossible negative age requirements
# -----------------------------------

print("\n--- Invalid Required Age Values ---")

# Now we want it to show us the records with an impossible
# negative age requirement.

print(
    df[df["required_age"] < 0][
        ["appid", "name", "required_age"]
    ].head(20).to_string(index=False)
)

# We found one record, so it looks like an invalid record.
# Eventually we can convert negative required_age values to null.


# -----------------------------------
# Metacritic Score Review
# Purpose: determine whether a score of 0 is being used to represent missing data
# -----------------------------------

print("\n--- Metacritic Score Distribution ---")

print(
    df["metacritic_score"]
    .value_counts()
    .sort_index()
    .head(20)
)

print(
    "\nGames with Metacritic score of 0:",
    (df["metacritic_score"] == 0).sum()
)

# Here we found 91,372 rows have metacritic_score = 0.
# That's about 96% of the dataset.
#
# Earlier we saw that ~96% of metacritic_url was missing.
#
# So now we have evidence that metacritic_score = 0 probably means
# no Metacritic score is available.


# -----------------------------------
# Price Outlier Review
# Purpose: inspect the highest-priced records before deciding whether they are invalid
# -----------------------------------

# Now we want to see the highest priced games in the dataset.

print("\n--- Highest Priced Games ---")

print(
    df[
        [
            "appid",
            "name",
            "price",
            "developers",
            "publishers"
        ]
    ]
    .sort_values("price", ascending=False)
    .head(20)
    .to_string(index=False)
)

# We saw The Leverage Game Business Edition,
# Ascent Free-Roaming VR Experience,
# and Houdini Indie.
#
# These aren't necessarily normal consumer games and look like they could be
# business software or training tools.
#
# So high prices are outliers, but not necessarily invalid.

# -----------------------------------
# Sentinel Value Summary
# Purpose: count special values that may represent unavailable data
# -----------------------------------

print("\n--- Sentinel Value Checks ---")

print(
    "pct_pos_total = -1:",
    (df["pct_pos_total"] == -1).sum()
)

print(
    "pct_pos_recent = -1:",
    (df["pct_pos_recent"] == -1).sum()
)

print(
    "num_reviews_total = -1:",
    (df["num_reviews_total"] == -1).sum()
)

print(
    "num_reviews_recent = -1:",
    (df["num_reviews_recent"] == -1).sum()
)

print(
    "metacritic_score = 0:",
    (df["metacritic_score"] == 0).sum()
)

# These counts help us understand how often special values like -1 or 0
# are being used instead of normal missing values.
#
# We do not change them yet.
# We are only validating how they are represented in the source.


# -----------------------------------
# Review Count Consistency Check
# Purpose: compare positive + negative reviews against num_reviews_total
# -----------------------------------

print("\n--- Review Count Consistency Check ---")

review_check = df[
    [
        "appid",
        "name",
        "positive",
        "negative",
        "num_reviews_total",
        "pct_pos_total"
    ]
].copy()

# Create our own calculated review total so we can compare it
# against the provided num_reviews_total field.

review_check["calculated_total"] = (
    review_check["positive"]
    + review_check["negative"]
)

# Calculate the difference between the source field and our calculation.

review_check["total_difference"] = (
    review_check["num_reviews_total"]
    - review_check["calculated_total"]
)

print("\nMost common differences between provided and calculated review totals:")

print(
    review_check["total_difference"]
    .value_counts()
    .head(20)
)

# Now count how many rows match exactly.

exact_review_matches = (
    review_check["total_difference"] == 0
).sum()

print(
    "\nRows where num_reviews_total matches positive + negative:",
    exact_review_matches
)

print(
    "Rows where they do not match:",
    len(review_check) - exact_review_matches
)


# -----------------------------------
# Inspect Review Count Mismatches
# Purpose: look at actual records where the review totals do not agree
# -----------------------------------

review_mismatches = review_check[
    review_check["total_difference"] != 0
]

print("\nSample review count mismatches:")

print(
    review_mismatches[
        [
            "appid",
            "name",
            "positive",
            "negative",
            "num_reviews_total",
            "calculated_total",
            "total_difference"
        ]
    ].head(20).to_string(index=False)
)

# We do not automatically assume one field is wrong.
#
# If the fields disagree, they may come from different source systems,
# represent different review populations, or use different timing rules.


# -----------------------------------
# Positive Review Percentage Consistency Check
# Purpose: compare pct_pos_total against a percentage calculated from
# positive and negative reviews
# -----------------------------------

print("\n--- Positive Review Percentage Consistency Check ---")

# Only calculate a percentage where positive + negative is greater than 0.

valid_review_rows = review_check[
    review_check["calculated_total"] > 0
].copy()

valid_review_rows["calculated_pct_positive"] = (
    valid_review_rows["positive"]
    / valid_review_rows["calculated_total"]
    * 100
)

# Round the calculated value because the source pct_pos_total field
# appears to be stored as a whole number.

valid_review_rows["calculated_pct_positive_rounded"] = (
    valid_review_rows["calculated_pct_positive"]
    .round()
)

# Compare only rows where the source percentage is valid
# and not using the -1 sentinel value.

valid_pct_rows = valid_review_rows[
    valid_review_rows["pct_pos_total"] >= 0
].copy()

valid_pct_rows["pct_difference"] = (
    valid_pct_rows["pct_pos_total"]
    - valid_pct_rows["calculated_pct_positive_rounded"]
)

print("\nMost common percentage differences:")

print(
    valid_pct_rows["pct_difference"]
    .value_counts()
    .head(20)
)

print(
    "\nExact percentage matches:",
    (valid_pct_rows["pct_difference"] == 0).sum()
)

print(
    "Percentage mismatches:",
    (valid_pct_rows["pct_difference"] != 0).sum()
)


# -----------------------------------
# Inspect Percentage Mismatches
# Purpose: review records where the provided percentage differs
# from our calculated percentage
# -----------------------------------

pct_mismatches = valid_pct_rows[
    valid_pct_rows["pct_difference"] != 0
]

print("\nSample percentage mismatches:")

print(
    pct_mismatches[
        [
            "appid",
            "name",
            "positive",
            "negative",
            "pct_pos_total",
            "calculated_pct_positive_rounded",
            "pct_difference"
        ]
    ].head(20).to_string(index=False)
)


# -----------------------------------
# Numeric Range Validation
# Purpose: identify values that violate basic logical rules
# -----------------------------------

print("\n--- Numeric Range Validation ---")

print(
    "Negative prices:",
    (df["price"] < 0).sum()
)

print(
    "Discounts below 0:",
    (df["discount"] < 0).sum()
)

print(
    "Discounts above 100:",
    (df["discount"] > 100).sum()
)

print(
    "Negative average playtime:",
    (df["average_playtime_forever"] < 0).sum()
)

print(
    "Negative recent average playtime:",
    (df["average_playtime_2weeks"] < 0).sum()
)

print(
    "Negative peak CCU:",
    (df["peak_ccu"] < 0).sum()
)

print(
    "Negative positive-review counts:",
    (df["positive"] < 0).sum()
)

print(
    "Negative negative-review counts:",
    (df["negative"] < 0).sum()
)

# These are basic logical checks.
#
# For fields like price, playtime, CCU, and review counts,
# negative values would normally be invalid.


# -----------------------------------
# Platform Availability Check
# Purpose: identify records that do not support Windows, Mac, or Linux
# -----------------------------------

print("\n--- Platform Availability Check ---")

no_platform = df[
    (~df["windows"])
    & (~df["mac"])
    & (~df["linux"])
]

print(
    "Rows where Windows, Mac, and Linux are all False:",
    len(no_platform)
)

print("\nSample records with no supported platform:")

print(
    no_platform[
        [
            "appid",
            "name",
            "windows",
            "mac",
            "linux"
        ]
    ].head(20).to_string(index=False)
)

# If records exist here, they are worth reviewing.
#
# A Steam application with no supported operating system may represent
# unavailable, unreleased, incorrectly scraped, or unusual application data.


# -----------------------------------
# Missing Important Descriptive Fields
# Purpose: quantify missing values in fields that may matter for analysis
# -----------------------------------

print("\n--- Important Field Completeness ---")

important_fields = [
    "name",
    "developers",
    "publishers",
    "genres",
    "categories"
]

for column in important_fields:
    print(
        f"{column} missing values:",
        df[column].isnull().sum()
    )

# Even if a field has no true nulls, some values may still be empty strings
# or contain empty list representations.
#
# Those can be checked later during cleaning if needed.


# -----------------------------------
# Phase 2 Conclusion
# Purpose: summarize the validation findings and define cleaning rules
# -----------------------------------

# Phase 2 is complete.
#
# We identified the following cleaning rules:
#
# - Convert release_date to datetime.
# - Convert -1 sentinel values in the derived review fields to null.
# - Convert negative required_age values to null.
# - Treat metacritic_score = 0 as unavailable rather than a true score.
# - Preserve source review metrics because num_reviews_total does not
#   consistently equal positive + negative.
# - Consider creating separate calculated review metrics rather than
#   overwriting the source fields.
# - Parse estimated_owners into usable numeric fields.
# - Inspect the two records with missing names.
# - Preserve extreme price, playtime, DLC, and CCU values unless further
#   evidence shows that they are invalid.
#
# Next:
# Phase 3 - Data Cleaning and Transformation