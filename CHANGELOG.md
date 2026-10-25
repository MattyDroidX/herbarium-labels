# Changelog

## Unreleased — English API proposal 0.1.0a2 — 2026-10-25

- Renamed public code/interfaces to English: `bryophytes.py`, `BryophyteReading`, `SheetReading`, CLI commands/options, JSON fields, catalogue statuses, messages, and report artifacts. This intentionally breaks old Python imports/command names; schema version is `0.2.0`.
- Added read-only legacy JSON/status adapters with conflict detection; preserve original file bytes, source-language literal text, uncertain dates, and human corrections.
- Translated prompt instructions and documented hashes, editorial-marker changes, and the need for live scientific comparison. Original-language examples remain unchanged.
- Added offline `demo` with synthetic deliveries and verification flags, thirteen regressions (42 tests total), a testing guide, migration guide, architecture overview, and workflow diagrams in Mermaid/SVG.
- Renamed public documentation files to English and retained maintainer-only apply/commit/push control.


- Proposed Pillow requirement raised to `>=13,<14` with a regenerated runtime lock after 37 advisory records were reported for Pillow 12.3.0; validated in an isolated review copy before maintainer application.
- Maintainer-only apply/commit/push policy recorded; remaining changes are supplied as an unapplied patch.

- English documentation, contributor instructions, package description, and release guidance, preserving scientific prompts and existing Portuguese CLI/data contracts.
- Release preparation: separate development-tool lock, explicit source-distribution contents, distribution checks, and manual Trusted Publishing workflow. Remote execution/publication is recorded only when it actually occurs.
- Bryophyte cache checks SHA-256 of image and configuration before requests. Legacy JSON remains readable in reports; incompatible results require a new output directory and are preserved.
- Exclusive transcription/batch output lock; atomic writes and valid human corrections preserved. Reports using new JSON reject changed image content.
- Per-task aggregation, including known usage from incomplete responses; concurrency remains six tasks.
- Universal runtime dependency lock with hashes and all extras; clean Python 3.12 installation and installed SDK tests using mock HTTP transport without paid calls.
- Ten regression/SDK tests added to the original fourteen, for 24 offline tests before the release-preparation checks. Scientific prompts and Sennen full-sheet processing preserved.

## 0.1.0a1 — local preparation

- Extracted bryophyte and Sennen workflows.
- Environment configuration and separation from the private project.
- Documentary schemas for people, hands, and attributions; draft profiles.
- Offline tests and an iterative roadmap.
