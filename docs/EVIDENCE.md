# Evidence of quality and practical use

The project maintainer reports research use and acceptance by researchers. This is relevant evidence of quality and usefulness in those contexts. Citations, names, and testimonials require verification/permission; no publication has been invented.

Internal TSennen/Taxa records from October 2026 report:

- 311 original full-sheet photographs: reported agreement of 100% for general accession number in matched readings, 92% for exsiccata number, 86% for date, 84% for name, and 79% for shelfmark.
- Name differences include literal versus standardized names. Formal reporting requires per-field denominators, a protocol, and treatment of unmatched readings. These figures are neither character error rate (CER) nor overall accuracy.
- One recorded local execution: approximately 11 seconds, 5,457 input tokens, and 1,904 output tokens.
- A 549-image bryophyte batch with reported cost/time of USD 0.91/18 minutes; another 300-photo batch at approximately USD 0.47.
- Pending suggestions required a human decision before editing in the host application.

These are historical records, not experiments repeated during extraction or release preparation. Private data are not redistributed, and the same costs are not guaranteed.

A delivered workbook was inspected read-only: 549 records on each of two sheets, 549 embedded images, literal text in every record, 306 records with explicit uncertainties, no formula cells, and 549 existing local links per sheet. Samples from the beginning, middle, and end were read. This was not a complete paleographic review; 306 uncertainties do not mean 306 confirmed errors. The original workbook was neither modified nor packaged.

The extracted modules and tests were inspected. Sennen sends the full sheet and a crop and returns separate labels. Offline tests use synthetic images and simulated providers, including mock HTTP transport through the installed SDK. See [VALIDATION.md](https://github.com/MattyDroidX/herbarium-labels/blob/main/VALIDATION.md) for current checks and limitations.

Docker/localhost were inaccessible in the original extraction session. This limitation is historical, not a current defect claim. No paid API call or modification of the research environment has been made during this preparation.

## Maintainer-reported Taxa equivalence — 2026-10-26

After applying the reuse proposal, the maintainer ran the 61-test suite and a separate equivalence check using Taxa's Pillow 11.3, `field_map={"shelfmark": "cota"}`, and Portuguese review-message templates. They reported exactly matching suggestions against the current `app/transcription.py` in three cases: shelfmark spacing, a date in Roman numerals, and reading uncertainties.

This is evidence for that host integration and those three cases. The private test fixtures/application were not supplied or independently executed in this session, and the result is not generalized to every field, collection, or live model. The follow-up retains the suggestion comparison rules and adds synthetic regressions for the reported scenarios.

## Independent maintainer release verification — 2026-10-26

The maintainer subsequently reported independent verification of all six integration contracts: plain path-based Python calls and old adapters, an external `meu-herbario` package discovered only through entry points in a separate environment, duplicate `sennen` rejection, Portuguese report presentation, unchanged Taxa suggestion results/imports with options-derived model labels, and explicit prices/retries/Excel text safety.

On a copy of six photographs from a real research batch, five had old JSON without image hashes. With a simulated counting client, strict mode stopped with zero requests; explicit acceptance requested only the new photograph, preserved all five JSON files byte for byte, and marked historical associations unverified. The next run reused all six with no requests. The originals were untouched and no paid requests were made. These private photographs/results are not included in the repository.

The supplied-rate cost calculation was USD 0.0825, not a provider charge. The maintainer's 83-test suite passed on source with Pillow 13 and the installed package with Pillow 11.3; the latter initially skipped one SDK test because the optional `claude` extra was missing. That test then passed with Taxa's Anthropic 1.17/Pillow 11.3 interpreter. The assistant did not independently run the private application or those six-image fixtures; its release-polish suite uses synthetic data and includes one additional batch-price-precedence regression.
