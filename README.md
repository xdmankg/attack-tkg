# ATT&CK-TKG

Data and code accompanying *Temporal Knowledge Graph–Based Longitudinal Analysis
of ATT&CK Technique Relations in Public CTI and the Condition Dependence of
Temporal-Model Comparison Results*, by HyoungJu Kim and Junho Choi.

The analysis covers 2002–2023 and 1,474 core CTI documents. It compares temporal
models of Technique co-reporting under changes in document composition,
collection, observation scope, analysis period and evaluation settings.
Co-reporting does not establish execution order or causality. Positive Excess
does not establish pairwise significance.

## Data

`data/` contains canonical identifiers, duplicate mappings, adopted evidence
locations, document–Technique links, event-time assignments and document–year
weights. Source PDFs and quoted report text are not redistributed.

`results/initial/`, `results/followup/` and `results/corrections/` retain distinct
analysis stages. `figures/` contains the 11 figures extracted from the final
manuscript. The 27 CSV files in `results/paper_tables/` are text transcriptions of
manuscript tables, not substitutes for full-precision analysis files.

Start with [the paper-to-file index](docs/paper_artifacts.csv) and
[the data dictionary](docs/data_dictionary.md). Collection-level repository URLs
are listed in [source and rights documentation](docs/rights.md) and linked from
the manifest. Original document download URLs, historical retrieval dates and
repository revisions remain unavailable. This package supports reproduction
from the retained derived inputs, not recovery of the original collection or
reexecution of source-text extraction. See [coverage and limitations](docs/coverage.md).
Table 16 counts positive years using `Positive Excess > 1e-12` to exclude
floating-point residuals. This reporting tolerance is not a significance
criterion. All six counts match the retained annual values under that rule;
[numerical notes](docs/numerical_notes.md) retain the strict-zero comparison and
the limits of the historical code audit.

## Reproducing the results

Use Python 3.12 and install the tested dependencies:

```bash
python -m pip install -r requirements.txt
python scripts/verify.py
python scripts/reproduce.py
```

The first command after installation checks identifiers, weights, all annual
observed graphs, follow-up Positive Excess descriptors and key reported results.
The second redraws Figures 3 and 5–10 from retained numerical files. Publication
artwork remains unchanged; all new outputs go to the ignored `reproduced/` folder.
Figures 1, 2, 4 and 11 are explanatory artwork and are supplied as final images.

Selected analysis replays are separate commands:

```bash
python scripts/replay_analysis.py models
python scripts/replay_analysis.py initial-bootstrap
python scripts/replay_analysis.py followup-bootstrap
python scripts/replay_analysis.py loto
python scripts/replay_null.py --year 2002
python scripts/check_table16.py
```

The default inference dataset is `BASELINE_STAGE15_S0`. Other dataset IDs are in
[the run registry](docs/run_registry.csv). Parameters, numerical tolerances and
verification scope are documented in [reproduction instructions](docs/reproduction.md).
The complete high-intensity Monte Carlo experiment is not run by these defaults.

## Updating release files

Release text uses LF line endings, enforced by `.gitattributes`. After reviewing
an intended change to README, citation metadata or other distributed files, run:

```bash
python scripts/update_checksums.py
python scripts/update_checksums.py --check
python scripts/verify.py
```

The update command normalizes text, refreshes the public-file hashes in both
provenance indexes and rebuilds `checksums.sha256`. It retains historical
`source_sha256` values. It does not validate a scientific change; the subsequent
verification is required. See [the change record](CHANGELOG.md).

## Analysis versions

The initial S0 result, the earlier condition-specific runs, the V07-01 follow-up
and the V07-01R corrections are kept separate. The corrected candidate rule is
`IC - min(IC) <= 2.0 + 1e-12`. It differs from the pairwise R1–R2 practical-tie
rule. Original V07 output columns are retained for provenance; corrected
summaries and recalculated sets determine the interpretation.

Five replicate bundles share prefix samples across L0, L1 and L2 within each
bundle. Agreement within an intensity does not establish convergence.
See [analysis history](docs/analysis_history.md).

## Citation and contact

Repository: https://github.com/xdmankg/attack-tkg.

Author metadata is in `CITATION.cff`. Journal and archive DOIs have not been
assigned in this package. [Release instructions](docs/release.md) describe
versioned publication and archiving. The repository URL alone does not identify
an archived release.
Correspondence: Junho Choi,
xdman@chosun.ac.kr.

## Rights

Author-written code and software-use instructions are licensed under
[MIT](LICENSE). The authors' derived data, numerical results, original figures
and research documentation are licensed under [CC BY 4.0](LICENSE-DATA), within
the authors' rights. Third-party CTI and ATT&CK content retain their own terms.
The licenses apply to distinct materials. See [the scope and upstream sources](docs/rights.md).
