# Data dictionary

| Path | Unit and content |
|---|---|
| `data/canonical_documents.csv` | 1,856 canonical documents; component hashes, representatives, duplicate membership and final analytical inclusion. |
| `data/source_manifest.csv` | 2,192 raw documents linked to canonical IDs, relative collection paths, source-file SHA-256 hashes and collection-level repository URLs. |
| `data/collection_snapshots.csv` | Collection repository URLs and URL-check dates, separate from unavailable historical retrieval/revision fields. |
| `data/analytical_document_year_registry.csv` | 4,060 document-year records, collection membership, weights, Technique counts and eligible strata. |
| `data/document_year_weights.csv` | Core canonical ID, calendar year and frozen weight for 2002–2023. |
| `data/all_year_assignments.parquet` | Retained assignments before clipping to the analytical period. Includes years outside 2002–2023. |
| `data/document_techniques.csv` | 5,258 distinct adopted direct-evidence links in the broader mapping population; join to the core registry for the analytical corpus. |
| `data/technique_evidence_locations.csv` | 9,550 adopted direct-evidence mentions, IDs, page/sentence/span positions and mapping dispositions; source quotations omitted. |
| `data/event_time_assignments.csv` | 14,252 normalized event-time mentions with evidence positions, interval bounds, precision, rules and anchoring metadata. |
| `data/temporal_intervals.csv` | 8,149 distinct retained temporal intervals, multiplicities and associated evidence IDs. |
| `data/relation_universe.csv` | 28,195 undirected pairs in frozen feature-index order. |
| `data/examples/` | Small schematic examples for Figures 2 and 3, separate from empirical inputs. |

`canonical_document_id` is the join key across evidence, time assignments and
Technique mappings. `raw_document_id` refers to an individual retained source
copy. The 2,192-row identity manifest covers the records admitted to the canonical
identity stage; it is not an inventory of all 2,269 initially collected files.
No missing raw-file records have been synthesized.

`source_path` is a relative collection path with forward slashes and percent
encoding. Decode it as UTF-8 to recover non-ASCII characters in original filenames.
Encoding changes representation only; it does not alter file identity. A source
path is not a retrieval URL. Missing URLs and historical snapshot metadata are
marked `unavailable` rather than inferred from document titles.

`collection_repository_url` identifies the upstream collection, not an individual
document download or publisher page. It joins `source_dataset` to `collection`
in `collection_snapshots.csv`. `url_checked_date` records the current source-page
check and must not be read as the original `retrieval_date`.

Analytical weights are positive, but a core document's weights within 2002–2023
need not sum to one if part of its allocation lies outside that period. The frozen
weights are retained without renormalization. The full assignment file supports
inspection of this difference. Neither an unweighted document count nor a count
of distinct years is a substitute for weighted document mass.

Technique evidence covers a broader population than the 1,474 core documents.
Within the core, 533 documents have no adopted Technique, 353 have one and 588
have at least two. Documents without a pair still enter weighted document mass.

Internal descriptor column names are retained for numerical traceability:

| Stored column | Manuscript name |
|---|---|
| `component_share_birth` | New-relation rate |
| `component_share_death` | Disappearance rate |
| `component_share_increase` | Increase rate |
| `support_share_low` | Low-support relation share |
| `support_share_medium` | Medium-support relation share |
| `rms_low` | RMS low |
| `rms_medium` | RMS medium |
| `rms_high` | RMS high |
| `persistent_relation_rms` | Persistent-relation RMS |

Foundation NPZ files contain `observed`, `supports`, `analytical_coverage`,
`active_nodes_0` through `active_nodes_21`, and `mu_*` / `residual_*` arrays for
L0, L1 and L2. Annual arrays use row order 2002–2023 and the column order in
`relation_universe.csv`. `supports` counts observed documents, not weighted mass.

Table 16's positive-year column counts annual `Positive Excess > 1e-12`.
The cutoff is a numerical reporting tolerance, not a significance threshold.
Cumulative and peak values use the unchanged annual arrays. Strict-zero counts
and all 132 listed pair-year values remain in the two Table 16 check CSVs.

The initial bootstrap replay stores `delta_rss_star`; E02 and E03 use separate
CSV columns `T12_null` and `T12_null_E03`. Follow-up bootstrap tables link to NPZ
arrays through `null_array_key`. `seed_uint64` must be parsed as an integer from
its decimal text, never through a floating-point conversion.
