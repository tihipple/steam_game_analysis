# Export validation

36 checks passed against the committed CSVs. This does not validate workbook formulas or refresh behavior.

- PASS: game_metrics: required columns
- PASS: game_metrics: nonempty
- PASS: game_metrics: complete appid
- PASS: game_lookup: required columns
- PASS: game_lookup: nonempty
- PASS: game_lookup: complete appid
- PASS: publisher_bridge: required columns
- PASS: publisher_bridge: nonempty
- PASS: publisher_bridge: complete appid
- PASS: metrics: unique appid
- PASS: lookup: unique appid
- PASS: metrics and lookup ID sets match
- PASS: bridge IDs exist in metrics
- PASS: bridge: unique pairs
- PASS: bridge: complete publisher
- PASS: price: complete and nonnegative
- PASS: positive: complete and nonnegative
- PASS: negative: complete and nonnegative
- PASS: owner_min: complete and nonnegative
- PASS: owner_max: complete and nonnegative
- PASS: peak_ccu: complete and nonnegative
- PASS: discount: complete and within bounds
- PASS: ownership bounds ordered
- PASS: ownership midpoint matches bounds
- PASS: review totals match source counts
- PASS: review percentage null pattern
- PASS: review percentages match calculation
- PASS: num_reviews_total: negative sentinels removed
- PASS: pct_pos_total: negative sentinels removed
- PASS: required_age: negative sentinels removed
- PASS: source percentage upper bound
- PASS: Metacritic zero treated as null
- PASS: release dates parse
- PASS: release_year: matches date
- PASS: release_month: matches date
- PASS: release_quarter: matches date
