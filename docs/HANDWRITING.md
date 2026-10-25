# Handwriting catalogue

Share documented handwriting samples for reading and comparison while preserving uncertainty.

1. **Person:** stable ID, names/aliases, roles, and affiliations with sources. Jesuit, curator, and researcher are historical information.
2. **Hand:** an observed writing style with its own ID; the writer may be unknown. A label may contain several hands, and a person may have variants.
3. **Sample:** image/crop, hash, provenance, collection location, documented date, human transcription, and rights.
4. **Attribution:** hand → person, with evidence, sources, reviewer, and candidate/confirmed/contested status. Current schema values are `candidate`, `confirmed`, and `contested`; legacy Portuguese values remain accepted when reading older records.

References to Brotéria and other catalogues require verifiable edition, volume, pages, and identifier. A contributor list identifies people but does not prove who wrote a particular label. Signed letters and handwriting catalogues can provide additional evidence, subject to their own rights.

Confirmed attribution requires a source, sample, justification, and reviewer. Structural validation does not replace historical analysis. Model confidence is not proof.

Sampaio, Sennen, Zimmermann, and Luisier profiles are drafts (`draft`). No historical characteristics, aliases, or attributions have been invented. See `library/catalog.json`; it currently contains no curated samples or confirmed attributions.

Automatic recognition is future work. Include unknown writers and similar hands, prevent leakage between documents/specimens, and evaluate transcription and attribution separately.
