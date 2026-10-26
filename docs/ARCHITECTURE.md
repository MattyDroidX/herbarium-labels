# Architecture overview

This describes the shared architecture published in 0.1.0a3 and extended by the 0.1.0a4 candidate. [Open the SVG](diagrams/architecture.svg) or edit the [Mermaid source](diagrams/architecture.mmd).

![Architecture overview](diagrams/architecture.svg)

```mermaid
flowchart LR
    Input["Original images: unchanged"] --> Imaging["imaging.py: EXIF / RGB / thumbnail; no upscaling"]
    Profiles["profiles.py: built-ins / registry / installed entry points"] --> Imaging
    Profiles --> Provider["provider.py: schema + prompt + explicit options/client"]
    Imaging --> Provider
    Host["Host: key/client, optional request context"] --> Provider
    Provider --> Reading["Validated reading + usage; separate labels preserved"]
    Input --> Cache["cache.py: image/config identity + output lock"]
    Profiles --> Cache
    Cache --> Pipeline["pipeline.py: preflight / request / atomic JSON"]
    Provider --> Pipeline
    Pipeline --> Report["Shared offline Excel / PDF / ZIP"]
    Reading --> Suggestions["suggestions.py: canonical field comparisons"]
    Mapping["Host field map + review/report translations"] --> Suggestions
    Suggestions --> Review["Host human review; no automatic database edits"]
    Report --> Review
    Catalog["catalog.py + library/: independent documentary validation"]
```

Profiles select the scientific prompt, schema, image views, and report columns. Both built-ins share image preparation, Claude requests, cache/persistence, and offline delivery. Sennen retains the full sheet and lower crop without upscaling. Registered and installed entry-point profiles use the same contract from Python and CLI. Folder APIs receive paths and ordinary keyword parameters; CLI adapters delegate to them.

The host owns authentication, optional request concurrency/user limits, field mappings, review-language rendering, and database decisions. An injected client remains caller-owned. Catalogue validation stays independent and does not identify writers or inject examples into prompts.

Cache checks precede requests. Strict conflicts stop; explicit historical acceptance records hashes separately while preserving original JSON; incomplete readings are not saved. The CLI exits nonzero for transcription failures. Batch requires complete input coverage before reports/ZIP. Standalone reports require no competing writer. See [integration](INTEGRATION.md), [testing](TESTING.md), and the remaining [roadmap](https://github.com/MattyDroidX/herbarium-labels/blob/main/PLAN.md).

The host can supply report translations as well as review-suggestion messages. Explicit acceptance stores historical provenance separately from new cache identity; it does not establish scientific approval. See [continuing older folders](INTEGRATION.md#continue-an-older-reviewed-folder).

In 0.1.0a4, `prompts.py` appends the optional uncertainty-language instruction for every profile. The provider and cache use that same effective prompt; an omitted language retains the preceding identity. `messages.py` loads bundled report/review templates independently, so presentation language does not change model requests or cached literal evidence.
