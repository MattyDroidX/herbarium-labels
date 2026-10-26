# herbarium-labels

Transcribe botanical labels into structured JSON and create Excel, PDF, and ZIP deliveries for human review. Built from research workflows for PO/LISU bryophytes and F. Sennen sheets, with separate scientific contracts for each collection.

## Install

Python 3.11+:

```sh
python -m pip install "herbarium-labels[all]==0.1.0a3"
```

This documentation describes **0.1.0a3**. The PyPI command applies after that version is published; before publication, install the reviewed source with `python -m pip install -e ".[all]"`. The previous alpha, [0.1.0a2](https://pypi.org/project/herbarium-labels/0.1.0a2/), is already published. Extras are `claude`, `reports`, `heif`, and `all`.

The declared compatibility floor is Pillow 11.3; the recommended hashed environment in `requirements.lock` uses Pillow 13. Compatibility with an older version does not mean it contains current security fixes. The Pillow 11.3 test is a functional integration check, not a recommendation to downgrade.

## Try it offline

No API key, network connection, or collection images are needed:

```sh
python -m herbarium_labels demo --output ./demo-output --pdf
```

Use a new directory. Open `verification.json`, `input/transcription/transcriptions.xlsx`, `input/transcription/review.pdf`, and `input/transcriptions.zip` inside it. This uses simulated readings to demonstrate delivery; it does not measure transcription accuracy. [Checked-in synthetic examples](examples/synthetic/README.md) can be opened without running Python.

## Choose a collection profile

The same CLI supports both built-in workflows and installed profile extensions:

```sh
herbarium-labels batch --profile po-bryophytes --images ./input --pdf
herbarium-labels batch --profile sennen --images ./sheets --pdf
```

`po-bryophytes` remains the default for existing commands. `sennen` sends the full sheet plus a lower-label crop and preserves separate labels. These are collection-specific readers, not general handwriting recognition.

Before a live run, set `ANTHROPIC_API_KEY` privately in your environment and choose an available `TRANSCRIPTION_MODEL`. `.env.example` is a reference and is not loaded automatically. Input images must be authorized for the provider; start with a small selection and a defined budget. Optional `TRANSCRIPTION_PRICE_IN` and `TRANSCRIPTION_PRICE_OUT` are USD per million tokens; costs remain unknown without them.

```sh
herbarium-labels transcribe --profile sennen --images ./input --output ./output --limit 1 --workers 1
herbarium-labels report --profile sennen --images ./input --output ./output
```

`report` works offline. `batch` writes `input/transcription/` and `input/transcriptions.zip`. Supported inputs are nonrecursive JPG, JPEG, PNG, HEIC, and HEIF; HEIF needs its extra. Duplicate filename stems are rejected. Originals are never modified.

## Use it from Python

```python
from pathlib import Path
from herbarium_labels import TranscriptionOptions, read_image

reading, usage = read_image(
    Path("sheet.jpg").read_bytes(),
    profile="sennen",
    options=TranscriptionOptions(model="YOUR_AVAILABLE_MODEL", max_retries=0),
)
for label in reading.labels:
    print(label.origin, label.literal_text)
```

Clients, model settings, request limiting, field mapping, and review translations are caller-configurable. See [integration examples](docs/INTEGRATION.md) for Taxa's `cota` mapping and host-owned translations. These extension options require 0.1.0a3; the published 0.1.0a2 exposes `sennen.read_labels(content, client=None)`.

## Process folders from Python

The Python API takes paths and keyword arguments directly:

```python
from herbarium_labels import TokenPrices, TranscriptionOptions, transcribe_folder, create_report

options = TranscriptionOptions(model=selected_model, max_retries=2,
    prices=TokenPrices(input_rate, output_rate, model=selected_model))
totals = transcribe_folder("input", "output", profile="sennen", options=options, limit=1)
reports = create_report("input", "output", profile="sennen", messages=report_translations)
```

`batch_folder` performs transcription and delivery together. Price precedence is `prices=` > `options.prices` > environment, and the selected rates apply to both stages without modifying the supplied options. For separate calls, use `options.prices` for transcription and pass the same object as `create_report(..., prices=options.prices)`. `register_profile` adds a Python profile in the current process; installed packages can advertise profiles to the CLI through `herbarium_labels.profiles` entry points. Run `herbarium-labels profiles` to list names. See the [integration guide](docs/INTEGRATION.md) for complete contracts and plugin metadata.

Report messages may be a mapping or callback. For a Portuguese PO/LISU report:

```sh
herbarium-labels report --profile po-bryophytes --images ./input --output ./output \
  --messages-json examples/synthetic/report-messages-po-pt.json
```

Only presentation changes; literal labels and uncertainties retain their source text. [Portuguese synthetic report examples](examples/synthetic/README.md) include Excel/PDF and a preview.

## Continue a legacy output folder

For an older batch whose existing JSON is in `input/transcricao/json/`, select that output folder explicitly:

```sh
herbarium-labels batch --profile po-bryophytes --images ./input \
  --output ./input/transcricao --accept-existing --pdf \
  --messages-json examples/synthetic/report-messages-po-pt.json
```

`--accept-existing` does not search for or rename old folders. Without `--output`, the default is `input/transcription/`. The example preserves existing JSON and writes the delivery archive to `input/transcricao.zip`. New photographs still require an authorized provider request.

## Review and reuse

Literal spelling, line breaks, and uncertainty remain distinct from interpretation. Suggestions never edit a database or approve a reading. Code is MIT-licensed; image, API-use, and redistribution rights remain separate. Preserve [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

Cache identity includes the profile, prompt, model, schema, image policy, and codecs. Strict reuse is the default. To continue a reviewed older folder, explicitly use `--accept-existing`; an acceptance ledger preserves the original JSON and records its association with the current image. Recorded image mismatches and invalid readings remain blocked. See [continuing older folders](docs/INTEGRATION.md#continue-an-older-reviewed-folder).

## Develop

```sh
python -m pip install --require-hashes -r requirements.lock
python -m pip install --no-deps -e .
python -m unittest discover -s tests -v
```

See [testing](docs/TESTING.md), [contributing](CONTRIBUTING.md), [architecture](docs/ARCHITECTURE.md), [workflow](docs/WORKFLOW.md), [migration](docs/MIGRATION.md), and [publishing](docs/PUBLISHING.md). Research provenance and evaluation limits are documented in [EVIDENCE.md](docs/EVIDENCE.md). Live evaluation of this extracted alpha, broad Unicode/long-text report coverage, and curated handwriting attribution remain ongoing work.

The separately hashed `requirements-compat.lock` selects Pillow 11.3 for functional compatibility checks; `requirements.lock` remains the recommended current environment.
