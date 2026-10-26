# Host integration contracts

These interfaces describe the 0.1.0a4 release candidate. The preceding 0.1.0a3 alpha is published; notes-language selection and bundled catalogues first appear in 0.1.0a4. Install the reviewed candidate source/wheel during preparation, and pin `herbarium-labels==0.1.0a4` after release. Do not use a floating alpha range in a consuming application.

The supported API and one-preceding-alpha notice policy for incompatible changes/removal are defined in the [README](../README.md#public-api-and-compatibility). Other implementation helpers remain internal.

## Canonical fields and host fields

Schemas and saved readings use English canonical names. An application translates them only at its boundary. Field mappings apply to both reading the existing record and returning a suggestion:

```python
from herbarium_labels.sennen import suggestions

rows = suggestions(
    {"cota": "12", "transcription": "Already reviewed"},
    reading,
    "sheet.jpg",
    field_map={"shelfmark": "cota"},
)
# Each row is (host_field, suggested_value, review_text).
# A changed shelfmark produces ("cota", "68/9", review_text).
```

Supported canonical keys are `transcription`, `shelfmark`, `exsiccata_number`, `collection_date`, and `original_locality`. Unspecified keys map to themselves. Unknown keys, empty host names, and collisions raise `ValueError`. Values are suggestions, never database updates.

## Taxa integration with Portuguese notes and review messages

```python
from herbarium_labels import TranscriptionOptions, load_messages, read_image
from herbarium_labels.sennen import suggestions

options = TranscriptionOptions(model=selected_model, notes_language="pt")
reading, usage = read_image(
    image_bytes, profile="sennen", client=existing_client, options=options,
)
rows = suggestions(
    record, reading, filename,
    options=options,
    messages=load_messages("pt", kind="review"),
    field_map={"shelfmark": "cota"},
)
```

The injected client remains caller-owned. This changes only generated uncertainty notes and review presentation; source text is not translated. Adjust templates with a mapping/callback if the host needs its existing exact wording.

Taxa adoption is a separate Taxa release after 0.1.0a4 is published and verified. Only then replace its `app/transcription.py`, pin the exact package version in Taxa's `requirements.txt`, and move the maintainer's current equivalence cases into Taxa's own suite. Require exact suggested values and review text for shelfmark spacing, Roman-numeral dates, and uncertainties before rollout. The bundled catalogue alone is not evidence of identical wording to a private host catalogue. No Taxa code, deployment, or research data is changed by this package proposal.

## Model uncertainty language

`TranscriptionOptions(notes_language=None)` preserves the complete 0.1.0a3 prompt and cache identity byte for byte under identical model/schema/dependency/image settings. Accepted values are `None`, `"en"`, `"pt"`, and `"es"`; other values raise `ValueError` at construction.

A selected language appends one shared instruction to the profile prompt: write only `uncertainties` entries in that language, without translating or normalizing `literal_text`, `labels`, `name_as_written`, `handwritten_notes`, or other transcribed fields. The same rule applies to installed/external profiles. Base profile prompts and reading schemas are unchanged. This is a model instruction; offline tests validate the request contract, not live linguistic compliance or scientific accuracy.

The effective prompt is hashed in the cache configuration. Each explicit language has a different identity, including explicit English versus `None`. New folder JSON records `notes_language` in the envelope, outside the scientific `reading` object; old files are never rewritten. A different notes language blocks strict cache reuse before requests. Explicit historical acceptance still preserves the old JSON and its old language; it does not translate accepted readings or regenerate notes.

CLI `transcribe` and `batch` expose `--notes-language {en,pt,es}`. `--lang` independently controls report presentation and never sets model notes implicitly. Localizing a report does not alter its cache identity.

## Review language belongs to the host

Pass a callable `messages(message_id, context) -> str` that connects to the application's translation catalogue. It receives all presentation fragments: `source`, one canonical field name, and optionally `uncertainties`.

```python
from herbarium_labels.sennen_suggestions import DEFAULT_MESSAGES

def review_message(message_id, context):
    template = app_translation_catalogue[message_id]
    return template.format_map(context)

rows = suggestions(record, reading, filename,
                   field_map={"shelfmark": "cota"}, messages=review_message,
                   options=options_used_for_this_reading)
```

Use the same `TranscriptionOptions` for reading and suggestion rendering so the model label follows the actual selected model. An explicit `model_label` still overrides the display text. The host can supply its own catalogue or start from `load_messages("pt", kind="review")`. `DEFAULT_MESSAGES` documents the English templates and is immutable. A mapping of template overrides is also accepted; missing entries fall back to English. Use a complete mapping or a callable for fully localized review text.

Context contains `field`, `host_field`, `current`, `reading`, `filename`, `model`, and joined literal `uncertainties`. Text from the image/model is never translated. Render all returned values as plain text or escape them for the host UI; the library does not return trusted HTML.

## Client and request ownership

```python
from herbarium_labels import TranscriptionOptions, read_image

reading, usage = read_image(image_bytes, profile="sennen", client=existing_client,
                           options=TranscriptionOptions(model=selected_model, max_tokens=16000),
                           request_context=lambda: server_semaphore)
```

An injected client owns authentication, endpoint, HTTP timeout, retries, thread safety, and closure. The library never closes it. If the library creates a client, it reads `ANTHROPIC_API_KEY`, applies `timeout`/`max_retries`, and closes the client after use. Missing keys, invalid images, provider API errors, and incomplete readings raise `TranscriptionError`; incomplete readings carry known `input_tokens`/`output_tokens` on the exception. Programming errors from custom clients propagate.

There is no module-wide semaphore or implicit per-user quota. `request_context` is an optional factory returning a synchronous context manager, entered for the actual request and exited on failure too. The server handles tenant/user quotas. The retained `check_rate(user_id, limiter=callback)` helper requires an explicit callback; omitting it raises rather than silently disabling a previous rate policy. Existing servers must adapt before upgrading.

Options snapshot the model at construction. An explicit model overrides `TRANSCRIPTION_MODEL`. For injected clients, timeout/retry fields do not reconfigure that client. `workers` controls the file pipeline and does not create extra requests in `read_image`.

## Collection profiles

`get_profile("po-bryophytes")` and `get_profile("sennen")` supply a frozen contract: name, prompt, Pydantic schema, report columns, and `ImagePolicy`. Keep multiple-label evidence separate. A profile must provide `uncertainties` and either `literal_text` or `labels` (entries containing `origin`/`literal_text`). Optional `rotation_degrees` uses clockwise 0/90/180/270; absent rotation and notes default to 0/empty for reports.

```python
from herbarium_labels import TranscriptionProfile, read_image
from herbarium_labels.imaging import ImagePolicy

profile = TranscriptionProfile(
    name="my-collection", prompt=curated_prompt, schema=Reading,
    columns=(("filename", "Filename"), ("accession", "Accession")),
    images=ImagePolicy(long_edge=1568),
)
reading, usage = read_image(image_bytes, profile=profile, client=existing_client)
```

### Register profiles and expose them to the CLI

```python
from herbarium_labels import register_profile, list_profiles
register_profile(profile)
print(list_profiles())
```

Registration is local to the process. To expose a profile in fresh CLI processes, an installed Python package advertises a zero-argument profile factory:

```toml
[project.entry-points."herbarium_labels.profiles"]
my-collection = "my_herbarium.profiles:create_profile"
```

`create_profile()` returns a `TranscriptionProfile` named `my-collection`. Install that package in the same environment, then run:

```sh
herbarium-labels profiles
herbarium-labels batch --profile my-collection --images ./input --pdf
```

Listing discovers names without executing factories. Only the selected plugin is loaded. Duplicate names, invalid names, and a factory returning a different profile name fail explicitly. Factories are trusted installed Python code, not model output or files loaded from a transcription directory. Keep scientific prompts/schemas reviewed. The public group follows [the PyPA entry-point specification](https://packaging.python.org/en/latest/specifications/entry-points/).

## Folder API without argparse

```python
from herbarium_labels import transcribe_folder, create_report, batch_folder

totals = transcribe_folder(images, output, profile=profile, options=options,
                          client=existing_client, limit=10, sample=False,
                          request_context=lambda: server_semaphore)
reports = create_report(images, output, profile=profile, include_pdf=True,
                        messages=report_messages, prices=prices)
delivery = batch_folder(images, output, profile=profile, options=options,
                        client=existing_client, include_pdf=True, messages=report_messages)
print(totals.photos, totals.reused, totals.failures)
print(reports.workbook, reports.pdf)
print(delivery.archive, delivery.totals)
```

`limit` must be a positive integer or `None`. A supplied client remains caller-owned; ensure it supports concurrent calls, or select `workers=1`. Folder calls accept an optional request-context factory too. The library API raises exceptions for incomplete batches; the CLI converts them to exit statuses. Earlier namespace-based `pipeline.transcribe/report/batch` and bryophyte wrappers remain compatibility adapters. New code should use the path-based functions.

`batch_folder` defaults to `images/transcription/` and `images/transcriptions.zip`. With an explicit output path, the archive is adjacent to that folder and named `<output-name>.zip`. It returns `BatchResult(totals, reports, archive)`; report-only calls return `ReportFiles(workbook, pdf)`. A PDF-disabled report has `pdf=None`.

## Translate Excel and PDF presentation

`create_report` and `batch_folder` accept `messages`, a mapping or `(message_id, context) -> str` callback. Use the public loader for bundled templates:

```python
from herbarium_labels import load_messages, create_report
messages = load_messages("pt", kind="report", profile="sennen")
messages["column.filename"] = "Ficheiro do projeto"
reports = create_report(images, output, profile="sennen", messages=messages)
```

`load_messages(lang, *, kind="report", profile=None)` accepts `en`, `pt`, or `es`; returns a fresh dictionary; defaults report profiles to `po-bryophytes` and reviews to `sennen`. Review messages currently support only Sennen; other review profiles raise `ValueError`. External report profiles receive translated common presentation labels, translated filename headings, and their own profile-specific column names; hosts supply any additional translations.

CLI report/batch accept `--lang {en,pt,es}` and `--messages-json`; JSON entries override the selected catalogue key by key. Omitting both preserves existing English behavior. Invalid catalogue keys still fail report validation before batch requests. Keys:

- `sheet.literal`, `sheet.fields`: Excel sheet names.
- `column.filename`, `column.image`, `column.literal_text`, `column.handwritten_notes`, `column.uncertainties`, `column.reviewed`: literal-review headings and PDF labels.
- `field.<canonical_key>`: profile-specific Fields-sheet headings, including `field.filename`.
- `pdf.title`, `review.choices`: PDF document title and review choices.

The callback context includes `profile` and the English `default` template. A mapping may contain `{profile}` placeholders; a callback returns the final text. Resolve a complete map/callback for fully localized reports; missing mapping entries fall back to English. Sheet names are validated for Excel restrictions, length, and distinctness before paid batch calls. Text is resolved once per report/batch. Literal readings, uncertainty values, scientific field keys, output filenames, and original images are unchanged. PDF markup is escaped.

Bundled Portuguese uses European Portuguese. Spanish requires review by a native speaker with domain expertise ("requer revisão por falante nativo da área"). Every catalogue has the same keys and format markers as English. The English catalogue matches the preceding default templates exactly. Existing complete Portuguese custom mappings remain in `examples/synthetic/report-messages-po-pt.json` and `report-messages-sennen-pt.json`. Use the mapping matching the selected profile; unknown message keys are rejected.

## Continue an older reviewed folder

```sh
herbarium-labels batch --profile po-bryophytes --images ./input --accept-existing --pdf
```

If earlier JSON lives in `input/transcricao/json/`, keep that location explicitly:

```sh
herbarium-labels batch --profile po-bryophytes --images ./input \
  --output ./input/transcricao --accept-existing --pdf
```

The Python equivalent is `batch_folder(images, output=Path(images) / "transcricao", profile="po-bryophytes", accept_existing=True)`, with `Path` from `pathlib`. Default output remains `transcription/`; acceptance does not discover or rename directories. The explicit legacy output produces the adjacent archive `transcricao.zip`.

Python equivalent: `batch_folder(images, profile="po-bryophytes", accept_existing=True)`. This explicit decision permits valid earlier readings to remain alongside new photographs. The full selected batch is checked before saving acceptance or making requests. Only new photographs need transcription.

The library never rewrites the old JSON or claims it was generated with the new prompt/model/image pipeline. `.accepted-existing.json` stores the profile, original JSON SHA-256, current image SHA-256, acceptance time, and whether an old recorded image hash could be verified. Missing old hashes are marked as historically unverified: the maintainer is explicitly accepting the association with the current image, not proving which image was used earlier. Acceptance does not establish scientific correctness or human-review approval.

A recorded source-image mismatch, wrong profile/schema, malformed JSON, or invalid token counts cannot be bypassed. Once accepted, matching files resume without repeating the flag. If the reading is subsequently corrected, review it and explicitly accept again; previous acceptance is retained. A changed image remains blocked. Accepted readings remain historical imports when settings change; their original model/usage remain intact. Keep the ledger together with JSON and source images when backing up/moving a project. Reports are regenerated from JSON; this option does not import edits made only in Excel. No migration of real collection folders is performed by this patch.

## Supply prices and align request defaults

```python
from herbarium_labels import TokenPrices, TranscriptionOptions

prices = TokenPrices(input_per_million=input_rate, output_per_million=output_rate,
                     model=selected_model)
options = TranscriptionOptions(model=selected_model, prices=prices)
```

Explicit prices take precedence over environment rates and may be zero. Prices are USD per million tokens; there is no built-in tariff table. A model-bound rate returns unknown for other models, useful when a report includes accepted historical readings. Omitting the model applies the caller's rates to every model in the report. Environment variables remain a compatibility fallback. CLI flags are `--price-in`, `--price-out`, and optional `--price-model`; both rates must be supplied together.

Price sources are resolved as follows:

| API | Priority, highest first |
| --- | --- |
| `transcribe_folder` | `options.prices`, then environment |
| `create_report` | `prices=`, then environment |
| `batch_folder` | `prices=`, then `options.prices`, then environment |

A non-`None` batch override applies to both transcription and report estimates. The frozen `TranscriptionOptions` supplied by the caller is not modified. `TokenPrices(0, 0)` is an explicit zero-rate override. Prefer defining rates once in options for a batch; pass `prices=` when deliberately overriding the entire delivery. For separate transcription/report calls, pass `options.prices` to `create_report(..., prices=options.prices)`.

The default `max_retries` is **2** in `TranscriptionOptions`, CLI, and compatibility wrappers. Injected clients retain their own timeout/retry policies. Sennen's legacy `MODEL`/`MODEL_LABEL` attributes are resolved when accessed; new integrations pass the reading's options to `suggestions(..., options=options)`.

## Dependency compatibility

Metadata permits Pillow `>=11.3,<14`, covering Taxa's 11.3.0. The primary hashed lock keeps Pillow 13. A separate Linux/Python 3.12 compatibility check exercises Pillow 11.3.0 with synthetic inputs. This is functional compatibility, not evidence of security equivalence: later Pillow releases fix decoder vulnerabilities. Do not downgrade a current installation merely to match the minimum. Hosts remain responsible for auditing their selected dependency graph.

The separately hashed `requirements-compat.lock` selects Pillow 11.3 for functional compatibility checks; `requirements.lock` remains the recommended current environment.
