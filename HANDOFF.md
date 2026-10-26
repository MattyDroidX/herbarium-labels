# Development handoff

Updated: 2026-10-26. Published baseline: `0.1.0a3`. Maintainer-applied release candidate: `0.1.0a4`; isolated Portuguese-wording follow-up.

## Maintainer control

Only the maintainer applies changes, commits, pushes, tags, or publishes unless explicitly delegated. The maintainer has applied the base 0.1.0a4 patch. This incremental Portuguese-wording follow-up is prepared and tested in isolation; it does not alter that working tree. No private Taxa code, deployment, original collection data, or paid API request is part of this task.

## Published baseline and evidence

The maintainer downloaded the 0.1.0a3 TestPyPI wheel, confirmed its version/import in a clean environment, passed 84 tests without skips, and verified the synthetic Excel/PDF/ZIP demo with all flags true. They then triggered PyPI publication and supplied successful workflow run 40387409728. This updates the earlier preparation-only records; a fresh production install of 0.1.0a3 was not independently executed in this candidate task.

Earlier research use/acceptance and the maintainer's independent Taxa equivalence checks remain documented in docs/EVIDENCE.md. Preserve their stated scope; ordinary synthetic tests do not establish live transcription accuracy.

## Candidate implementation

- Optional `TranscriptionOptions.notes_language`: `None`, `en`, `pt`, or `es`. One shared prompt suffix is used for every collection profile, including extensions. `None` retains the exact 0.1.0a3 prompt/cache identity; explicit language selections change identity. New JSON stores the selection outside the scientific reading object. Existing JSON and literal fields are preserved.
- Bundled report and Sennen-review catalogues, public `load_messages`, report/batch `--lang`, transcribe/batch `--notes-language`, and key-by-key CLI JSON overrides. English defaults match the preceding templates. Portuguese is European Portuguese; Spanish requires native domain review.
- Locale package-data declarations and required-resource checks for wheel/source archives. No dependency or profile prompt/schema/image-policy changes.
- Public API and one-preceding-alpha notice policy in README. Consuming applications must pin an exact alpha. Taxa adoption is a separate release after 0.1.0a4 is published/verified, with the maintainer's exact equivalence cases incorporated into Taxa's suite before replacing app/transcription.py.
- Earlier release-polish items were already present: explicit historical `transcricao/` example, `--accept-existing` alternative in CHANGELOG, and batch price precedence (`prices` > `options.prices` > environment) for both stages.

## Verification

105 tests passed against source and the actual installed wheel on Linux/Python 3.12.14 with Pillow 13.0.0 and 11.3.0; no tests were skipped. The compatibility environment uses requirements-compat.lock, with the locally cached Pillow wheel hash verified against that lock. Build-from-sdist, strict Twine metadata, distribution contents/licenses/credential-pattern checks, dependency consistency, workflow SHA policy, public-file hashes, and patch applicability passed. Six synthetic localized reports were generated; Portuguese/Spanish PDFs for both profiles were rendered and inspected. See VALIDATION.md for commands and limits.

## Next steps

The maintainer reviews/applies the incremental wording patch, reruns checks, and confirms remote CI before publication. Follow docs/PUBLISHING.md for a matching v0.1.0a4 tag, TestPyPI wheel validation, and then PyPI. Do not move the published 0.1.0a3 tag. No candidate publication or native Windows run is claimed here.

Authorized live evaluation, real HEIF examples, long/Unicode report coverage, curated handwriting sources/retrieval/attribution, and the broader iterative roadmap remain separate work. Historical acceptance is explicit and preserves original JSON; it is not scientific approval and does not import Excel-only edits.

## Portuguese wording follow-up

The maintainer reports 104 passing tests on the applied candidate and exact prompt/cache equivalence to the published 0.1.0a3 in both profiles with notes_language omitted. Their Taxa comparison found matching fields/values/uncertainties but four wording differences. Two catalogue entries now retain the supplied legacy phrases: source photograph/confirmation and the exsiccata_number caption/Sennen reading phrase. A new exact rendered-review regression failed on the earlier catalogue and passes after alignment. The assistant did not execute the private Taxa suite or inspect all 549 existing reviews. No prompt, cache, reading, comparison rule, API, or version change is introduced.
