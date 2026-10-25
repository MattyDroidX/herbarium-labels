# herbarium-labels

An open Python library for transcribing botanical labels and producing reviewable JSON, Excel, PDF, and ZIP files. It extracts workflows used in research and TSennen/Taxa, with results reviewed and accepted by researchers according to the maintainer. It complements Hespi and other tools.

## Current scope

Proposed English API alpha **0.1.0a2**, prepared as an unapplied patch for maintainer review. Code, commands, schemas, messages, and report interfaces are English; literal label text always retains its source language.

- **Bryophytes:** PO/LISU-specific reading, JSON persistence, cache verification, and reports.
- **Sennen:** full sheet plus lower crop, separate labels and structured fields through a Python API.
- **Catalogue:** documentary validation of people, hands, samples, sources, and attributions; four uncurated drafts.
- **Offline demonstration:** synthetic images and simulated responses, with delivery checks.

Example retrieval, profile injection, automatic handwriting attribution, generic segmentation, and native review import are future work. English interfaces do not imply general paleographic accuracy for every collection. See [the architecture](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/ARCHITECTURE.md), [workflow](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/WORKFLOW.md), and [roadmap](https://github.com/MattyDroidX/herbarium-labels/blob/main/PLAN.md).

## Install locally

Requires Python 3.11+. From the reviewed source tree:

```sh
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --require-hashes -r requirements.lock
python -m pip install --no-deps -e .
```

The lock includes all extras and Pillow 13. An alternative is `python -m pip install -e ".[all]"`, which resolves declared version ranges. Extras: `claude`, `reports`, `heif`, and `all`. Local verification used Linux/Python 3.12; the configured remote matrix is not a claim of completed CI.

Source destination: [MattyDroidX/herbarium-labels](https://github.com/MattyDroidX/herbarium-labels). No TestPyPI/PyPI upload is claimed. The wheel contains runtime modules; the repository/source archive also include documentation, tests, tools, and the draft catalogue.

## Try the entire delivery offline

No API key, network connection, or real collection images are needed:

```sh
python -m herbarium_labels demo --output ./demo-output --pdf
python -m unittest discover -s tests -v
```

Use a new directory for each demo. Open `demo-output/verification.json`: `all_passed` should be `true`. Inspect `demo-output/input/transcription/transcriptions.xlsx`, `review.pdf`, and `demo-output/input/transcriptions.zip`. The mock supplies known fixture readings; this demonstrates the pipeline, not OCR/paleographic quality. [The testing guide](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/TESTING.md) explains every artifact and check.

## Transcribe authorized images

Set `ANTHROPIC_API_KEY` privately in the environment. `.env.example` is a reference, not automatically loaded configuration. `TRANSCRIPTION_MODEL` selects the model; verify availability before a paid run. Optional input/output prices are USD per million tokens; without both, estimated cost is unknown.

```sh
herbarium-labels transcribe --images ./input --output ./output
herbarium-labels report --images ./input --output ./output
herbarium-labels batch --images ./input --pdf
```

`python -m herbarium_labels` is equivalent. `transcribe` writes readings; `report` creates reports without an API request; `batch` requires a reading for every input, then produces a delivery ZIP. Its fixed output directory is `input/transcription/`; the archive is `input/transcriptions.zip`. Originals are unchanged.

Inputs are nonrecursive JPG, JPEG, PNG, HEIC, or HEIF files. HEIF requires its extra. Duplicate stems are rejected. New JSON uses English keys and schema version `0.2.0`. Existing Portuguese JSON is normalized in memory for reading/reporting without changing its bytes. The old Python module/CLI names have been renamed; see [migration](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/MIGRATION.md).

## Resume without replacing human work

Cache identity includes image/configuration hashes: prompt, model, schema, transformation, SDK, and codecs. The selected batch is checked before requests. Incompatible or unverifiable existing results stop transcription; preserve them and use a new output directory. Legacy results are not automatically promoted into verified cache.

`.transcription.lock` prevents overlapping transcriptions/batches; an existing legacy lock also blocks a new run. Check for an active process before removing stale locks. Standalone `report` must run without another writer. Lost responses may require another paid request; exactly-once execution is not guaranteed.

## Process a Sennen sheet

```python
from pathlib import Path
from herbarium_labels.sennen import read_labels

reading, usage = read_labels(Path("sheet.jpg").read_bytes())
for label in reading.labels:
    print(label.origin, label.literal_text)
```

The collection-specific lower crop complements the full sheet. The function returns suggestions/readings, not database edits or human approval. See [architecture](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/ARCHITECTURE.md) for the independent catalogue and host-review boundaries.

## Validate and build

```sh
python -m unittest discover -s tests -v
python -m pip install --require-hashes -r requirements-dev.lock
python -m build --no-isolation
python -m twine check --strict dist/*
python tools/check_dist.py dist/*
```

See [testing](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/TESTING.md), [validation records](https://github.com/MattyDroidX/herbarium-labels/blob/main/VALIDATION.md), [contribution instructions](https://github.com/MattyDroidX/herbarium-labels/blob/main/CONTRIBUTING.md), and [maintainer-controlled publication](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/PUBLISHING.md). Only the maintainer applies changes, commits, or pushes unless explicitly delegated.

## Scientific safeguards and rights

Preserve literal spelling, line breaks, and uncertainties; normalization is separate. Institution, collector, determiner, taxonomic author, and writer are distinct roles. Draft profiles do not establish authorship. See [handwriting curation](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/HANDWRITING.md) and [practical evidence](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/EVIDENCE.md).

Prompt instructions were translated for the English API. Their policies are documented and tested structurally, but equivalent scientific performance has not been demonstrated by the offline suite. Live evaluation needs permitted images and a defined budget; see [prompt changes](https://github.com/MattyDroidX/herbarium-labels/blob/main/docs/PROMPT_CHANGES.md).

Code is MIT-licensed; [LICENSE](https://github.com/MattyDroidX/herbarium-labels/blob/main/LICENSE) and [NOTICE.md](https://github.com/MattyDroidX/herbarium-labels/blob/main/NOTICE.md) preserve provenance. Image/API/redistribution rights are independent. A live provider run, real HEIF decoding, and complete long/Unicode report validation remain pending; see [security](https://github.com/MattyDroidX/herbarium-labels/blob/main/SECURITY.md) and [validation limits](https://github.com/MattyDroidX/herbarium-labels/blob/main/VALIDATION.md).

## Checked-in demonstration files

Open [examples/synthetic/README.md](examples/synthetic/README.md) to inspect the synthetic input image, rendered PNG preview, PDF, workbook, JSON, and verification results directly from the repository. These are simulated fixtures, not research or OCR-quality evidence.
