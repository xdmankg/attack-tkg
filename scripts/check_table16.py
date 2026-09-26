"""Compare Table 16 with full-precision annual Positive Excess values."""
import json
import re

import pandas as pd

from common import ROOT, csv

INPUT = 'results/initial/e02/annual_rcd1_residual_long.parquet'
TOLERANCE = 1e-12
COUNT_HEADER = 'Years with Positive Excess > 10⁻¹²'


def compare():
    annual = pd.read_parquet(ROOT / INPUT)
    table = csv('results/paper_tables/table_16.csv')
    assert table.columns[1] == COUNT_HEADER
    rows, annual_rows, listed_pairs = [], [], []
    for _, row in table.iterrows():
        first, second = re.findall(r'T\d{4}(?:\.\d{3})?', row.iloc[0])
        listed_pairs.append((first, second))
        part = annual[(annual.technique_i_id == first) &
                      (annual.technique_j_id == second)].copy()
        assert len(part) == 22 and part.annual_window.is_unique
        values = part.positive_excess
        assert values.notna().all() and values.ge(0).all()
        reported = int(row.iloc[1])
        strict = int(values.gt(0).sum())
        tolerant = int(values.gt(TOLERANCE).sum())
        tiny = part[values.gt(0) & values.le(TOLERANCE)]
        peak = part.loc[values.idxmax()]
        peak_year = int(peak.annual_window.split('::')[-1])
        reported_peak_year, reported_peak_value = re.fullmatch(
            r'(\d{4})\s*\(([^)]+)\)', row.iloc[3]).groups()
        assert round(values.sum(), 4) == float(row.iloc[2])
        assert peak_year == int(reported_peak_year)
        assert round(peak.positive_excess, 4) == float(reported_peak_value)
        assert tolerant == reported
        rows.append({
            'technique_i': first, 'technique_j': second,
            'reported_positive_years': reported,
            'strict_positive_years': strict,
            'years_above_1e_minus12': tolerant,
            'small_positive_years': ';'.join(tiny.annual_window),
            'small_positive_values': ';'.join(format(v, '.17g') for v in tiny.positive_excess),
            'reported_cumulative_positive_excess': float(row.iloc[2]),
            'computed_cumulative_positive_excess': float(values.sum()),
            'peak_year': peak_year, 'peak_value': float(peak.positive_excess),
            'count_status': 'matches_reporting_rule_and_strict' if strict == reported
                            else 'matches_reporting_rule_only',
        })
        for item in part.itertuples():
            annual_rows.append({
                'technique_i': first, 'technique_j': second,
                'year': int(item.annual_window.split('::')[-1]),
                'positive_excess': item.positive_excess,
                'strict_positive': item.positive_excess > 0,
                'above_1e_minus12': item.positive_excess > TOLERANCE,
            })

    for cutoff in (0, TOLERANCE):
        ranked = annual.assign(positive_year=annual.positive_excess.gt(cutoff)).groupby(
            ['technique_i_id', 'technique_j_id']).agg(
                years=('positive_year', 'sum'), total=('positive_excess', 'sum')).reset_index()
        different_base = (ranked.technique_i_id.str.split('.').str[0] !=
                          ranked.technique_j_id.str.split('.').str[0])
        ranked = ranked[(ranked.years >= 10) & different_base].sort_values('total', ascending=False)
        assert list(ranked[['technique_i_id', 'technique_j_id']].head(6).itertuples(
            index=False, name=None)) == listed_pairs

    comparisons = pd.DataFrame(rows)
    annual_check = pd.DataFrame(annual_rows).sort_values(['technique_i', 'technique_j', 'year'])
    affected = int((comparisons.reported_positive_years != comparisons.strict_positive_years).sum())
    summary = {
        'status': 'adopted_reporting_rule_verified', 'pairs': len(comparisons),
        'annual_values': len(annual_check), 'strict_count_mismatches': affected,
        'comparison_tolerance': TOLERANCE,
        'adopted_reporting_rule': 'Positive Excess > 1e-12',
        'reporting_tolerance_is_significance_criterion': False,
        'all_counts_match_at_comparison_tolerance': True,
        'cumulative_and_peak_values_match_at_display_precision': True,
        'top_six_order_unchanged_between_comparisons': True,
        'historical_table_generation_rule': 'not_established',
        'archived_arrays_modified': False,
        'tolerance_applied_to_graph_or_descriptor_algorithms': False,
        'input_file': INPUT,
    }
    return comparisons, annual_check, summary


def main():
    comparisons, annual_check, summary = compare()
    out = ROOT / 'reproduced' / 'table_16'
    out.mkdir(parents=True, exist_ok=True)
    comparisons.to_csv(out / 'table_16_numeric_check.csv', index=False)
    annual_check.to_csv(out / 'table_16_annual_check.csv', index=False)
    (out / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
