# Synthetic demonstration assets

These public fixtures were generated for this project using synthetic text and simulated provider responses. They contain no collection image, real specimen record, private research output, or handwriting attribution. The generated demonstration assets are supplied under the project's MIT license; this does not license external collection material.

You can inspect every file directly in this repository; no temporary-directory access or API key is needed.

- [Synthetic input image](input/synthetic.jpg): clearly marked as a synthetic label.
- [Rendered PDF preview](review-preview.png): open this image to inspect English headings and layout.
- [Review PDF](output/review.pdf): the original one-page synthetic report.
- [Excel workbook](output/transcriptions.xlsx): English sheets and embedded image; keep its adjacent `images/` folder so the relative link works.
- [Structured reading](output/json/synthetic.json): English schema/keys produced by version 0.1.0a2.
- [Separate sheet labels](sheet_reading.json): two simulated labels, kept separate.
- [Verification results](verification.json): `all_passed` is `true`; all usage/call counts are simulated, not billed provider usage.

The workbook contains formula-like literal text starting with `=` stored as text and collection number `001`. This is intentional safety-test input. The literal values come from known fixtures, not an OCR experiment.

These files were generated and verified with the published 0.1.0a2 English API. See the [testing guide](../../docs/TESTING.md), [architecture](../../docs/ARCHITECTURE.md), and [workflow](../../docs/WORKFLOW.md).

To generate a fresh demonstration with the installed version, use a new output directory:

```sh
python -m herbarium_labels demo --output ./demo-output --pdf
```

Do not replace these synthetic fixtures with private herbarium images. An offline mock does not establish paleographic accuracy or the quality of translated prompts on real collections.

## Portuguese report presentation (0.1.0a3 follow-up)

The proposed report-localization API generated a second delivery from the same synthetic JSON, without a provider request or changes to literal evidence:

- [Portuguese report preview](portuguese/review-preview.png)
- [Portuguese review PDF](portuguese/output/review.pdf)
- [Portuguese Excel workbook](portuguese/output/transcriptions.xlsx), with its adjacent image copies
- [PO/LISU report messages](report-messages-po-pt.json)
- [Sennen report messages](report-messages-sennen-pt.json)

Only headings, sheet names, and review presentation are translated. These are synthetic examples, not Cristiana's collection data or a quality evaluation. Use the profile-specific JSON map with CLI `--messages-json`, or pass a mapping/callback to the Python folder APIs.
