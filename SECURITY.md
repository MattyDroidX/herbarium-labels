# Security

Never put credentials or private research data in commits, logs, issues, or distribution packages. API keys come from the environment; offline reports do not require a key. Transcription sends images to Anthropic, so verify permission for both target images and any future examples.

The library is not an authentication server. Host applications implement authorization, limits, and human review. Treat images and model responses as untrusted data. Keep image paths within the allowed input directory, escape report markup, and store label content as Excel text rather than executable formulas.

Before release, review the public-file allowlist, history, dependency locks, dependency advisories, and secrets in both the source tree and built distributions. `tools/check_dist.py` performs structural checks and a limited pattern scan; it is not an external audit or a complete secret detector. No external security audit has been performed.

A private vulnerability-reporting channel has not yet been verified for the selected MattyDroidX/herbarium-labels repository. Enable GitHub Private Vulnerability Reporting once the repository exists and update this document with the actual route. Do not post sensitive details in public issues while a private channel is unavailable. No contact address is invented here.
