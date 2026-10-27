# Export data dictionary

## Tables and relationships

| File | Grain | Key |
| --- | --- | --- |
| `game_metrics.csv` | One Steam application record | `appid` |
| `game_lookup.csv` | One descriptive application record | `appid` |
| `publisher_bridge.csv` | One application–publisher relationship | `appid`, `publisher` |

Metrics and lookup have matching ID sets. The bridge covers records with publishers and may have several rows per application. Joining metrics to the bridge can repeat game metrics; use the appropriate grain for each calculation.

## Metrics fields

| Field | Meaning |
| --- | --- |
| `appid` | Steam application identifier; complete and unique in metrics and lookup |
| `release_date` | Parsed source release date |
| `price` | Recorded snapshot price; source currency not documented in repository |
| `discount` | Recorded discount percentage, 0–100 |
| `required_age` | Source age requirement; invalid negatives converted to null |
| `metacritic_score` | Source score; zero treated as unavailable |
| `positive`, `negative` | Source positive and negative review counts |
| `calculated_review_total` | Sum of positive and negative review counts |
| `calculated_positive_pct` | Positive share of calculated review total, on a 0–100 scale; null for zero total |
| `num_reviews_total`, `pct_pos_total` | Separate source review metrics; unavailable sentinel values replaced with null |
| `owner_min`, `owner_max` | Bounds parsed from the source estimated ownership range |
| `owner_midpoint` | Arithmetic midpoint of those bounds; an estimate |
| `average_playtime_forever`, `average_playtime_2weeks`, `median_playtime_forever` | Source playtime fields; units not independently established by repository metadata |
| `peak_ccu` | Source peak concurrent-user field in the CSV; workbook mapping issue documented separately |
| `recommendations` | Source recommendation count; separate from concurrent users |
| `dlc_count` | Source downloadable-content count |
| `release_year`, `release_month`, `release_quarter` | Calendar fields derived from release date |

## Lookup and bridge fields

| Field | Meaning |
| --- | --- |
| `name` | Application title; may repeat across distinct IDs or be missing |
| `developers`, `publishers`, `genres`, `categories` | List-like strings from the cleaned source; not scalar categories |
| `windows`, `mac`, `linux` | Source platform support flags |
| `publisher` | One parsed source publisher label per bridge row; includes unresolved placeholder-like labels |

The workbook adds lookup results and segmentation fields. These spreadsheet columns are not present in the committed metrics CSV. The workbook's review categories should not be treated as official Steam classifications without verifying their formulas.
