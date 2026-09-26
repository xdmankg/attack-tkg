# Figure captions

Figure 1. Overview of the ATT&CK-TKG construction and longitudinal evaluation workflow.

Figure 2. Construction of annual co-reporting graphs using document–year weights (schematic example).

Figure 3. CP-null adjustment of observed co-reporting strength to obtain Positive Excess (schematic example). All six documents belong to one equal-weight stratum, with each document–year weight set to 1. The displayed μ values are the mean co-reporting strengths calculated from two valid illustrative incidence matrices; they are neither empirical CP-null estimates from the study nor averages of the displayed thumbnails. The illustrated single swap preserves row and column sums and, in this example, also leaves aggregate pair strengths unchanged. Calculations use unrounded values: 1/6 − 1/12 = 1/12, displayed as 0.08 after rounding to two decimal places.

Figure 4. Evaluation framework separating condition sensitivity from numerical and inferential sensitivity (schematic).

Figure 5. Concentration of pair potential across documents. Within each document population, documents are ranked in descending order of pair potential, and cumulative shares are calculated at every rank. Markers indicate the top 1%, 5%, and 10%, with document counts rounded up to the nearest integer. The inset enlarges the leading 10% of documents. The dashed diagonal represents a uniform reference.

Figure 6. Comparison of linear slopes of robust-scaled descriptors between the observed and Positive Excess representations. Slopes are estimated by fitting the robust-scaled descriptor values for the 21 transitions against the normalized time coordinate τ∈[−1, 1]. Each slope represents change in a robust-scaled descriptor per unit of normalized time, not change in the descriptor’s original units per calendar year.

Figure 7. Wild bootstrap test of in-sample fit improvement from an additional linear time term. The histogram shows the bootstrap distribution of ΔRSS* for the initial independent Rademacher test (B = 10,000; seed = 2026081505), with Analytical Coverage as the only predictor in the reduced model. Within each of the 21 transitions, one Rademacher multiplier is shared across the residuals of all nine descriptors; multipliers are independent across transitions. The solid line marks the observed ΔRSS = 15.548, and shading indicates the upper tail used to calculate the raw p-value (0.1399). The dashed line marks the 95th percentile of the bootstrap distribution (17.984). The histogram is generated from the saved replay array identified in the Supplementary reproducibility materials. Multiplier-setting sensitivity is reported in Section 5.6.

Figure 8. Comparison of temporal models using information criteria, LOTO prediction errors, and pseudo-temporal null tests (initial setting). (A) ΔIC is calculated relative to the minimum IC across R0, R1, and R2. The shaded IC-based candidate band (ΔIC ≤ 2) identifies candidate-set membership and is distinct from the pairwise practical-tie criterion for R1 versus R2 (|T12| ≤ 2). (B) LOTO prediction-error differences and their confidence intervals are based on the initial full-period scaling procedure; subsequent fold-local analyses are reported in Section 5.6. (C) E02 denotes the first pseudo-temporal null run, and E03 denotes an independent replication. Each run uses B = 200 null replicates and a lower-tail test relative to the observed T12. The two null arrays are not pooled, and Monte Carlo p-values are calculated separately for each run.

Figure 9. IC-based candidate sets and ΔIC margins across reporting and observation conditions (initial condition-specific runs).

Figure 10. IC-based candidate sets and ΔIC margins across CP-null sampling intensities (B0; five independent replicate bundles per intensity).

Figure 11. Proposed validation workflow for operational use of document-level Positive Excess candidates (schematic). This study directly provides only the initial document-level candidate stage and its supporting document evidence; subsequent validation and operational use are proposed follow-up procedures. T1057–T1083 is a candidate listed in Table 16. The document icons and the incident, host, session, and timing details are illustrative and do not represent a completed case of telemetry validation or detection-rule performance evaluation.
