# Release and archive

Repository: https://github.com/xdmankg/attack-tkg.

The package is prepared for version 1.0.0. `CITATION.cff` records the actual
repository URL; no journal or archive DOI has been supplied. Packaging does not
publish a release or change repository visibility.

## Before tagging

Table 16 now states the adopted rule, `Positive Excess > 1e-12`. The table
transcription and note agree with that rule. The historical generator remains
unlocated; `numerical_notes.md` preserves that distinction.

Replace the files in the existing repository with the contents of `attack-tkg/`;
do not add another enclosing `attack-tkg` directory. Include `.gitattributes`
and retain the repository's own `.git` directory. Keep `reproduced/` and local
execution environments out of version control. Confirm public access before
using an unrestricted-access claim in the manuscript.

Release text is stored with LF line endings. `.gitattributes` also requests LF
working-tree text on Windows, so a checkout does not invalidate byte-level hashes.
The table transcriptions have been normalized before their hashes were computed;
changing the attributes file alone would not repair an older mismatched manifest.

After reviewing edits, run:

```bash
python scripts/update_checksums.py
python scripts/update_checksums.py --check
python scripts/verify.py
python scripts/check_table16.py
```

The update command refreshes both public-file hash indexes and the complete
checksum manifest. Historical `source_sha256` values are not rewritten. Review
file changes before committing, and verify a fresh checkout before tagging.

## GitHub and Zenodo

1. Enable the repository in the Zenodo GitHub integration before creating its
   release. Tag the reviewed commit `v1.0.0` and publish the GitHub release.
2. Inspect the resulting Zenodo record. Check the authors, title, version and
   file coverage. Declare both MIT and CC BY 4.0, with their separate scopes and
   third-party exclusions from `rights.md`.
3. Record the actual version DOI in `CITATION.cff` as `doi` and add a DOI link to
   README. Use that version DOI in the manuscript Data availability statement
   and dataset reference. Keep the journal article DOI separate.
4. The archived release is a fixed snapshot. A subsequent DOI-only README or
   citation update on the development branch does not change that snapshot.
   Do not move the released tag or silently replace archived content. Archive
   substantive revisions as a new version.

If the first archived files must already contain their own DOI, use a manual
Zenodo draft instead: reserve a DOI, insert it into the files, regenerate the
checksums, create the matching GitHub release, and upload that exact release to
the reserved draft. A reserved DOI is not yet a published record. Do not also
create a second automatic archive for the same release.

## Manuscript links after publication

The Data availability statement should identify the actual GitHub repository,
the archived version and its DOI. Describe the materials as derived document
mappings, temporal assignments, numerical results, analysis code and reproduction
instructions. Source CTI reports are not redistributed, and the package does not
reconstruct the original collection process. Code is MIT; authors' derived data
and research materials are CC BY 4.0 within the scope in `rights.md`.

Create the dataset reference from the published archive metadata: authors,
package title, version, year, Zenodo and the actual version DOI. Add the journal's
dataset marker where required. Do not use a placeholder DOI or claim a public
archive exists before its record is published.

## Documentation

- [Zenodo GitHub integration](https://help.zenodo.org/docs/github/)
- [Reserving a DOI for a manual upload](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/)
- [DOI reservation and GitHub integration](https://support.zenodo.org/help/en-gb/24-github-integration/73-can-i-pre-reserved-a-doi-before-a-github-release)
- [Mixed license uploads](https://help.zenodo.org/docs/deposit/describe-records/licenses/)

Zenodo documentation checked on 2026-09-26. Line-ending behavior follows
[Git attributes documentation](https://git-scm.com/docs/gitattributes), checked
on 2026-09-27.
