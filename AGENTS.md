# Repository Guidelines

These instructions apply throughout the repository. Explicit user requests take precedence over implementation guidance here. Documentation must be written in English; use English code and interfaces. Preserve literal evidence in its source language. English prompt translations and API changes are documented in `docs/PROMPT_CHANGES.md` and `docs/MIGRATION.md`; their live scientific effects remain to be evaluated.

## Context and session startup

- Read `README.md`, `HANDOFF.md`, `VALIDATION.md`, and section 25 of `PLAN.md` before changing code.
- Existing workflows have been used in research and accepted by researchers. Preserve that evidence and its limits; do not describe the project as unvalidated.
- Build a useful open library that complements Hespi. Its value does not depend on outperforming another project.
- Treat `PLAN.md` as an iterative roadmap. Distinguish implemented, proposed, and tested features.

## Code and compatibility

- Python 3.11+; source in `src/herbarium_labels/`, tests in `tests/`, catalogue in `library/`.
- The English API uses `bryophytes.py` with `transcribe`, `report`, `batch`, and offline `demo`. Preserve legacy JSON reading, original literal text, Excel/PDF/ZIP integrity, and the migration rules in `docs/MIGRATION.md`.
- `sennen.py` processes a full sheet and lower crop with multiple labels. Do not replace that capability with a cropped-input assumption.
- `catalog.py` validates people, sources, samples, and attributions; it does not identify writers or inject examples into prompts.
- Keep changes small, documented, and testable. Preserve scientific safeguards. Further prompt/contract changes require justification and validation; offline tests do not establish paleographic equivalence.
- Prioritize content/configuration caching and per-task aggregation before increasing parallelism. Preserve originals and human corrections.

## Scientific fidelity and handwriting

- Preserve literal spelling, lines, and uncertainties. Normalization and interpretation are separate layers.
- Do not fill missing data or confuse institution, collector, determiner, taxonomic author, and writer.
- Separate person, observed hand, sample, and attribution. A label can contain several hands.
- Jesuit, curator, and researcher are documentary metadata, not visual handwriting classes.
- Keep Sampaio, Sennen, Zimmermann, and Luisier profiles as drafts until curated. Do not invent aliases, biographies, examples, or attributions.
- Brotéria and similar references require verifiable editions/locations. A list of people does not establish label authorship.
- Confirmation requires a sample, source, evidence, and reviewer. Automatic similarity is not confirmed authorship.

## Security and data

- Never commit `.env`, keys, uploads, backups, databases, or private results. Read API keys from the environment and never log their values.
- The code's MIT license does not license images or collections. Check local, API, and redistribution permissions separately.
- Work in this library. TSennen/Taxa references are read-only context; do not change research deployments, live databases, or containers without explicit scope.
- Ordinary tests must be offline and synthetic. Paid calls require authorized images and an agreed budget.
- Never execute model output as code, a formula, or a path. Preserve escaping, path validation, and Excel text cells.

## Verification and publication

- Run `python -m unittest discover -s tests -v` after relevant changes; use `PYTHONPATH=src` when the package is not installed.
- Check catalogue/schema consistency after changes. Visually inspect reports after layout changes. Use a simulated provider before live integration.
- Record results/limits in `VALIDATION.md`, changes in `CHANGELOG.md`, and concrete next steps in `HANDOFF.md`.
- Preserve `LICENSE` and `NOTICE.md`. Before release, review dependency locks, secrets, distribution contents, and data permissions.
- Follow `docs/PUBLISHING.md` and existing publication authorization. Resolve only genuinely missing details; do not invent an account, repository URL, authors, or CI results.

## Maintainer control

Only the maintainer may apply repository changes, commit, or push unless they explicitly authorize that action. Do not interpret a request for advice or preparation as permission to apply changes. Prepare remaining proposals as patches in an isolated temporary directory and test there; leave the working tree and Git state unchanged. SSH is unnecessary when the maintainer handles remote operations.

Deliver requested review images and reports inside the repository under `examples/synthetic/` and `docs/diagrams/`; temporary-directory links alone are insufficient. Synthetic examples must be identified as such, with no private collection material.
