# Development handoff

Updated: 2026-10-25. Version: local alpha `0.1.0a2`. This document distinguishes the working tree from the remaining unapplied release proposal.

## Maintainer intent and control

Share a useful open library built from research workflows, complementary to Hespi. Research use and acceptance by researchers were reported by the maintainer; preserve that evidence and its limits. English documentation is required for international reuse.

The selected source destination is `MattyDroidX/herbarium-labels`; the SSH remote was configured at the maintainer's request. The intended package route is TestPyPI followed by PyPI.

**Only the maintainer applies changes, commits, or pushes unless explicitly delegated.** This instruction also covers repository patch application. After this restriction was given, remaining edits/builds were prepared in a temporary review copy. Do not modify the working tree or Git state to finish the proposal without authorization. No commit, push, tag, or package upload has been made by the assistant. SSH access is unnecessary for preparation when the maintainer handles remote operations.

## Provenance and current implementation

See `NOTICE.md` for original TSennen/Taxa source references and hashes. The private application, deployments, databases, uploads, backups, and research outputs must remain separate. Personal workstation paths are not required in public documentation.

- `src/herbarium_labels/bryophytes.py`: `transcribe`, `report`, `batch`, `demo`; Claude/Pydantic, per-image JSON, Excel, optional PDF, ZIP.
- `src/herbarium_labels/sennen.py`: full sheet plus lower crop, multiple labels, structured fields, advisory suggestions; no database writes or automatic human approval.
- Environment key/model/prices; unknown cost without configured tariffs. Optional HEIF dependency, rotation/path/collision checks, atomic JSON.
- `catalog.py`: sources, people, hand samples, and attributions with reference/evidence checks.
- `library/`: catalogue/schema and four draft people, without invented roles, aliases, samples, or confirmed attributions.
- Content/configuration cache checks before requests; incompatible/legacy JSON requires a fresh output directory while remaining readable by reports.
- Per-task results and central aggregation, known incomplete-response usage, six workers, exclusive transcription/batch output lock.
- Runtime lock with hashes and all extras. Extraction originally preserved the prompts. The English API proposal now translates them deliberately; equivalent live scientific quality remains untested.

## English release preparation

Documentation, package description/docstrings, contributor instructions, release guide, source manifest, distribution checker/tests, and CI/publication workflows were prepared. The source tree and earlier local artifacts were modified before the maintainer-only application rule. Remaining translations, dependency correction, and refreshed manifests are supplied as an **unapplied patch** against that tree.

The review proposal changes Pillow from `>=11.3,<13` to `>=13,<14` after the advisory check reported 37 known vulnerability records for locked Pillow 12.3.0. It regenerates the runtime lock and locks the build backend with development tools. The preceding documentation-only proposal passed 29 offline tests on both source and installed wheel, metadata/content/license checks, and advisory scans with no known vulnerabilities reported for the current Linux/Python 3.12 dependency selection. Details are in `VALIDATION.md`; these changes must not be described as already applied to the maintainer's working tree.

## Verification and practical evidence

Original extraction: 14 synthetic/offline tests passed. Cache increment: 24 passed, including installed Anthropic 1.17.0 with mock HTTP transport. Release checks added five distribution regressions, for 29 tests before testing the remaining proposal.

The real research workbook was inspected read-only: 549 records per sheet, 549 embedded images, literal text throughout, 306 records with uncertainty, no formula cells, valid local links. This is not a complete paleographic review and does not mean 306 errors. Private results are not packaged. Historical agreement/cost figures and limits remain in `docs/EVIDENCE.md`.

See `VALIDATION.md` for current local commands, package-installation checks, advisory findings, and outstanding remote checks. Do not invent successful CI or uploaded package URLs.

## Known limitations and future work

- No example retrieval, profile injection, automatic handwriting attribution, generic segmentation, native review events/import, or canonical v2 integration.
- Filename-stem collisions remain blocked. Occurrence IDs, manifests, cross-occurrence deduplication, and automatic candidate revisions remain proposed.
- Current interfaces are English: `bryophytes.py`, `transcribe`/`report`/`batch`/`demo`, English fields/reports/statuses. Legacy data is read in memory; old imports/commands are renamed. Preserve literal evidence in its source language. Review `docs/MIGRATION.md` and `docs/PROMPT_CHANGES.md`.
- Use fresh output after image/configuration/codec changes. Legacy identity is not inferred. Stale locks require checking for an active process before removal; standalone reports do not acquire a write lock.
- Lost responses may require repeat paid requests. Failure without usage cannot prove zero billing.
- PDF Unicode/long-text behavior and complete visual report inspection remain pending. No layout change was introduced in the release documentation work.
- Live provider/model execution and real HEIF decoding remain unverified in the extracted alpha; paid integration needs permitted images and a defined budget.
- Remote matrix runs, TestPyPI/PyPI account setup, package-name availability, private reporting configuration, and publication still need actual execution.

## Next steps

1. Maintainer reviews/applies the remaining patch; confirm manifest hashes and rerun the documented checks on the applied tree.
2. Maintainer reviews the public-file allowlist and actual Git author identity, then commits/pushes without overwriting existing remote history.
3. Inspect actual Linux/Windows and Python-version CI results.
4. Configure independent TestPyPI/PyPI Trusted Publishers for `publish.yml` and environments `testpypi`/`pypi`.
5. Maintainer tags the reviewed version, publishes to TestPyPI, and verifies the uploaded wheel in a clean environment before triggering PyPI.
6. Record real URLs, hashes, and results. Update the verified private reporting route.
7. Continue the scientific roadmap: long/Unicode reports with visual inspection; permitted live integration; sourced, rights-cleared handwriting curation.

Do not change the private research environment to prepare this library.

## English API continuation

The cumulative proposal now includes the preceding English-release preparation plus the English code/API migration. Apply only the latest cumulative patch against the unchanged working tree; do not apply it on top of the earlier patch. Version is `0.1.0a2`, schemas `0.2.0`; documentation filenames are English. No working-tree or Git mutation occurred during this continuation.

New regression checks cover legacy alias conflicts, preserved literal/JSON bytes, English schemas/statuses/CLI, legacy locks, and the offline demo. The demo creates inspectable files and verification flags; it is not a paleographic accuracy experiment. Architecture/workflow SVG and Mermaid files are in `docs/diagrams/`; use `docs/TESTING.md` to reproduce the checks.

Final local verification for this continuation: 42 tests passed against source and the installed English wheel in a fresh Python 3.12 environment. Console entry point and module import/version were checked; wheel/source metadata/allowlist checks passed. Short synthetic PDF and both SVG diagrams were rendered and visually inspected. Prompts were deliberately translated and require a separate authorized scientific comparison; no live call was performed.
