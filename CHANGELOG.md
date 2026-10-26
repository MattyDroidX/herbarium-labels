# Changelog

## Unreleased — 0.1.0a3

- Document batch price precedence (`prices` > `options.prices` > environment) consistently for transcription and reports, with a regression test. Add explicit legacy `transcricao/` continuation examples.

- Add public path-based `transcribe_folder`, `create_report`, and `batch_folder` APIs with artifact return values; the CLI calls these directly. Existing namespace adapters remain compatible.
- Add process-local profile registration, lazy installed discovery via `herbarium_labels.profiles` entry points, CLI profile listing/selection, and explicit collision checks.
- Localize Excel sheet/column names and PDF presentation through mappings/callbacks or CLI JSON; preserve literal evidence and validate sheet names before batch requests.
- Add explicit `--accept-existing` historical-reading reuse with a separate acceptance ledger, unchanged JSON, source/hash/schema checks, and clear marking of unverified historical image associations.
- Name the collection-specific rules `sennen_suggestions`, retaining old imports. Derive suggestion model labels from the supplied reading options, accept explicit `TokenPrices`, and standardize default retries at 2.

- Share image preparation, structured Claude requests, cache/persistence, and Excel/PDF/ZIP export through explicit collection profiles. The CLI selects built-in or installed profiles through `--profile`; existing commands default to PO/LISU.
- Add caller-configurable field mappings and review messages for Sennen suggestions, including Taxa's `shelfmark` to `cota` boundary mapping. Fix the mixed-language default text.
- Expose per-call options and injected clients, consistent `TranscriptionError`, explicit request contexts, and client resource ownership. Remove implicit module-wide semaphore/history; the old rate helper requires a host callback.
- Stop upscaling small Sennen images; preserve full-sheet and lower-crop views. New profile/preparation cache identity requires a fresh output directory or explicit `--accept-existing` reuse; both preserve previous JSON.
- Permit Pillow `>=11.3,<14` for functional compatibility; retain Pillow 13 in the primary hashed lock and add a separate legacy-compatibility check.
- Update the public README and integration guide; remove the obsolete English API patch. Exclude internal maintenance records from source distributions.
- Pin GitHub Actions to upstream commit SHAs and configure reviewed Dependabot updates. CLI transcription failures return a nonzero status.

## 0.1.0a2 — 2026-10-25

- Published English API alpha to TestPyPI and PyPI, with maintainer-reported TestPyPI wheel tests (42 passed) and a clean PyPI install/CLI check.
- English modules, commands, schemas, messages, and report artifacts; read-only legacy Portuguese JSON/status adapters preserve literal text and source files.
- Offline synthetic demonstration, migration/testing guides, architecture/workflow diagrams, public demonstration assets, and distribution checks.
- Content/configuration caching, conservative resume, atomic JSON, exclusive output lock, task aggregation, and protection of human corrections.
- Separate collection contracts, documentary catalogue drafts, provenance/licenses, hashed dependencies, and manual Trusted Publishing.

## 0.1.0a1 — local preparation

- Extracted bryophyte and Sennen workflows from research code.
- Environment configuration and separation from the private project.
- Documentary schemas, draft handwriting profiles, offline tests, and iterative roadmap.
