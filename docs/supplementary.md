# Reproducibility notes

## Document identity and event time

The source manifest connects raw identifiers to canonical components, relative
collection paths, source checksums and analytical membership. Duplicate copies
remain linked to the same canonical ID. Collection dates, repository revisions
and original URLs were not present in the retained manifests and are marked
unavailable. No canonical ID has been assigned to the CISA AA20-352A example by
inference; this release does not establish that advisory's corpus membership.

The document-year registry preserves the archived weights. Publication date and
event time are distinct. Core-period totals use the retained allocations, without
renormalizing a document after excluding years outside 2002–2023. In the annual
pair-potential summary, each core document is counted once in its earliest
assigned core year and its pair potential is not document-year weighted. Total
pair potential is 66,325. This descriptive summary is separate from annual graph
construction.

## CP-null and Positive Excess

Randomization trades Technique membership between documents within equal-weight
strata, retaining each document's Technique count and each Technique's document
frequency. Numerical kernels and seed records are supplied. The expectation uses
200, 2,400 or 9,600 samples per year for L0, L1 or L2. Within each bundle, the
higher intensities extend the same chain prefixes.

Positive Excess is the positive part of observed co-reporting strength minus the
null expectation. It is not a pairwise significance test. Pseudo-temporal graphs
use a fixed expectation estimated from separate calibration samples. Observed
document counts continue to define support levels when descriptors are computed
from pseudo-observed strengths. E02 and E03 each contain 200 statistics and are
not pooled.

## Table 16 reporting tolerance

Positive years in Table 16 are counted using `Positive Excess > 1e-12` to
exclude floating-point residuals. This is a reporting tolerance, not a
significance criterion. It reproduces all six counts without changing the
archived annual arrays, cumulative values or peaks. Four counts differ from a
strict-zero comparison, as recorded in `docs/numerical_notes.md`. The adopted
rule does not establish what the unlocated original table generator used.

## DWB and conditional tests

The retained implementation generates independent standard Gaussian innovations
of length n + ell - 1. Each DWB multiplier is the sum of ell consecutive
innovations divided by sqrt(ell), giving unit marginal variance and covariance
max(1 - h/ell, 0) at lag h. No circular wrapping, endpoint padding or extra
empirical variance normalization is used. Lengths 2, 3 and 4 are included.
Independent Rademacher and Gaussian multipliers are separate settings.

One transition multiplier is shared across all nine response descriptors.
Reduced-model residuals are centered by descriptor. The two tests are
Time | Analytical Coverage and Analytical Coverage | Time. Upper-tail p-values
use the plus-one correction; follow-up tail comparisons use the retained
1e-12 numerical tolerance. Holm corrections are stored separately for the two
directions and the nine descriptor-specific tests. Exact seeds appear in the
bootstrap result rows. B = 10,000 in each setting.

## LOTO and block resampling

Full-period scaling, fold-local scaling and fold-local scaling with adjacent
transition exclusion are distinct settings. Predictions fitted on a fold's
robust scale are transformed back to raw descriptor units before scoring.
For the preprocessing comparison, both methods are scored using the H0 training
median/MAD scale. For the adjacency comparison, both methods use the GAP1
training scale. The scale is 1.4826 times the median absolute deviation; values
at or below 1e-12 are replaced by 1.0.

Moving-block resampling is noncircular. A block start is uniform over 0 through
n - ell, blocks are concatenated, and the sequence is truncated to n = 21.
Lengths 2, 3 and 4 are used alongside IID transition resampling. There are 10,000
replicates. Percentile intervals use the 2.5th and 97.5th percentiles with linear
quantile interpolation. The statistic is the mean paired squared-error
difference, using matched scoring scales. Stored rows identify the analysis
role, scoring scale, models, seed and interval.

The 49 datasets comprise `BASELINE_STAGE15_S0`, `BASELINE_V06_S0_FULL`,
`BASELINE_V06_S1_DROP_TOP1`, `BASELINE_V06_S2_DROP_TOP5`, and 45 combinations of
three scenarios, five bundles and three intensities. Exact IDs and input paths
are in `run_registry.csv`.

## Figure data

Figure 3 uses `data/examples/figure_03/observed_incidence.csv` and
`illustrative_state_2.csv`. Each has six documents in one unit-weight stratum.
The illustrative expectation is the equally weighted mean of the two
co-reporting strength matrices, not the mean incidence matrix or an empirical
CP-null estimate. The displayed single swap happens to preserve aggregate pair
strength. Calculations use unrounded numbers: 1/6 - 1/12 = 1/12, displayed as 0.08.

Figure 5 includes every document rank in descending pair potential. Top 1%, 5%
and 10% counts use ceiling, and the inset enlarges the leading 10%. The diagonal
is a uniform reference. Figure 6 slopes use robust-scaled descriptors fitted to
normalized time tau in [-1,1] over 21 transitions, not raw change per year.

Figure 7 reads `results/initial/figure_07/initial_bootstrap_replay.npz`, array
`delta_rss_star`. This is a saved replay from frozen Stage15 inputs and the
V03 algorithm with seed 2026081505, not a claim that the original execution
archived this filename. The archived verification record is retained. The
public replay reproduced all 10,000 values exactly in the checked environment.
There are 1,398 upper-tail values, giving (1,398+1)/(10,000+1) = 0.139886.
The linear-interpolation 95th percentile is 17.984492, displayed as 17.984.
Subsequent multiplier-setting sensitivity corresponds to Table 23.

Figure 8 keeps E02 and E03 separate. Its initial LOTO intervals are reported at
manuscript precision in `LOTO_table19.json`; the retained full initial bootstrap
CSV is also supplied. The IC-based candidate band is minimum-relative and is distinct
from pairwise practical tie. Figure 9 contains 17 plotted conditions and 51 IC
values; the historical sampling budgets must not all be described as 200/year.
Figure 10 uses actual per-replicate IC values. S2 R2 is the minimum in two L2
bundles, so all plotted Delta IC values are nonnegative although R2-R0 can be
negative.

Only the first document-level candidate stage of Figure 11 is provided by the
study. T1057-T1083 is a Table 16 candidate; incident, host, session and time details
in the drawing are illustrative. Later validation and operational use are
proposed procedures. The schema must not be read as evidence that those
validations have been completed.

Collection repository URLs and their current check dates are listed in
`data/collection_snapshots.csv`; they do not recover historical collection
metadata. See `docs/rights.md` for the upstream sources and separate license
scopes, and `docs/numerical_notes.md` for the Table 16 counting comparison.
