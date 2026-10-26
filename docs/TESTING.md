# Test and understand the library

All commands here are for a maintainer-reviewed/applied source tree. The assistant prepares patches in isolation; only the maintainer applies changes, commits, or pushes unless explicitly delegated.

## 1. Install and inspect the interface

Follow the virtual-environment installation in [README.md](../README.md), then run:

```sh
python -m herbarium_labels --help
python -m herbarium_labels transcribe --help
python -m herbarium_labels report --help
python -m herbarium_labels batch --help
python -m herbarium_labels demo --help
```

Use `--images` for an input directory and `--output` for transcription/report output. `batch` derives its output under the images directory. `transcribe --limit N --sample` selects a spaced sample; it still calls the configured live provider unless invoked inside the offline demonstration.

## 2. Run the automated offline suite

```sh
python -m unittest discover -s tests -v
```

Expected result for the 0.1.0a4 candidate: 105 tests and `OK`, without a real API key. The SDK contract test needs the `claude` extra; it uses mock HTTP transport, not the provider service. Full-suite reporting/demo tests need the `reports` extra. Installing the runtime lock provides both. `PYTHONPATH=src` is available for source-only development but must be unset when checking a wheel.

| Test file | Main evidence |
| --- | --- |
| `test_core.py` | Rotation, paths, research-flow compatibility, reports, full sheet/crop, separate labels |
| `test_cache.py` | Image/config changes, preserved corrections, preflight, locking, failure/resume, token aggregation |
| `test_sdk.py` | Actual installed SDK serializes schemas and parses simulated HTTP responses |
| `test_distribution.py` | Distribution paths, required notices/locales, forbidden files, credential-pattern rejection |
| `test_reuse.py` / `test_folder_api.py` | Host mappings, profiles/plugins, folder APIs, prices, review/report messages, historical acceptance |
| `test_localization.py` | Exact default prompt/cache compatibility, notes language, catalogue parity, CLI language selection |
| `test_english_api.py` | English interfaces, legacy reads without text changes, schema/version conflicts, demo CLI |

These are engineering checks. They do not measure transcription accuracy on real handwriting.

## 3. Inspect a full synthetic delivery

```sh
python -m herbarium_labels demo --output ./demo-output --pdf
```

The destination must not exist. On a second run choose, for example, `./demo-output-2`; the demo refuses to overwrite earlier work. The command always uses a simulated provider and temporarily replaces any real key with a dummy value. It sends no network requests and creates no charges.

```text
demo-output/
  verification.json
  sheet_reading.json
  input/
    synthetic.jpg
    transcriptions.zip
    transcription/
      json/synthetic.json
      transcriptions.xlsx
      review.pdf
      images/synthetic.jpg
      thumbnails/synthetic.jpg
  extracted/
    transcription/...
```

Check these files:

1. **`verification.json`:** `all_passed: true`, two simulated calls (one bryophyte reading, one sheet reading), unchanged original, cache reuse, safe text cells, valid ZIP, and image links before/after extraction. No real OCR is performed.
2. **Original image:** a clearly marked synthetic label. Compare it with the oriented copy; the original hash must remain unchanged.
3. **JSON:** `schema_version: "0.2.0"`, `filename`, `reading.literal_text`, `reading.uncertainties`, and cache hashes. Line breaks and literal content must match the fixture.
4. **Excel:** English sheets `Literal transcription` and `Fields`; embedded image; relative image link; collection number `001` preserved as text. The fixture begins with `=`, and its cell must remain text instead of a formula.
5. **PDF:** image, English headings, literal text, notes, uncertainty, and review checkboxes; inspect clipping, overlap, and readability. Automated header checks alone do not prove layout quality.
6. **ZIP:** extract before opening the workbook. Its relative image links must work in the extracted folder.
7. **`sheet_reading.json`:** two distinct entries in `reading.labels`, demonstrating that the full-sheet route does not flatten labels together.

The demonstration runs transcription again after persistence. The valid reading must be reused with no extra bryophyte provider call. Its verification flags make this visible without spending money.

## 4. Confirm old research files remain usable

```sh
python -m herbarium_labels report --images ./original-images --output ./old-output --no-pdf
```

The old directory should contain its original `json/*.json`. The reader maps old keys in memory, preserves literal values, and writes English-named reports; it does not rewrite those JSONs. Keep a backup and compare their hashes if testing real data. Conflicting English/legacy fields or unknown schema versions are rejected.

Never overwrite a human correction to obtain a new model result. Old cache configuration cannot be assumed equivalent to the translated prompt/schema; choose a fresh output for a new transcription. See [migration](MIGRATION.md).

## 5. Verify a distributable installation

```sh
python -m pip install --require-hashes -r requirements-dev.lock
python -m build --no-isolation --outdir dist/0.1.0a4
python -m twine check --strict dist/0.1.0a4/*
python tools/check_dist.py dist/0.1.0a4/*
python -m venv .wheel-venv
.wheel-venv/bin/python -m pip install --require-hashes -r requirements.lock
.wheel-venv/bin/python -m pip install --no-deps dist/0.1.0a4/herbarium_labels-0.1.0a4-py3-none-any.whl
.wheel-venv/bin/python -m unittest discover -s tests -v
.wheel-venv/bin/python -m herbarium_labels demo --output ./wheel-demo --pdf
```

Unset `PYTHONPATH` for the wheel commands. Use `.wheel-venv\Scripts\python.exe` on Windows. To verify import origin, print `herbarium_labels.__file__`: it must point into that environment's `site-packages`. The wheel provides runtime code; source archives additionally contain tests/docs/catalogue.

Dependency advisory scans contact public services and are separate from offline tests. Follow [PUBLISHING.md](PUBLISHING.md) for the hashed-lock scans, TestPyPI installation check, and manual PyPI sequence. Do not claim remote CI or uploads until executed.

## 6. Plan a live scientific check separately

Before any real API call, confirm image permissions, current model access, prices, and budget. Review every pilot reading against the original, including spelling, lines, uncertain dates, role separation, and label boundaries. Compare the translated prompt against an authorized baseline with the same images/model, and report denominators and limitations.

Historical research acceptance applies to the original workflows; the English prompt translation needs its own scientific comparison. A passing mock-provider demo cannot establish that equivalence. Real HEIF, extensive Unicode, long text, and different collections also require their own validation.

## 7. Inspect the documentary catalogue offline

From the repository/source archive, inspect the versioned draft data without any API:

```python
from pathlib import Path
from herbarium_labels.catalog import Catalog

catalog = Catalog.model_validate_json(Path("library/catalog.json").read_text(encoding="utf-8"))
print(catalog.schema_version)  # 0.2.0
for person in catalog.persons:
    print(person.display_name, person.status)  # four drafts
print(len(catalog.samples), len(catalog.attributions))  # 0, 0
```

A valid schema confirms structure and references. It does not establish who wrote a label, clear image rights, or make a draft profile suitable for automatic selection. The catalogue is not currently inserted into either transcription prompt.

## Reuse contract checks (available since 0.1.0a3)

Run `python -m unittest discover -s tests -v` on the reviewed source and installed wheel. `test_reuse.py` covers Taxa mappings on input/output, complete host translations, literal uncertainty preservation, missing-key errors, client ownership, per-call options, optional host limiting, EXIF/crop/no-upscaling behavior, custom profiles, Sennen cache/report/ZIP delivery, cross-profile cache rejection, human corrections, and CLI failure status.

The standard lock uses Pillow 13. The separate Linux/Python 3.12 compatibility job installs Pillow 11.3.0, checks dependency consistency, and reruns the synthetic suite. It verifies functionality only. Ordinary tests make no paid requests and cannot establish paleographic equivalence or a security audit of old dependencies.

Run `python tools/check_workflows.py` to reject movable action references. SHA provenance was checked against the upstream repositories; Dependabot proposes updates for maintainer review. YAML parsing and package-content checks remain separate checks.

The separately hashed `requirements-compat.lock` selects Pillow 11.3 for functional compatibility checks; `requirements.lock` remains the recommended current environment.

## Folder API follow-up

`test_folder_api.py` covers normal Python parameters and artifact return values, CLI delegation, explicit prices/model labels, common retry defaults, process-local registration, lazy plugin discovery, duplicate/factory failures, an installed entry point exercised through a fresh CLI process, report-map/callback localization, Excel title validation, and explicit existing-reading acceptance. Acceptance tests preserve JSON bytes and historical models, reuse only old readings, transcribe only new photographs, block recorded/accepted image changes and invalid profiles, validate the full batch before saving acceptance, and retain explicit renewal history after human edits.

The checked-in Portuguese synthetic delivery is a presentation example, not a real collection result. Original literal text remains unchanged. The maintainer separately reported matching Taxa suggestions for shelfmark spacing, Roman-numeral dates, and uncertainties; the private application/tests are not copied or changed here.

The release-polish regression confirms that a batch-level price override reaches both transcription and report estimates while leaving the caller options unchanged.

## Cross-platform fixture encodings

JSON fixtures containing literal non-ASCII characters must use `encoding="utf-8"`. Locale-default writes can produce CP1252 on Windows, which is not a valid encoding for the runtime JSON byte reader. The legacy Portuguese-envelope regression simulates CP1252 fallback while writing a UTF-8 fixture explicitly, then verifies that acceptance leaves every JSON byte unchanged. Do not loosen runtime decoding or force a UTF-8 CI locale to hide an invalid fixture.

## 0.1.0a4 language and distribution regression checks

The expanded suite has 105 offline tests. `tests/test_localization.py` checks frozen 0.1.0a3 prompt/cache hashes (captured before implementation in `tests/fixtures/a3-contracts.json`), injected-client requests for every notes language and an external profile, metadata/resume conflicts, unchanged source reading values, catalogue key/format-marker parity, existing Portuguese terminology, Sennen review rendering, and CLI language/JSON precedence. Distribution tests reject wheels or source archives missing locale files at their package paths.

Run all tests against source with both runtime locks, then install the built wheel in separate clean environments and rerun without `PYTHONPATH`. `requirements.lock` uses Pillow 13; `requirements-compat.lock` uses Pillow 11.3. Include the `claude` SDK/report extras through these locks so no SDK test is skipped. The publication guide includes wheel verification commands.

These tests exercise software/request contracts with simulated clients. They do not establish live model translation compliance, linguistic review of Spanish, or equivalence to every private Taxa review template. Taxa must preserve its own exact equivalence regression before replacing its implementation.

The Portuguese review regression additionally pins the maintainer-supplied Taxa source/exsiccata wording and a complete rendered review with its original uncertainty. This presentation-only follow-up keeps the scientific request and cache configuration unchanged.
