# Development handoff

Updated: 2026-10-26. Published baseline: `0.1.0a2`. Next proposal: `0.1.0a3`.

## Maintainer control

Only the maintainer applies repository changes, commits, tags, pushes, or publishes unless explicitly delegated. The maintainer applied the preceding reuse patch and reported 61 passing tests plus three equivalent Taxa cases. The maintainer has now applied the folder/plugin/localization/acceptance follow-up and independently checked all six integration areas. The final documentation/price-precedence polish is an isolated incremental proposal. Never modify the private Taxa application, databases, or deployment to prepare this package.

## Published baseline

The maintainer applied the English API patch, pushed tag `v0.1.0a2`, published to TestPyPI, downloaded its wheel into a clean environment, and reported 42 passing offline tests. They then triggered PyPI publication, installed `herbarium-labels[all]==0.1.0a2` in a fresh environment, and verified CLI help. These facts are recorded from the session logs; no unsupported assertion is made about every remote CI matrix job.

## Reuse proposal

- Shared `imaging.py`, `provider.py`, `pipeline.py`, `profiles.py`, and `pricing.py`; public `TranscriptionOptions`, `TranscriptionProfile`, `read_image`, `TranscriptionError`.
- Both built-in profiles work through cached JSON and offline Excel/PDF/ZIP; the CLI accepts `--profile`. Scientific contracts remain collection-specific.
- Sennen suggestions map canonical fields to host fields and accept complete host-owned review translations. The mixed-language default is corrected.
- No upscaling; Sennen retains the full sheet plus lower crop. No implicit global semaphore or per-user request history. The compatibility rate helper requires a host callback.
- Missing-key/provider/image/incomplete errors have a public exception; injected clients remain caller-owned. File-pipeline clients close after use.
- Pillow compatibility floor is 11.3; the recommended hashed lock remains 13. See dependency limits in docs/INTEGRATION.md.
- Actions use verified upstream commit SHAs; Dependabot proposes updates. Obsolete review patch removed; maintenance records are excluded from source distributions.

## Folder integration follow-up

The new incremental patch targets the already-applied 0.1.0a3 tree. It adds path-based folder APIs and artifact results, direct CLI delegation, registered/installed entry-point profiles, report messages and Portuguese synthetic examples, explicit historical-reading acceptance with a separate hash ledger, `sennen_suggestions` naming with a compatibility shim, explicit `TokenPrices`, options-derived model labels, and a common retry default of 2.

The follow-up passed **83 offline tests** against source and the installed wheel on Linux/Python 3.12, with Pillow 13 and 11.3. Package metadata/content checks and translated-report visual inspection passed. No private application or collection folder was modified. See VALIDATION.md and docs/INTEGRATION.md.

## Release polish

The release target remains 0.1.0a3. The final incremental patch corrects the cache changelog wording, documents `prices` > `options.prices` > environment for both batch stages, adds a regression preserving the caller options, and shows legacy `transcricao/` output explicitly. README/install instructions and docs/PUBLISHING.md now describe the intended release version and complete TestPyPI-first workflow. Tests: 84 passed against source and installed wheels with Pillow 13 and 11.3; package/dependency checks passed. The maintainer's independent 83-test/Taxa/copied-batch evidence is recorded in docs/EVIDENCE.md.

At the 2026-10-26 index check, both PyPI and TestPyPI still listed 0.1.0a2 and no 0.1.0a3 files. No new publication is claimed. Apply the final patch, review/commit/push the release tree, confirm CI, tag v0.1.0a3, validate the uploaded TestPyPI wheel, then trigger PyPI. The maintainer performs those actions.

## Before applying/releasing

Review the patch and validation record. Apply only to the matching baseline, rerun tests, inspect synthetic Sennen exports, and check installed-wheel behavior. New version is `0.1.0a3`; never overwrite the already-published tag/version. Strict cache identity remains the default. To reuse valid older JSON deliberately, choose `--accept-existing`; the acceptance ledger preserves original bytes and records whether historical image hashes were verifiable. Do not run it automatically on real data. Reports use JSON and do not import Excel-only edits. Check the host rate-policy migration before adopting.

Remaining work includes authorized live evaluation with a defined budget, long/Unicode report coverage, real HEIF samples, curated handwriting sources/examples, review import, and the broader roadmap in PLAN.md. No paid service call is included in this proposal.

The separately hashed `requirements-compat.lock` selects Pillow 11.3 for functional compatibility checks; `requirements.lock` remains the recommended current environment.

## Windows CI fixture correction

The maintainer pushed commit `904bb46`. In run [40374862961](https://github.com/MattyDroidX/herbarium-labels/actions/runs/40374862961), Ubuntu/Python 3.11–3.14, Pillow compatibility, and distribution jobs succeeded. Windows/Python 3.11–3.14 all failed in the same legacy-Portuguese JSON test. Its fixture used locale-default encoding with `ensure_ascii=False`, producing CP1252 bytes that the UTF-8 JSON reader correctly rejected.

An isolated test-only proposal specifies UTF-8 in the fixture/helper and simulates CP1252 fallback inside the existing regression. Runtime JSON handling, scientific contracts, workflows, Dependabot configuration, and dependency pins are unchanged. The original failure was reproduced locally with CP1252 file-I/O defaults. The maintainer must apply/commit/push the fix and verify the real Windows rerun before tagging 0.1.0a3. No native Windows rerun is claimed during patch preparation.

Dependabot was introduced to propose monthly GitHub Actions updates for SHA-pinned dependencies; no automerge workflow was configured. Its four major-update PRs remain separate review work. The workflow listens to both push and pull_request, explaining duplicate runs for internal PR branches.
