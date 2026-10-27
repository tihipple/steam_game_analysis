# Findings

## Pricing and estimated audience

Recalculated from `game_metrics.csv`, grouped by the price recorded in the dataset:

| Price tier | Application records | Mean ownership midpoint |
| --- | ---: | ---: |
| Free ($0) | 19,420 | 134,488 |
| Above $0, below $5 | 39,409 | 36,983 |
| $5 to below $10 | 19,106 | 58,200 |
| $10 to below $20 | 12,751 | 144,753 |
| $20 to below $40 | 3,364 | 400,901 |
| $40+ | 898 | 788,452 |

Among paid records, higher price tiers have higher mean estimated ownership. Free records also have a larger mean audience than the two lowest paid tiers. This does not show that raising a game's price increases demand: franchise recognition, release age, genre, discount timing, and extreme values can affect these averages. Snapshot prices are not necessarily launch prices.

## Release cohorts

| Release year | Application records | Mean ownership midpoint |
| --- | ---: | ---: |
| 2014 | 1,529 | 320,984 |
| 2024 | 20,427 | 36,565 |

The dataset shows a much larger recent release cohort with lower average estimated ownership. This is a cross-sectional comparison of release cohorts, not a history of annual sales. Older games have had longer to accumulate owners. The 2025 cohort is partial, and early cohorts have small samples.

## Review sentiment

The mean calculated positive-review percentage is **75.40%**, across **72,648 records with at least one calculated review**. The other 22,300 records have no calculated percentage and are excluded from this mean. This is an unweighted mean of game-level percentages, not the percentage of all reviews that are positive.

The workbook's review-versus-owner analysis shows greater concentration in its Positive and Very Positive categories at higher ownership tiers. Those category labels are project-defined groupings. Small review counts can produce unstable percentages, and the original and calculated review fields are not interchangeable.

## Publishers

The publisher bridge contains **92,611 distinct application–publisher relationships**. A relationship count is different from the number of games or publishers. Multi-publisher games appear in more than one publisher group, so totals across publishers are not additive to the full game count.

The workbook compares catalog size, average ownership, and review sentiment. Large catalogs do not uniformly have large average audiences. Mean ownership can be dominated by a few successful games; follow-up comparisons should include medians, distribution plots, and minimum sample sizes.

## Practical interpretation

This project demonstrates how data preparation and careful metric definitions support a readable market analysis. It identifies patterns worth investigating rather than proving a pricing strategy or predicting commercial success. No revenue, causal, forecasting, or verified workbook concurrency conclusions are claimed.
