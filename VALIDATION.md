# Validation record

Date: 2026-10-26. Release target: `0.1.0a3`; preceding implementation patches have been applied by the maintainer. This final release-polish increment is prepared/tested in isolation for maintainer application. No tag, commit, push, or upload was made by the assistant.

## Final release-polish checks

- **84 offline tests passed** against source on Linux/Python 3.12.14 with Pillow 13, and against the installed proposal wheel with Pillow **13.0.0** and **11.3.0**. All SDK/report extras were present in the installed-wheel environments; no SDK test was skipped there.
- The new regression confirms that explicit batch `prices` overrides `options.prices` in both transcription and report estimates without mutating caller options. Production behavior is unchanged; function documentation and integration examples now explain the precedence.
- Changelog now permits a fresh output directory **or explicit `--accept-existing`**. README/integration/release instructions show selecting `input/transcricao/` explicitly; directory selection/defaults are unchanged. Original JSON is not rewritten.
- Wheel/source builds, strict Twine metadata, distribution/license/credential-pattern checks, dependency consistency, workflow SHA policy, public-file hashes, and local Markdown links were checked. No report layout, scientific prompt/schema, image transform, dependency-lock, or suggestion-comparison change was introduced.
- Independent maintainer evidence covers all six integration areas and the copied six-photo batch: strict zero requests; acceptance one simulated request; five old JSON files byte-identical; subsequent zero requests. Their 83-test Pillow 11.3 run initially skipped an absent-SDK test, subsequently rerun successfully with Taxa's Anthropic 1.17 interpreter. See docs/EVIDENCE.md; private fixtures were not independently executed here.
- Read-only index metadata checks on 2026-10-26 showed PyPI/TestPyPI latest version 0.1.0a2 and no 0.1.0a3 files. These are preparation-time checks, not publication results.

## Release scope and limits

No paid API requests or changes to original research data occurred. Provider behavior is simulated in the ordinary suite. Broader scientific/live-provider evaluation, real HEIF examples, and long/Unicode PDF coverage remain separate work. Pillow 11.3 support is functional compatibility; the primary lock retains Pillow 13.

The maintainer controls application and publication. Follow docs/PUBLISHING.md for a reviewed commit, matching v0.1.0a3 tag, TestPyPI installation verification, and then PyPI. Keep existing published versions/tags intact.

---

# Earlier validation record

Date: 2026-10-26. Published baseline: `0.1.0a2`. The maintainer applied the preceding 0.1.0a3 reuse patch. This **incremental folder-API follow-up** is prepared in isolation and remains unapplied/unpublished. It keeps the unreleased version target at `0.1.0a3`; no new upload is claimed.

## Maintainer integration evidence

The maintainer reported 61 passing tests on the applied preceding patch and exactly matching suggestions against Taxa's current `app/transcription.py` in three cases using Pillow 11.3, `shelfmark` to `cota`, and Portuguese templates: shelfmark spacing, Roman-numeral dates, and uncertainties. This is reported host evidence for those cases; the private application/fixtures were not independently executed or changed here. See docs/EVIDENCE.md.

## Follow-up verification

- **83 offline tests passed** against the proposal source on Linux/Python 3.12.14 with Pillow 13.0.0.
- The actual proposal wheel was installed in clean environments with Pillow **13.0.0** and **11.3.0**; **83 tests passed in each**. Imports were confirmed in `site-packages`, and dependency consistency passed. The compatibility environment uses the same pinned graph as `requirements-compat.lock`; the older Pillow wheel was hash-verified and installed locally after the current lock. No claim is made that an offline package index contained that older wheel.
- Twenty-two new tests cover plain path arguments/artifact returns, CLI delegation, per-call prices/model labels, common retry defaults, host request contexts, lazy registration/discovery and collision failures, a synthetic installed entry point used by a fresh CLI process, translated report mappings/callbacks, and explicit legacy acceptance/continuation.
- Acceptance tests preserve original JSON bytes and historical model/usage, request only new photographs, permit no-key reuse, mark absent historical image hashes as unverified, reject recorded/accepted image changes, validate every selected old record before saving acceptance or requesting, and retain explicit renewal history after later human edits. Malformed data/wrong schemas/profiles remain blocked. No real collection folder was migrated.
- Public named folder APIs use paths and keyword arguments; namespace APIs remain compatibility adapters. CLI `profiles` discovers registered/installed names without loading plugin factories, and selected plugins use the standard `herbarium_labels.profiles` entry-point group.
- A complete Portuguese mapping generated public synthetic Excel/PDF in `examples/synthetic/portuguese/`. Workbook sheet/column labels and formula-safe literal cells were checked. PDF text extraction and document metadata confirmed Portuguese presentation and unchanged literal text; the PDF was rendered and visually inspected, with no observed clipping/overlap in this short fixture. It does not establish complete Unicode/long-text coverage.
- Wheel/source builds, strict Twine metadata checks, allowed contents/licenses/credential-pattern checks, Python/TOML/YAML syntax, workflow SHA policy, local documentation links, and public-file hashes were checked. Updated SVGs were rendered and visually inspected.
- Scientific prompt strings, reading model definitions, suggestion-comparison rules, and image preparation are unchanged from the applied 0.1.0a3 baseline. Only suggestion model-label selection and configuration/presentation boundaries change.

## Limits and control

These are software-contract and synthetic artifact checks. They do not establish every collection's transcription accuracy, all private Taxa cases, remote CI results, real HEIF decoding, or a live provider run. The standard lock remains on Pillow 13; supporting 11.3 functionally does not backport image-decoder fixes. Prices are caller-supplied estimates and never assumed to be provider billing evidence.

Acceptance is a deliberate historical import, not scientific approval or a claim that old readings used a new pipeline. Without an old image hash, the historical source association cannot be verified. Keep the ledger with JSON and sources. Reports regenerate from JSON and do not import edits made only in Excel. Unchanged scientific safeguards and original research evidence remain applicable.

No assistant application to the maintainer tree, commit, tag, push, publication, paid request, or private-data migration occurred. The incremental patch is for the maintainer to review and apply over the current tree.

---

# Earlier validation record

Date: 2026-10-26. Published baseline: `0.1.0a2`. Isolated reuse proposal: `0.1.0a3`; not applied to the maintainer working tree and not published. Schemas remain `0.2.0`.

## Published baseline

The maintainer's session logs show tag `v0.1.0a2` pushed, successful TestPyPI download/install, **42 tests passed** against that wheel, then a fresh PyPI installation of `herbarium-labels[all]==0.1.0a2` and successful CLI help. This supersedes historical "unapplied patch"/"no upload" preparation statements. It does not assert results for every remote CI matrix job.

## Reuse proposal checks

- **61 offline tests passed** against the isolated source on Linux/Python 3.12.14 with Pillow 13.0.0.
- A clean environment installed the actual proposed wheel; import location was confirmed in `site-packages`, version `0.1.0a3`. **61 tests passed** with Pillow 13.0.0 and dependency consistency passed.
- A separate clean environment installed the same wheel with Pillow **11.3.0** and the locked dependency graph. Dependency consistency and **61 tests passed**. The downloaded Pillow wheel matched the SHA-256 in PyPI metadata. `requirements-compat.lock` records all hashes for this compatibility environment.
- Nineteen new integration regressions cover host field maps on input/output, translated review rendering, literal uncertainties, missing keys, injected/owned clients, failure cleanup, explicit options and request context, no-upscaling/EXIF/tiny crops, custom profiles, Sennen cached deliveries, human corrections, cross-profile conflicts, and CLI failure status.
- The installed Anthropic SDK was exercised through mock HTTP transport, not a real provider. Its test fixture now distinguishes client ownership: internally created clients close, injected clients remain open.
- Wheel/source build, strict Twine metadata checks, public-content/license/credential-pattern checks, workflow SHA policy, YAML syntax, and SVG XML checks passed. Internal maintenance files and the obsolete review patch are excluded from the distribution.
- Action SHAs were resolved from the upstream repositories on 2026-10-26. Dependabot proposes future action updates. Pinning is checked separately from dependency locks.
- Architecture/workflow SVGs were rendered and visually inspected; text and directional connectors were readable. A synthetic Sennen delivery produced JSON, Excel, PDF and a valid ZIP. The one-page PDF was rendered and inspected: separate Sennen/Porto literal blocks, image, uncertainties, and review fields were readable without observed clipping in this short fixture.
- PO/LISU prompt and reading schemas are unchanged. Sennen prompt changes only "enlarged crop" to "crop", aligning the wording with no upscaling. This image-policy change has a new cache identity; historical results are preserved and need a fresh output directory for new transcription.

## Limits

These tests establish the stated software contracts for Linux/Python 3.12 and the selected dependencies. They do not prove direct integration with a running Taxa server, other Pillow versions, remote CI success, scientific equivalence, real HEIF decoding, or broad long/Unicode PDF coverage. No private research data or paid API calls were used.

Pillow 11.3 is a functional compatibility floor, not a security recommendation. Later Pillow releases contain decoder fixes; the primary hashed lock remains Pillow 13. The unchanged primary dependency graph retains its earlier audit record; no new external security audit is claimed. Hosts must evaluate the dependencies they actually deploy.

The new shared pipeline retains conservative cache behavior: mismatched/legacy identities stop, originals and human corrections are not overwritten, and incomplete usage is aggregated without saving incomplete readings. Standalone reports still require no competing writer. Native review import, example retrieval, generic segmentation, and automatic handwriting attribution remain outside this proposal.

The maintainer alone reviews/applies, commits, pushes, tags, and publishes unless explicitly delegated. No assistant Git mutation or publication occurred.

---

# Historical validation record

Date: 2026-10-25. Proposed English API alpha: `0.1.0a2`; record/catalogue schemas: `0.2.0`. At this historical checkpoint, the English migration was an isolated proposal; the maintainer subsequently applied and published it. The maintainer controls apply, commit, and push.

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
