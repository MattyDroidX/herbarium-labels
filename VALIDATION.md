# Validation record

Date: 2026-10-25. Proposed English API alpha: `0.1.0a2`; record/catalogue schemas: `0.2.0`. All current work is in an isolated proposal, supplied as a cumulative unapplied patch. The maintainer controls apply, commit, and push.

## Practical evidence and earlier checks

The maintainer reports research use, review, and acceptance of the original workflows. Preserve this evidence and its limits; see [EVIDENCE.md](docs/EVIDENCE.md). A real workbook was inspected read-only: 549 records per sheet, 549 embedded images, literal text throughout, 306 records with uncertainty, no formula cells, existing local links. This was not a full paleographic review; uncertainty is not a confirmed error. No private result is redistributed.

Earlier milestones passed 14 original offline tests, then 24 after cache/concurrency changes, then 29 after distribution checks. Extraction and those preceding increments preserved the original prompt strings. Original-source hashes/provenance remain in NOTICE.md.

## English API proposal

- Modules/classes, CLI commands/options, JSON fields, catalogue statuses, messages, report headings/paths, and documentation filenames are now English. Historical names, scientific quotations, and literal label values retain their source language.
- Version `0.1.0a2` explicitly changes old import/command names; see [MIGRATION.md](docs/MIGRATION.md). The planned canonical v2 is not implemented.
- Legacy JSON/status keys are read into copies without rewriting source files. Conflicts and unsupported versions are rejected. Tests preserve ambiguous dates, leading zeros, original-language uncertainty, literal lines, and JSON byte hashes.
- English prompt instructions are intentionally different. [PROMPT_CHANGES.md](docs/PROMPT_CHANGES.md) records hashes/policy changes and the need for a live scientific comparison. A mock-provider test cannot prove equivalent transcription quality.

## Automated and artifact checks

- **42 offline tests passed** against the source proposal on Linux/Python 3.12.14 with Pillow 13.0.0. This includes installed Anthropic 1.17.0 through mock HTTP, full sheet plus crop, separate labels, cache/failure/resume/concurrency, reports, safe spreadsheet text/links, distribution restrictions, English schemas/CLI, and legacy migration.
- The new `demo` command passed all verification flags with no API key or network: one simulated bryophyte request, cache reuse without another request, one simulated sheet request, original preservation, English JSON/workbook, safe formula-like text, ZIP integrity, and image links before/after extraction.
- A synthetic PDF was rendered and visually inspected: English headings, image, literal text, uncertainty, and review checkboxes were readable without observed clipping/overlap in this short sample. This does not validate extensive Unicode or long-text pagination.
- Architecture/workflow Mermaid sources and standalone SVGs were created. SVGs were parsed/rendered and visually inspected; the Mermaid text is provided for GitHub rendering, which has not been executed remotely.
- English wheel/source built successfully with the locked setuptools 84.2.1 backend; `twine check --strict` and distribution checks passed (15 wheel members and 60 source-archive files). A fresh environment installed the actual wheel with no source-path override: **42 tests passed**, console/module help passed, version `0.1.0a2` and `site-packages` import location confirmed.
- Local documentation links, workflow YAML syntax, SVG XML and embedded Mermaid source consistency, Python/TOML syntax, and unchanged dependency-lock bytes were checked. The public-file manifest was refreshed.
- Catalogue JSON, four draft profiles, and generated schema are updated to English statuses/schema 0.2.0; no new historical facts or attributions were added.

## Dependencies, publication, and limitations

The preceding advisory scan reported 37 known advisory records for Pillow 12.3.0. The cumulative proposal requires Pillow 13 and retains the corrected hashed runtime lock. The dependency graphs/locks are unchanged from the preceding audited proposal: pip-audit/PyPI reported no known vulnerabilities for the Linux/Python 3.12 runtime and development-tool selections on 2026-10-25. Those scans were not repeated solely for identifier changes; other marker branches require their own checks.

The development lock includes setuptools 84.2.1. Recommended builds use `python -m build --no-isolation` after installing that lock. Default isolated builds may resolve a different allowed backend. The distribution checker performs a limited credential-pattern/allowlist check, not an external audit.

No live Anthropic call, paleographic comparison of translated prompts, real HEIF decoding, complete long/Unicode export review, or remote CI run was performed here. The configured matrix requests Linux/Windows and Python 3.11–3.14, without claiming successful remote results. Provider/model availability and prices require verification before any paid test; images must be permitted and a budget agreed.

Known behavior remains: duplicate filename stems are rejected; IDs/manifests/deduplication and native review events/import are future work. Standalone reports do not acquire a transcription lock. Inspect transcribe's failure summary; per-image failures do not always imply a nonzero command status. Batch refuses incomplete delivery. Lost responses may require repeat paid requests.

No working-tree or Git mutation occurred during this English-code continuation. No assistant apply, commit, tag, push, TestPyPI upload, or PyPI upload occurred. Publication commands are for the maintainer after review/application, using [PUBLISHING.md](docs/PUBLISHING.md).
