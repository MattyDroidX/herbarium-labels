# Workflow diagram

[Open the standalone SVG](diagrams/workflow.svg) or edit the [Mermaid source](diagrams/workflow.mmd). This is the implemented delivery workflow, including failure stops; it does not imply an automated review application.

![Workflow overview](diagrams/workflow.svg)

```mermaid
flowchart TD
    Start["Choose command"] --> Command{"demo / report / transcribe / batch?"}
    Command -- demo --> Fixture["Create synthetic images; use simulated provider"]
    Fixture --> Validate["Validate images and duplicate filename stems"]
    Command -- "transcribe or batch" --> Validate
    Command -- report --> Load["Read stored English or legacy JSON; no API"]
    Validate --> Lock["Acquire exclusive output lock"]
    Lock --> Cache{"Existing selected JSON matches image/config?"}
    Cache -- incompatible --> Stop["Stop; preserve previous work and choose fresh output"]
    Cache -- reusable --> Reuse["Reuse without provider request"]
    Cache -- missing --> Request["Request structured reading; bounded SDK retries"]
    Request --> Complete{"Complete and valid response?"}
    Complete -- no --> Failure["Record failure in summary; do not persist incomplete reading"]
    Complete -- yes --> Save["Save English JSON atomically"]
    Save --> Mode{"Batch delivery?"}
    Reuse --> Mode
    Failure --> Mode
    Mode -- no --> Done["Return transcription summary; inspect failures"]
    Mode -- yes --> All{"Every input has a reading?"}
    All -- no --> Abort["Stop incomplete batch before reports/ZIP"]
    All -- yes --> Reports["Build English Excel and optional PDF"]
    Load --> Reports
    Reports --> Archive{"Batch?"}
    Archive -- yes --> ZIP["Create temporary ZIP; check integrity; replace archive"]
    Archive -- no --> Review["Inspect original, literal text, uncertainty, and links"]
    ZIP --> Review
    Review --> Human["Human decision; no automatic approval/import"]
```

- **`transcribe`:** validate selected inputs/cache, request missing readings, validate/persist complete results, and return usage/failure totals. Inspect the printed failures: this command currently does not guarantee a nonzero exit status for every per-image provider failure.
- **`report`:** read existing English/legacy JSON, validate image identity when recorded, and generate English reports without a provider call. Standalone reports do not acquire the transcription lock; avoid concurrent writers.
- **`batch`:** keep the output lock throughout transcription and delivery. Require readings for all inputs before reports/ZIP. Preserve an earlier archive if the new ZIP integrity check fails.
- **`demo`:** create a fresh synthetic input directory and mock provider, exercise batch/resume plus the Sennen Python route, and verify the generated files without network or paid usage.
- **Sennen Python route:** return `SheetReading` and usage for the full sheet plus crop. Its semaphore bounds concurrent calls. The host must explicitly invoke any per-user rate helper and perform human approval; these are not automatically provided by the CLI.

Existing JSON is not replaced just because a new model/schema/prompt is requested. Incompatible cache stops the run and asks for a new output directory. Failed/incomplete responses are not promoted to valid readings. A lost paid response before persistence may still require a repeated request.

The final human step is inspection of originals, literal text, field interpretation, uncertainty, and links. An Excel checkbox does not itself register an immutable review event or approve handwriting attribution. See [TESTING.md](TESTING.md) for reproducible checks and [MIGRATION.md](MIGRATION.md) for interface changes.
