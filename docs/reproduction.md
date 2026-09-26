# Reproduction

## Environment and outputs

`requirements.txt` records the versions used for this package's verification.
`configs/historical_stage15_environment.json` records the retained historical
Windows environment separately. A matching random seed is not a guarantee of
bitwise agreement across different numerical libraries or platforms.

Run commands from the repository root. All commands read retained inputs and
write to `reproduced/`. Do not replace the archived results with a replay output.
`checksums.sha256` covers every distributed file except itself. All release text
uses LF endings. `python scripts/update_checksums.py --check` checks the full
manifest and both public-file hash indexes without changing files. After an
intended release edit, run `python scripts/update_checksums.py` and then
`python scripts/verify.py`. The update command preserves historical source hashes;
it is not a substitute for reviewing changes to research inputs or outputs.

## Checks without new simulation

`python scripts/verify.py` checks the raw-to-canonical mapping and core membership;
compares all 4,060 analytical weights with the original assignment file;
reconstructs the 22 observed annual graphs; verifies 45 B0 descriptor datasets
against saved Positive Excess arrays; recalculates candidate sets; checks the
initial and pseudo-temporal bootstrap counts; and checks file hashes.

`python scripts/reproduce.py` redraws Figures 3, 5, 6, 7, 8, 9 and 10. Use
`--figures 5 10` to select figures. The Figure 7 plotting program deterministically
replays the original 10,000 statistics in its output directory, reloads that array
and plots it. It never overwrites the retained array. The final paper images in
`figures/` remain the publication reference; font rasterization and Figure 6's
reconstructed layout may differ from the embedded image.

## Analysis replays

`python scripts/replay_analysis.py models` fits R0/R1/R2 to 49 retained datasets
and checks the 135 follow-up B0 IC values against the archive.

`python scripts/replay_analysis.py initial-bootstrap` repeats the initial
Time | Analytical Coverage test from the original V03 numerical function. It
compares every statistic with the saved replay array using absolute and relative
tolerances of 1e-12 and records whether bitwise equality also holds.

`python scripts/replay_analysis.py followup-bootstrap --dataset BASELINE_STAGE15_S0`
repeats both test directions under five multiplier settings. It checks observed
statistics and tail counts. Stored null arrays are float32; comparisons to those
arrays use relative tolerance 1e-6 and absolute tolerance 1e-5. Published p-values
were calculated from full-precision statistics before storage.

`python scripts/replay_analysis.py loto --dataset BASELINE_STAGE15_S0` repeats
three prediction settings with three scoring scales, checks 567 transition-loss
values, and regenerates 40 bootstrap intervals. The CI comparison uses absolute
and relative tolerance 1e-9. The large redundant component-prediction CSV and
float32 LOTO resampling arrays are not distributed: raw descriptor datasets,
transition losses, scalers, seeds and the original numerical kernels are included.

Other valid `--dataset` values are listed in `docs/run_registry.csv`. Baseline and
follow-up datasets must not be substituted for one another.

`python scripts/replay_null.py --year 2002 --scenario S0_FULL --replicate 0 --level L0_STAGE15_MATCHED`
repeats one annual CP-null ensemble using the archived seeds and curveball
functions. The public wrapper averages chain means; tiny summation-order
differences are allowed (absolute tolerance 1e-12, relative tolerance 1e-10).
The L0 expectation uses 100 draws from each of two chains, even though the
historical run generated additional draws for diagnostics. L1 and L2 use the
retained prefix budgets. Select another year, scenario, bundle or level explicitly.
Running all high-intensity ensembles is computationally more expensive than
reading their saved arrays.

## Verification performed for this package

The saved verification report records the runs actually completed. It includes
all observed annual graphs, all 45 B0 saved descriptor series, 49 model fits,
the initial 10,000-statistic replay, the ten follow-up conditional tests and forty
LOTO bootstrap intervals on the Stage15 baseline, and one annual CP-null replay
(S0, bundle 0, 2002, L0). The entire 3,168,000-draw follow-up experiment was not
rerun during packaging. The script supports individual annual replays; this is
not a claim that every possible replay has been validated in this environment.

## Table 16 counting comparison

Run `python scripts/check_table16.py` to compare all 132 listed pair-year values
under strict positivity and a 1e-12 numerical cutoff. The saved comparison files
are in `results/paper_tables/`; new outputs go to `reproduced/table_16/`. This
command verifies all six counts under the adopted Table 16 reporting rule,
`Positive Excess > 1e-12`, and the displayed cumulative/peak values. The strict-zero
comparison is retained. The check does not establish the historical generator's
rule or modify retained arrays. See `docs/numerical_notes.md` and
`docs/table_notes.md`.
