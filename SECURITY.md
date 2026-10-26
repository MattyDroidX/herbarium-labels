# Security

Never put credentials or private research data in commits, logs, issues, or distribution packages. API keys come from the environment; offline reports do not require a key. Transcription sends images to Anthropic, so verify permission for both target images and any future examples.

The library is not an authentication server. Host applications implement authorization, limits, and human review. Treat images and model responses as untrusted data. Keep image paths within the allowed input directory, escape report markup, and store label content as Excel text rather than executable formulas.

Before release, review the public-file allowlist, history, dependency locks, dependency advisories, and secrets in both the source tree and built distributions. `tools/check_dist.py` performs structural checks and a limited pattern scan; it is not an external audit or a complete secret detector. No external security audit has been performed.

Use the repository's private vulnerability-reporting channel when enabled. Do not post credentials or sensitive research data in public issues. Maintainers should keep the reporting route visible in the repository Security tab.

The primary hashed environment uses Pillow 13. The lower Pillow 11.3 compatibility floor supports existing hosts; it does not imply that old image decoders have current security fixes. Keep application dependencies audited and current. The separate compatibility lock/job exercises synthetic inputs only.
