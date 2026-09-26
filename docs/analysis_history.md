# Analysis history

| Analysis | Role in the manuscript | Public location |
|---|---|---|
| Stage15 / 15E02–15E03 | Initial Positive Excess construction, descriptors, model comparison and temporal tests. | `results/initial/stage15/`, `results/initial/e02/`, `results/initial/figure_08/` |
| V03-02 | Initial independent Rademacher test and its retained numerical implementation. | `results/initial/figure_07/`, `scripts/initial_bootstrap_reference.py` |
| V04 / V05 / V06 | Earlier collection, TRR, scope, density and period analyses. Sampling budgets differ between runs. | `results/initial/figure_09/`, `results/initial/v05/` |
| V07-01 | Five follow-up bundles and three CP-null intensities; fold-local LOTO and multiplier sensitivity. | `results/followup/` |
| V07-01R | Deterministic corrections to candidate-set comparisons and inference/preprocessing summaries. | `results/corrections/` |

V07-01R does not replace an initial test with a later simulation. It distinguishes
the minimum-relative IC candidate set from the pairwise R1–R2 tie, and uses
actual set intersection for scenario comparisons. The original numeric IC values
are retained. B0 S0–S2 sets are disjoint in five of five bundles at L0 and L1;
at L2 they overlap in five of five bundles through R2.

Corrected preprocessing comparisons use matched scoring scales. In the retained
49-dataset summary, R2 fold-local RMSE decreases in 18 datasets, is equal in 20
and increases in 11. The original tables are preserved in `results/followup/loto/`
and corrected interpretations in `results/corrections/`.

Public numerical functions were extracted from the archived source without
changing function bodies. `code_provenance.csv` records source hashes and line
locations. Portable command-line wrappers and package validation were added.
Private experiment controllers, machine paths and editorial reports are not
included. The source data and retained results remain separate from replay output.
