# Licenses and source materials

Copyright 2026 HyoungJu Kim and Junho Choi.

| Materials | License |
|---|---|
| Author-written code in `scripts/`, executable settings in `configs/`, dependency files, README and software-use instructions | [MIT](../LICENSE) |
| Authors' derived data in `data/`, numerical outputs and table transcriptions in `results/`, original artwork in `figures/`, and research documentation in `docs/` | [CC BY 4.0](../LICENSE-DATA), to the extent of the authors' rights |
| Third-party CTI reports, source text, upstream repository materials and ATT&CK content | Respective rights holders' terms; not relicensed by this package |

The code and data licenses have different scopes. A license list in citation or
archive metadata does not mean that every file is dual-licensed. Instructions in
`docs/reproduction.md` and `docs/release.md` are associated software documentation
under MIT; data dictionaries, provenance records and scientific notes are CC BY 4.0.
License texts retain their original terms.

This package does not redistribute source CTI reports or complete extracted text.
Document identifiers, relative source paths, checksums and derived numerical
records are retained for traceability. The authors do not grant rights in
third-party titles, identifiers, trademarks or source content. References to
MITRE ATT&CK do not imply endorsement. See [MITRE ATT&CK terms of use](https://attack.mitre.org/resources/terms-of-use/).

## Upstream collections

| Collection label | Upstream repository | URL checked |
|---|---|---|
| APTnotes | https://github.com/aptnotes/data | 2026-09-26 |
| APT_CyberCriminal_Campagin_Collections | https://github.com/CyberMonitor/APT_CyberCriminal_Campagin_Collections | 2026-09-26 |

These are collection-level source references. The check date records inspection
of the public repository pages, not the original collection date. Historical
retrieval dates, commits and snapshot identifiers are unavailable in the retained
input manifests. A current repository revision must not be substituted for the
revision used in the analysis.

`data/source_manifest.csv` links each retained raw record to its collection
repository through `collection_repository_url`. This field is separate from
`retrieval_url` and `original_publisher_url`, which remain unavailable where no
document-level link was retained. APTnotes distinguishes its index from Box-hosted
report downloads; a Box download URL is not necessarily a publisher's original
URL. No file URL has been inferred from a similar title.

`data/collection_snapshots.csv` records the collection references and the status
of historical metadata. The package supports reproduction from retained derived
inputs, not reconstruction of the complete original collection snapshot.
