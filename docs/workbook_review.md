# Workbook review notes

The existing workbook and dashboard image are preserved as the original project deliverables. The repository documentation and Python validation add a separate, auditable view of the committed CSV data.

## Field mapping issue

In the workbook's `GameMetrics` sheet, the sampled `peak_ccu` values match the CSV's `recommendations` values rather than its `peak_ccu` values. The sampled `recommendations` values match `dlc_count`, and the sampled `dlc_count` values are blank. For example, application 730 has a CSV `peak_ccu` of 1,212,356 and `recommendations` of 4,401,572; the workbook labels 4,401,572 as `peak_ccu`.

The `PublisherBridge` sheet also contains sampled `peak_ccu` values matching recommendations. These observations establish a field mapping problem in the sampled records. They do not establish its full extent or the workbook's recalculation behavior.

**Affected use:** do not rely on workbook average peak CCU fields, related pivot results, or the original finding about peak CCU until the mappings and dependent pivots are repaired and refreshed in the spreadsheet application.

**Repair path:** restore the GameMetrics columns from the CSV using headers and `appid`, rebuild bridge metric lookups by header, refresh dependent pivots, then check representative records and aggregate results. Existing workbook values and formulas have not been rewritten by this documentation update.

## Compatibility

The Formula Notes tab includes Google Sheets functions such as `ARRAYFORMULA` and open-ended ranges. A downloadable `.xlsx` export does not establish that every formula, pivot, and chart refreshes correctly in Excel. The PNG provides a static preview; validation of the committed CSVs does not validate workbook formulas.

## Presentation observations

The original image truncates some category and publisher labels and includes a Grand Total category in the price chart. The README links both the preview and full findings so readers can see complete labels and independently calculated figures. A future workbook refresh should remove Grand Total from chart series, order categories numerically, and show complete labels.
