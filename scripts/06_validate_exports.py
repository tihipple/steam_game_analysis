"""Validate committed analysis inputs and independently summarize their results.

Run from any working directory. This does not recalculate the spreadsheet.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def main():
    tables = {
        name: pd.read_csv(ROOT / 'data' / 'excel' / f'{name}.csv',
                          keep_default_na=(name != 'publisher_bridge'))
        for name in ('game_metrics', 'game_lookup', 'publisher_bridge')
    }
    metrics, lookup, bridge = (tables[n] for n in tables)
    checks = []

    def check(label, condition):
        passed = bool(condition)
        checks.append((label, passed))
        if not passed:
            raise ValueError(f'Validation failed: {label}')

    required = {
        'game_metrics': {'appid', 'price', 'discount', 'positive', 'negative',
                         'calculated_review_total', 'calculated_positive_pct',
                         'owner_min', 'owner_max', 'owner_midpoint', 'release_date',
                         'release_year', 'release_month', 'release_quarter',
                         'num_reviews_total', 'pct_pos_total', 'required_age',
                         'metacritic_score', 'peak_ccu'},
        'game_lookup': {'appid', 'name', 'publishers'},
        'publisher_bridge': {'appid', 'publisher'},
    }
    for name, frame in tables.items():
        check(f'{name}: required columns', required[name] <= set(frame.columns))
        check(f'{name}: nonempty', not frame.empty)
        check(f'{name}: complete appid', frame.appid.notna().all())
    for name, frame in [('metrics', metrics), ('lookup', lookup)]:
        check(f'{name}: unique appid', frame.appid.is_unique)
    check('metrics and lookup ID sets match', set(metrics.appid) == set(lookup.appid))
    check('bridge IDs exist in metrics', set(bridge.appid) <= set(metrics.appid))
    check('bridge: unique pairs', not bridge.duplicated(['appid', 'publisher']).any())
    check('bridge: complete publisher', bridge.publisher.notna().all()
          and bridge.publisher.str.strip().ne('').all())
    for field in ['price', 'positive', 'negative', 'owner_min', 'owner_max', 'peak_ccu']:
        check(f'{field}: complete and nonnegative',
              metrics[field].notna().all() and metrics[field].ge(0).all())
    check('discount: complete and within bounds',
          metrics.discount.notna().all() and metrics.discount.between(0, 100).all())
    check('ownership bounds ordered', metrics.owner_min.le(metrics.owner_max).all())
    check('ownership midpoint matches bounds',
          metrics.owner_midpoint.eq((metrics.owner_min + metrics.owner_max) / 2).all())
    total = metrics.positive + metrics.negative
    check('review totals match source counts', metrics.calculated_review_total.eq(total).all())
    expected_pct = (100 * metrics.positive / total.where(total.gt(0))).round(2)
    actual_pct = metrics.calculated_positive_pct
    check('review percentage null pattern', actual_pct.isna().eq(expected_pct.isna()).all())
    check('review percentages match calculation',
          (actual_pct.dropna() - expected_pct.dropna()).abs().lt(0.000001).all())
    for field in ['num_reviews_total', 'pct_pos_total', 'required_age']:
        check(f'{field}: negative sentinels removed', metrics[field].dropna().ge(0).all())
    check('source percentage upper bound', metrics.pct_pos_total.dropna().le(100).all())
    check('Metacritic zero treated as null', metrics.metacritic_score.dropna().gt(0).all())
    dates = pd.to_datetime(metrics.release_date, errors='coerce')
    check('release dates parse', dates.notna().all())
    for field, expected in [('release_year', dates.dt.year),
                            ('release_month', dates.dt.month),
                            ('release_quarter', dates.dt.quarter)]:
        check(f'{field}: matches date', metrics[field].eq(expected).all())

    out = ROOT / 'outputs' / 'analysis'
    out.mkdir(parents=True, exist_ok=True)
    kpis = pd.DataFrame([
        ('application_records', len(metrics)),
        ('records_with_calculated_reviews', int(total.gt(0).sum())),
        ('average_calculated_positive_pct', actual_pct.mean()),
        ('average_ownership_midpoint', metrics.owner_midpoint.mean()),
        ('publisher_relationships', len(bridge)),
    ], columns=['metric', 'value'])
    kpis.to_csv(out / 'headline_metrics.csv', index=False)
    tiers = pd.cut(metrics.price, [0, 5, 10, 20, 40, float('inf')],
                   right=False, labels=['Under $5', '$5–$9.99',
                                        '$10–$19.99', '$20–$39.99', '$40+'])
    tiers = tiers.cat.add_categories(['Free'])
    tiers = tiers.where(metrics.price.ne(0), 'Free')
    price = metrics.assign(price_tier=tiers).groupby('price_tier', observed=True).agg(
        application_records=('appid', 'size'),
        mean_ownership_midpoint=('owner_midpoint', 'mean'))
    price = price.reindex(['Free', 'Under $5', '$5–$9.99', '$10–$19.99', '$20–$39.99', '$40+'])
    price.to_csv(out / 'price_performance.csv')
    metrics.groupby('release_year').agg(
        application_records=('appid', 'size'),
        mean_ownership_midpoint=('owner_midpoint', 'mean')).to_csv(out / 'release_trends.csv')
    report = '# Export validation\n\n'
    report += f'{len(checks)} checks passed against the committed CSVs. This does not validate workbook formulas or refresh behavior.\n\n'
    report += '\n'.join(f'- PASS: {label}' for label, _ in checks) + '\n'
    (out / 'validation_report.md').write_text(report, encoding='utf-8')
    print(f'{len(checks)} checks passed. Results: {out.relative_to(ROOT)}')
    print(kpis.to_string(index=False))


if __name__ == '__main__':
    main()
