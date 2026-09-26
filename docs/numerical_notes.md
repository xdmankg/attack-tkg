# Numerical reporting rule: Table 16

Table 16 uses `Positive Excess > 1e-12` to count positive years. This excludes
floating-point residuals and is a numerical reporting tolerance, not a
significance criterion. The table heading and manuscript note state this rule;
[the retained table note](table_notes.md) reproduces that wording.

All six reported counts agree with the retained full-precision annual values
under the adopted rule. Comparing them with a strict `R > 0` count yields the
following four differences:

| Pair | Reported: R > 1e-12 | Strict R > 0 | Extra residual |
|---|---:|---:|---:|
| T1012-T1057 | 14 | 15 | 3.47e-18 |
| T1012-T1027 | 14 | 15 | 3.90e-18 |
| T1082-T1083 | 11 | 12 | 3.90e-18 |
| T1003-T1053 | 15 | 16 | 1.69e-17 |

The other two pairs match under both rules. Cumulative values and peak
years/values agree at the paper's displayed precision and are calculated from
the unmodified annual values. Both counting rules yield the same six leading
pairs, in the same cumulative-value order, after the at-least-ten-year and
different-base-Technique filters. This does not imply identical membership of
the full eligible pair list under the two thresholds.

`results/paper_tables/table_16_numeric_check.csv` records all six comparisons;
`table_16_annual_check.csv` records all 132 pair-year values. Run
`python scripts/check_table16.py` to check the adopted rule and regenerate the
comparisons in `reproduced/table_16/` without overwriting retained inputs.

## Historical code audit

The reporting rule adopted for the current table is distinct from a claim about
the original table generator. The original generator has not been located.
The retained Stage15 E02 and E03 `contributors` functions rank relations within
each transition by squared change; they do not generate the cross-year Table 16
list. The inspected Stage16 assembly code also does not establish its historical
cutoff. Inspected source names and hashes remain in `table_16_rule_audit.json`.
A 1e-12 cutoff reproduces all six counts, but this does not prove historical use.
An epsilon elsewhere in the analysis is not evidence of this table's old rule.

This reporting clarification changes the table heading and its documentation,
not the six reported counts, cumulative values or peaks. No new cutoff has been
applied to graph construction, descriptors, model fitting or inference. The
archived numerical arrays and original numerical kernels are unchanged.

An earlier package note listed only three affected pairs. The T1082-T1083
comparison is retained here as the fourth; the strict-zero diagnostics have
not been removed.
