# Contributing

## Set up and test

Use Python 3.11+ and a virtual environment. Follow the installation commands in [README.md](README.md). Run `python -m unittest discover -s tests -v`; if the package is not installed, set `PYTHONPATH=src`. Tests must use synthetic data and simulated providers. Live calls require image permissions and an agreed budget.

Before release-related work, install `requirements-dev.lock` with `--require-hashes` and follow [the release guide](docs/PUBLISHING.md). No formatter, linter, or numerical coverage threshold is currently enforced. Use four-space indentation, `snake_case` functions/modules, `PascalCase` models, and focused regression tests for behavior changes.

## Propose a change

Explain the use case, current behavior, and expected result. Keep changes small. Use the English commands/models and preserve legacy JSON reading, source-language evidence, and full-sheet Sennen processing. Consult docs/MIGRATION.md before changing a public interface. Changes to prompts or schemas require justification, a changelog entry, and evaluation of their effects. Read [AGENTS.md](https://github.com/MattyDroidX/herbarium-labels/blob/main/AGENTS.md) for repository-specific invariants.

Use concise imperative commit subjects, such as `Validate cache identity before transcription`. This is guidance for new commits: the current history has no established commit-message convention.

A pull request should describe the behavior change, relevant issue if one exists, tests run and their results, and known limitations. Include before/after report samples when layout changes; use synthetic data and document visual inspection. Update `CHANGELOG.md`, `VALIDATION.md`, and `HANDOFF.md` where relevant.

## Scientific and documentary contributions

Write documentation in English. Preserve original-language names, quotations, and literal transcriptions. Public identifiers, commands, messages, and documentation are English. Separate interpretation from literal evidence. A profile requires sources; a transcription review does not establish handwriting authorship. Draft profiles stay drafts until curated.

Use only synthetic or authorized data. Do not submit credentials, private research results, or restricted images. The MIT code license does not grant image/data rights. When reporting quality, include versions, datasets, denominators, methods, and limitations; see [research evidence](docs/EVIDENCE.md).
