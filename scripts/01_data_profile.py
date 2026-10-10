### Phase 1: Understanding the Data

from pathlib import Path
import pandas as pd


# -----------------------------------
# Define the Project Root and File Path
# Purpose: create a reliable path to the raw dataset
# -----------------------------------

# Path makes file paths a bit cleaner and more reliable instead of having
# to manually type out the full string path to the file.

# __file__ means the current file that's running.
# Path(__file__) means the path to the current file.
# resolve() means get the absolute path.
# parent means go up one directory.
# parent.parent means go up two directories.
#
# PROJECT_ROOT is the root directory of the project, which is two levels
# up from the current file.

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Now we build the path to the data file by joining the project root with
# the relative path to the data file.
#
# This way, we don't have to hardcode the full path to the data file,
# which makes our code more portable and easier to maintain.

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "steam_large_dataset"
    / "games_march2025_full.csv"
)


# -----------------------------------
# Load a Sample of the Dataset
# Purpose: understand the structure without loading the entire dataset yet
# -----------------------------------

# Now we can read the CSV file and put it into a dataframe.
#
# nrows=1000 means we only read the first 1000 rows of the CSV file,
# which is useful for profiling the data without loading the entire
# dataset into memory.
#
# We're not analyzing the entire dataset yet. We're just trying to
# understand the structure.

df_sample = pd.read_csv(FILE_PATH, nrows=1000)


# -----------------------------------
# Review Dataset Shape
# Purpose: understand how many rows and columns are in the sample
# -----------------------------------

# .shape gives us the number of rows and columns in the dataframe.
#
# So if it prints (1000, 20), that means there are
# 1000 rows and 20 columns in the dataframe.

print("Shape:")
print(df_sample.shape)


# -----------------------------------
# Review Column Names
# Purpose: understand what data is available in the dataset
# -----------------------------------

# .columns gives us the column names of the dataframe.
#
# .tolist() converts the column names from an index object to a list,
# which is easier to read and work with.

print("\nColumns:")
print(df_sample.columns.tolist())


# -----------------------------------
# Review Sample Records
# Purpose: get a quick look at what the actual data looks like
# -----------------------------------

# .head() gives us the first 5 rows of the dataframe.
#
# This is useful for getting a quick look at the values and understanding
# how the fields are populated.

print("\nFirst 5 rows:")
print(df_sample.head())


# -----------------------------------
# Review Data Types
# Purpose: understand what type of data pandas assigned to each field
# -----------------------------------

# .dtypes gives us the data types of each column.
#
# This helps us understand what kind of data we're working with and
# whether some fields may eventually need to be converted.

print("\nData types:")
print(df_sample.dtypes)


# -----------------------------------
# Review Missing Values
# Purpose: identify which fields contain missing data
# -----------------------------------

# .isnull().sum() gives us the number of missing values in each column.
#
# This is useful for understanding the quality of the data and identifying
# fields that may need more investigation later.

print("\nMissing values:")
print(
    df_sample
    .isnull()
    .sum()
    .sort_values(ascending=False)
)


# -----------------------------------
# Begin Understanding the Grain
# Purpose: determine what one row in the dataset represents
# -----------------------------------

# Now we can start asking questions about the data:
#
# What does each field mean?
# Which one looks like the primary key?
# Which ones are measures?
# Which ones are dimensions?
#
# First, we ask:
# What does one row represent?

print("\n--- Grain Check ---")


# -----------------------------------
# Check Sample Row Count
# Purpose: establish how many records are in the sample
# -----------------------------------

# How many rows are in my sample?

print("Sample row count:", len(df_sample))


# -----------------------------------
# Check Unique AppIDs
# Purpose: test whether appid may uniquely identify each row
# -----------------------------------

# How many unique AppIDs are in my sample?

print("Unique AppIDs:", df_sample["appid"].nunique())


# -----------------------------------
# Check Duplicate AppIDs
# Purpose: determine whether the same appid appears more than once
# -----------------------------------

# How many rows reuse the same appid?

print(
    "Duplicate AppIDs:",
    df_sample["appid"].duplicated().sum()
)

# From here, we saw that there are 1000 rows in the sample and
# 1000 unique AppIDs.
#
# This suggests that each row represents one unique Steam application
# record and that appid may be a good primary key candidate.
#
# But we don't want to assume that one row = one unique game title,
# because some games may have the same name but different AppIDs.
#
# So we need to check game names as well.


# -----------------------------------
# Compare AppID and Game Name
# Purpose: see whether different AppIDs can share the same game name
# -----------------------------------

# Now we inspect the appid and name together.

print(
    df_sample[
        ["appid", "name"]
    ].head(20)
)

# We saw that Tom Clancy's Rainbow Six Siege appears multiple times with
# different AppIDs.
#
# This means that there are multiple Steam application records associated
# with the same game title.
#
# So now we know:
#
# appid = unique
# name = not unique
#
# This tells us that name cannot be used as a primary key.


# -----------------------------------
# Count Duplicate Game Names
# Purpose: quantify how often game names repeat
# -----------------------------------

# Now we ask:
# How many rows contain a game name that already appeared earlier?

print("\nDuplicate game names:")
print(df_sample["name"].duplicated().sum())

# We got 35.
#
# That does not mean there are 35 bad duplicate records.
# It means there are 35 rows whose name is repeated.


# -----------------------------------
# Review Most Repeated Names
# Purpose: understand whether repeated names are isolated or part of a pattern
# -----------------------------------

# This counts how often each name appears.

print("\nMost repeated names:")

print(
    df_sample["name"]
    .value_counts()
    .head(20)
)

# We saw:
#
# Shadow of the Tomb Raider: Definitive Edition had 20 records.
# Tom Clancy's Rainbow Six Siege had 5.
# EA SPORTS FC 25 had 4.
#
# Now we know repeated names are not just a rare edge case.
# Some titles have multiple AppIDs.
#
# Rare edge case means an unusual situation that happens very infrequently.


# -----------------------------------
# Inspect All Rows with Repeated Names
# Purpose: compare repeated titles and see whether the records are otherwise the same
# -----------------------------------

# Here, we return True for every row whose name appears more than once.
#
# keep=False means that all copies of the duplicated value are marked True,
# not just the later occurrences.
#
# .sort_values("name") groups matching names together so they are easier
# to compare.

duplicate_names = df_sample[
    df_sample["name"].duplicated(keep=False)
].sort_values("name")


# Now we ask:
#
# These records share the same name, but are they otherwise the same?
#
# We include:
#
# appid
#   - to confirm that the IDs differ
#
# release_date
#   - to see whether they might be versions released at different times
#
# developers and publishers
#   - to see whether they belong to the same organization or represent
#     something unrelated with the same title

print(
    duplicate_names[
        [
            "appid",
            "name",
            "release_date",
            "developers",
            "publishers"
        ]
    ].head(50)
)


# -----------------------------------
# Investigate One Repeated Title
# Purpose: understand why one game name may have multiple AppIDs
# -----------------------------------

print("\n--- Investigating repeated title ---")

# Now we want to see:
#
# From my 1000-row sample, give me only the rows where the name equals
# Tom Clancy's Rainbow Six Siege.

r6 = df_sample[
    df_sample["name"] == "Tom Clancy's Rainbow Six® Siege"
]


# From those records, only show the columns we care about right now.

print(
    r6[
        [
            "appid",
            "name",
            "release_date",
            "price",
            "developers",
            "publishers",
            "windows",
            "mac",
            "linux",
            "genres",
            "categories",
            "positive",
            "negative",
            "estimated_owners"
        ]
    ].to_string(index=False)
)


# -----------------------------------
# Compare Repeated Title Records
# Purpose: identify which fields differ between the Rainbow Six records
# -----------------------------------

print("\nColumns that differ between Rainbow Six records:")

# Look at every column in the Rainbow Six subset.
#
# If that column has more than one distinct value across the records,
# print the column name.

for column in r6.columns:
    if r6[column].nunique(dropna=False) > 1:
        print(column)

# Here we found some similarities, but also some important differences.
#
# Even though the title, developer, publisher, release date, genre,
# and categories are the same, the records behave differently in fields
# such as price, reviews, estimated owners, and playtime.
#
# This tells us that:
#
# Same name does not mean same underlying Steam record.
#
# Therefore, we should NOT treat repeated names as duplicate records.
#
# appid remains our primary key candidate.


# -----------------------------------
# Validate Grain Across the Full Dataset
# Purpose: confirm that appid remains unique beyond the 1000-row sample
# -----------------------------------

print("\n--- Full Dataset Grain Validation ---")

# Now we load the full dataset.

df = pd.read_csv(FILE_PATH)

# Ask whether the same pattern holds across the entire dataset.

print("Total rows:", len(df))
print("Unique appids:", df["appid"].nunique())
print("Duplicate appids:", df["appid"].duplicated().sum())

# Total rows and unique AppIDs are the same.
#
# This means that every row in the full dataset has a unique appid.
#
# This supports the conclusion that the source grain is:
#
# One row = one unique Steam application record.


# -----------------------------------
# Check for Missing AppIDs
# Purpose: confirm that the primary key candidate is also complete
# -----------------------------------

# Now we confirm that there are no missing appids.

print(
    "Missing appids:",
    df["appid"].isnull().sum()
)

# This returns 0, which means there are no missing appids
# in the full dataset.
#
# appid is both:
#
# unique
# non-null
#
# So it is a strong primary key candidate.


# -----------------------------------
# Phase 1 Conclusion
# Purpose: summarize what we learned before moving into data-quality validation
# -----------------------------------

# At this point we understand:
#
# - The dataset contains 94,948 rows.
# - The source grain is one row per unique Steam application.
# - appid is unique and non-null.
# - game names are not unique.
# - repeated names should not automatically be treated as duplicates.
#
# Now we can move into Phase 2:
# Data Quality Validation.