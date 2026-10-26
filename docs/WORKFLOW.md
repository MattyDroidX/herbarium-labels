# Workflow overview

This describes the proposed 0.1.0a3 source. The published 0.1.0a2 uses independent readers. [Open the SVG](diagrams/workflow.svg) or edit the [Mermaid source](diagrams/workflow.mmd).

![Workflow overview](diagrams/workflow.svg)

```mermaid
flowchart TD
    Start["Choose profile and command"] --> Mode{"demo / report / transcribe / batch?"}
    Mode -- demo --> Demo["Synthetic images and simulated provider"]
    Mode -- report --> Stored["Load JSON with matching profile; no API"]
    Mode -- "transcribe / batch" --> Lock["Validate inputs and acquire output lock"]
    Demo --> Lock
    Lock --> Cache{"Strict match or explicit historical acceptance?"}
    Cache -- conflict --> Stop["Stop; preserve originals, JSON and human corrections"]
    Cache -- "explicit acceptance" --> Accepted["Separate hash ledger; original JSON unchanged"]
    Accepted --> Reuse
    Cache -- reusable --> Reuse["Reuse without request"]
    Cache -- missing --> Prepare["Shared image preparation; Sennen adds lower crop"]
    Prepare --> Request["Structured request with explicit options/client"]
    Request --> Valid{"Complete and valid reading?"}
    Valid -- no --> Failure["Aggregate known usage/failure; no incomplete JSON"]
    Valid -- yes --> Save["Atomic profile-tagged JSON"]
    Save --> Delivery{"Batch with every input complete?"}
    Reuse --> Delivery
    Failure --> Delivery
    Delivery -- incomplete --> Stop
    Delivery -- transcribe --> Summary["Return totals; CLI failures exit 1"]
    Delivery -- complete --> Reports["Shared Excel and optional PDF; checked ZIP"]
    Stored --> Reports
    Reports --> Human["Human review outside the library"]
```

Profiles select the scientific prompt, schema, image views, and report columns. Both built-ins share image preparation, Claude requests, cache/persistence, and offline delivery. Sennen retains the full sheet and lower crop without upscaling. Registered and installed entry-point profiles use the same contract from Python and CLI. Folder APIs receive paths and ordinary keyword parameters; CLI adapters delegate to them.

The host owns authentication, optional request concurrency/user limits, field mappings, review-language rendering, and database decisions. An injected client remains caller-owned. Catalogue validation stays independent and does not identify writers or inject examples into prompts.

Cache checks precede requests. Strict conflicts stop; explicit historical acceptance records hashes separately while preserving original JSON; incomplete readings are not saved. The CLI exits nonzero for transcription failures. Batch requires complete input coverage before reports/ZIP. Standalone reports require no competing writer. See [integration](INTEGRATION.md), [testing](TESTING.md), and the remaining [roadmap](https://github.com/MattyDroidX/herbarium-labels/blob/main/PLAN.md).

The host can supply report translations as well as review-suggestion messages. Explicit acceptance stores historical provenance separately from new cache identity; it does not establish scientific approval. See [continuing older folders](INTEGRATION.md#continue-an-older-reviewed-folder).
