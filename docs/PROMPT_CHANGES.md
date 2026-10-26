# English prompt translation and evaluation limits

The original extraction preserved its scientific prompts byte-for-byte at the Python-string level. At the maintainer's request for English code/interfaces, the published `0.1.0a2` translates the instruction language and field references. This is an intentional prompt change; the earlier unchanged-prompt check does not apply to this revision.

## What changes

- Instructions and response-field references are English and use the new reading models.
- Bryophyte editorial markers `[Outra: ...]` and `[manuscrito: ...]` become `[Other: ...]` and `[handwritten: ...]` in new proposals.
- Sennen's generic origin marker is `other`; proper names `Sennen` and `Porto` remain.
- The instructions explicitly tell the model to retain the source language rather than translate label text.

Institution names, specimen examples, printed field labels, and source quotations remain in their original language because they are evidence, not interface text. Existing literal transcriptions are never edited to replace their earlier editorial markers.

## Scientific safeguards carried forward

- Copy visible text without correcting spelling, names, or abbreviations, and never invent missing information.
- Preserve source lines and label boundaries; do not merge several labels.
- Absent/illegible fields remain empty; uncertainty is reported separately.
- Keep collector, determiner, and taxonomic author distinct.
- Preserve ambiguous dates and abstain from `date_iso` when the order is unclear; PO/LISU-specific date examples remain collection-specific.
- Sennen still receives both the full sheet and lower-region crop; labels remain separate.
- Draft catalogue profiles are not injected into prompts, and no writer is identified automatically.

## Reproducible prompt identifiers

SHA-256 below is computed over each UTF-8 Python prompt string, not over the source file:

| Module | Extracted baseline prompt SHA-256 | English proposal prompt SHA-256 |
| --- | --- | --- |
| `bryophytes.py` | `dc0f36146a5bc2e9b0ec2310871c4c3c5cd9800454bf1d0d8ed147d56caf69bd` | `9f887603e7bd9c648ff116f63a9ec73f07cf6ed3a8a4f052df5cebb83c5a413c` |
| `sennen.py` | `6e226e194ae2519665cf39e5abd9d9c03c7844fe9ac7e2776ca9295531a547f7` | `6d864d7dc646eac86311a248e6f5c5089daee7a8c60764148563ed4fb5e949cf` |

The cache includes the prompt content, model, schema, transformations, SDK, and codecs. A translated prompt therefore cannot silently reuse a cache entry from the original configuration.

## What has and has not been demonstrated

Offline tests exercise the English schemas, exact request prompt payloads, response parsing, preserved legacy literals, separate labels, and report safety using simulated providers. They do not establish equivalent reading accuracy, date interpretation, or review time on real handwriting.

The maintainer's reported research acceptance remains evidence for the original workflows in their use contexts. Do not transfer those results automatically to this translation. Before claiming equivalent scientific performance, compare original and translated prompts on the same authorized images/model, review the outputs, and report methods, sample sizes, per-field denominators, uncertainty, cost, and limitations. A live comparison requires image permission and an explicit budget; none was performed in this task.

## Proposed 0.1.0a3 image policy

PO/LISU prompt and both Pydantic reading schemas are unchanged. Sennen retains the same instructions except that "second is an enlarged crop" becomes "second is a crop", matching the no-upscaling image policy. Full-sheet and lower-crop input remain distinct views. This transformation change has a new cache identity. Synthetic tests verify structure and fidelity; a permitted live comparison is still required to evaluate scientific effects.
