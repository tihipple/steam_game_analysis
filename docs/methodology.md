# Methodology and reproduction

## Analysis design

The project asks how pricing, reviews, release cohorts, and publishers relate to estimated audience size. Python prepares the data; the spreadsheet provides lookups, calculated categories, PivotTables, charts, and written findings. The deliverable is complete as an Excel/spreadsheet analysis project.

## Data origin and scope

The original scripts reference `data/steam_large_dataset/games_march2025_full.csv`. That raw file is excluded from Git. The repository does not identify its original download page, author, extraction method, currency definition, or upstream license. Those details need to be recovered from the original download before asserting a specific source attribution or reuse license. No upstream attribution has been invented.

The committed exports contain 94,948 unique Steam application IDs. Application IDs identify records; game names are not unique and should not be used as join keys. Related editions or applications may share a name. The dataset is a historical snapshot, with a partial 2025 release cohort.

## Preparation decisions

| Issue | Treatment | Reason |
| --- | --- | --- |
| Repeated game names | Keep distinct application IDs | Same title does not establish a duplicate record |
| Review fields containing `-1` | Replace sentinel values with null | Unavailable values should not be averaged as negative reviews |
| Negative required age | Convert to null | Invalid age requirement |
| Metacritic score of zero | Treat as unavailable | QA review found the pattern consistent with missing scores |
| Missing game names | Retain records; flag in cleaned source | Avoid inventing names or dropping valid IDs |
| Ownership ranges | Parse lower/upper bounds and midpoint | Enable comparisons while retaining uncertainty |
| Empty list strings | Convert to null | Represent unavailable categories consistently |
| Multiple publishers | Explode into distinct ID–publisher pairs | Preserve many-to-many relationships |

Some exported publisher labels are literal strings such as `None`, `N/A`, and `NA`. They are retained as source labels rather than silently reinterpreted or attributed to a company. The relationship headline includes these labels, so it is not a count of confirmed publisher attributions.

The original QA decisions and counts are in [`qa_notes.md`](../outputs/data_quality/qa_notes.md). The exported tables do not include every field from the intermediate cleaned source, including its missing-name flag.

## Metric definitions

- `calculated_review_total = positive + negative`.
- `calculated_positive_pct = 100 × positive / calculated_review_total`, rounded to two decimals. Records with zero calculated reviews remain null.
- `owner_midpoint = (owner_min + owner_max) / 2`. It is a comparison proxy, not an exact owner count or a sales estimate.
- Average calculated positive percentage excludes null percentages and gives each application equal weight.
- Release-year counts describe application records by release date, not sales during that year.
- Publisher averages use records attached to each publisher. Do not sum publisher groups to obtain total games or owners.

Original review counts and percentages are preserved separately. Their disagreement with the calculated metrics suggests differing definitions or snapshots; the underlying cause was not established.

## Reproducing the workflow

### Validate and summarize the included exports

Install `requirements.txt`, then run:

```bash
python scripts/06_validate_exports.py
```

The script checks required columns, keys, exact key-set alignment, publisher relationships, calculated fields, numeric bounds, and date-derived fields. It writes a Markdown validation report and CSV summaries only after all checks pass. This validates the exports, not the workbook engine.

### Rebuild exports from the original raw file

If you have the original raw CSV, place it at the path above and run these scripts from the repository root, in order:

```bash
python scripts/01_data_profile.py
python scripts/02_data_quality_validation.py
python scripts/03_data_cleaning.py
python scripts/04_excel_prep.py
python scripts/05_publisher_bridge.py
python scripts/06_validate_exports.py
```

Steps 01–02 print exploratory diagnostics. Step 03 saves an intermediate cleaned dataset under `data/cleaned/`; steps 04–05 export the three committed CSVs. Running the pipeline can overwrite those exports. The raw file and full intermediate cleaned data are not included, so a source-to-export rerun requires the original source. The workbook was assembled separately and is not rebuilt by these Python scripts.

## Reading and refreshing the workbook

Start with Summary, then the four analysis sheets. GameMetrics and GameLookup join on `appid`; PublisherBridge has one row per ID–publisher pair. Formula Notes and Dictionary document the spreadsheet approach. Read [workbook review notes](workbook_review.md) before reusing CCU-related results or refreshing the exported workbook.
