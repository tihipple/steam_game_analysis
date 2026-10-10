# Data Quality Notes

## appid
- 94,948 rows
- 94,948 unique appids
- 0 duplicates
- 0 nulls
- Decision: use as primary key candidate

## pct_pos_total
- Expected range: 0–100
- Found 39,575 records with value -1
- Some -1 rows still have positive and negative review counts
- Interpretation: likely sentinel/unavailable value
- Decision: convert -1 to null during cleaning

# Steam Dataset QA Log

# Phase 1
| Field | Check Type | Finding | Status | Decision | Notes |
|---|---|---|---|---|---|
| appid | Uniqueness | 94,948 unique values across 94,948 rows | Pass | Keep as primary key candidate | No duplicate AppIDs found |
| appid | Null check | 0 missing values | Pass | Keep as primary key candidate | Key is complete |
| release_date | Validity | All values converted successfully to datetime | Pass | Convert to datetime during cleaning | 0 failed conversions |
| estimated_owners | Data type | Stored as 15 text ranges | Review | Parse later | Consider min, max, and midpoint |
| pct_pos_total | Range | 39,575 values equal -1 | Investigate | Likely treat -1 as unavailable | Some rows still contain review counts |
| required_age | Range | 1 value equals -1 | Fail | Convert negative value to null | Negative age is invalid |
| metacritic_score | Missing representation | 91,372 values equal 0 | Investigate | Likely treat 0 as unavailable | Matches Metacritic URL pattern |
| price | Outlier | Maximum value is 999.98 | Review | Keep unless proven invalid | High prices appear plausible |

# Phase 2
| Field | Check Type | Finding | Status | Decision | Notes |
|---|---|---|---|---|---|
| appid | Uniqueness | 94,948 unique values across 94,948 rows | Pass | Use as primary key | No duplicate or missing AppIDs |
| release_date | Validity | 0 failed date conversions | Pass | Convert to datetime | All source values parse successfully |
| estimated_owners | Structure | 15 text-based ownership ranges | Review | Parse during transformation | Represents numeric ranges as text |
| pct_pos_total | Sentinel values | 39,575 values equal -1 | Clean | Convert -1 to null | Matches unavailable num_reviews_total records |
| pct_pos_recent | Sentinel values | 87,727 values equal -1 | Clean | Convert -1 to null | Matches unavailable num_reviews_recent records |
| num_reviews_total | Sentinel values | 39,575 values equal -1 | Clean | Convert -1 to null | -1 represents unavailable data |
| num_reviews_recent | Sentinel values | 87,727 values equal -1 | Clean | Convert -1 to null | -1 represents unavailable data |
| review metrics | Consistency | Only 6,222 rows have num_reviews_total = positive + negative | Review | Preserve source values separately | Likely different source definitions or snapshots |
| pct_pos_total | Consistency | 11,893 exact matches to calculated positive % | Review | Preserve source value and optionally create calculated metric | Source percentage differs from positive/negative counts |
| required_age | Range | 1 negative value | Fail | Convert negative value to null | Age cannot logically be negative |
| metacritic_score | Missing representation | 91,372 values equal 0 | Clean | Treat 0 as unavailable/null | Closely matches missing Metacritic URL pattern |
| price | Range | No negative prices | Pass | Keep values | High values are outliers but appear plausible |
| discount | Range | All values between 0 and 100 | Pass | Keep values | Valid percentage range |
| playtime | Range | No negative values | Pass | Keep values | Extreme values remain possible outliers |
| peak_ccu | Range | No negative values | Pass | Keep values | Valid range |
| platform flags | Consistency | Every application supports at least one OS | Pass | Keep values | No records with all three flags false |
| name | Completeness | 2 missing names | Review | Inspect during cleaning | Very small number of affected rows |

# Phase 3: Data Cleaning and Transformation

## release_date
- Converted `release_date` from text/object to `datetime64[ns]`.
- Validation confirmed the datatype changed successfully.
- No rows were lost during conversion.

## Review sentinel values
- Replaced `-1` with null in:
  - `pct_pos_total`
  - `pct_pos_recent`
  - `num_reviews_total`
  - `num_reviews_recent`
- Validation confirmed there are 0 remaining `-1` values in those fields.
- Null counts after cleaning:
  - `pct_pos_total`: 39,575
  - `pct_pos_recent`: 87,727
  - `num_reviews_total`: 39,575
  - `num_reviews_recent`: 87,727

## required_age
- Replaced negative `required_age` values with null.
- Validation confirmed 0 negative values remain.
- One record was affected.

## metacritic_score
- Replaced `metacritic_score = 0` with null because Phase 2 showed that 0 was being used as unavailable/missing data.
- Validation confirmed 0 Metacritic scores remain.
- 91,372 values are now represented as null.

## Missing names
- Two records have missing game names.
- The records were not deleted and no title was invented.
- Added `name_missing_flag` so these records can be identified later.
- Validation confirmed:
  - 2 missing names
  - 2 records flagged

## estimated_owners
- Split the text-based ownership ranges into:
  - `owner_min`
  - `owner_max`
  - `owner_midpoint`
- Example:
  - `20000 - 50000`
  - `owner_min = 20000`
  - `owner_max = 50000`
  - `owner_midpoint = 35000`
- Validation confirmed 0 missing `owner_min` values and 0 missing `owner_max` values.
- `owner_midpoint` is an estimate and should not be treated as an exact ownership count.

## Calculated review metrics
- Preserved the original review fields.
- Created:
  - `calculated_review_total = positive + negative`
  - `calculated_positive_pct`
- `calculated_positive_pct` is only calculated when total positive + negative reviews are greater than 0.
- 22,300 records have no calculated positive percentage because they have 0 calculated reviews.
- Validation confirmed:
  - 0 negative calculated review totals
  - 0 calculated percentages below 0
  - 0 calculated percentages above 100
- These fields are kept separate from the source review metrics because Phase 2 showed the source fields use different definitions or snapshots.

## Empty list values
- Converted `"[]"` strings to null in:
  - `genres`
  - `categories`
  - `developers`
  - `publishers`
  - `tags`
  - `supported_languages`
  - `full_audio_languages`
- Validation confirmed 0 remaining `"[]"` values.
- Final null counts:
  - `genres`: 5,441
  - `categories`: 5,907
  - `developers`: 5,451
  - `publishers`: 5,780
  - `tags`: 22,117
  - `supported_languages`: 5,412
  - `full_audio_languages`: 55,090

## Final cleaning validation
- Total rows: 94,948
- Unique AppIDs: 94,948
- Duplicate AppIDs: 0
- Missing AppIDs: 0
- `release_date` datatype: `datetime64[ns]`
- Negative `required_age` values: 0
- `metacritic_score = 0`: 0
- `pct_pos_total = -1`: 0
- `pct_pos_recent = -1`: 0
- `num_reviews_total = -1`: 0
- `num_reviews_recent = -1`: 0

## Phase 3 conclusion
- The original source grain was preserved.
- No rows were deleted.
- Raw source data remains untouched.
- The cleaned dataset was saved separately as:
  `data/cleaned/steam_games_cleaned.csv`