# Release 0.1.0a3

This guide prepares and publishes `herbarium-labels==0.1.0a3`. Version 0.1.0a2 is the preceding published alpha. Publication remains a maintainer action; the assistant does not apply patches, commit, push, tag, or upload unless explicitly authorized.

The release uses the existing `publish.yml` Trusted Publishers and GitHub environments `testpypi` and `pypi`. Their repository is `MattyDroidX/herbarium-labels`; workflow filename is `publish.yml`. The workflow requires a tag matching the package version. No API-token secret or Anthropic key is required for publication or ordinary offline tests.

Commands below use Linux/macOS/WSL paths. On native Windows, replace virtual-environment `bin/python` with `Scripts/python.exe`. Run commands from the repository root.

## 1. Apply, review, and verify the release tree

Apply the reviewed incremental patch yourself, then verify the tree. The full runtime lock installs optional SDK/report dependencies, so the SDK contract test can run too.

```sh
python -m pip install --require-hashes -r requirements.lock
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
python -m pip check
python -m unittest discover -s tests -v
python tools/check_workflows.py
python -m build --no-isolation --outdir dist/0.1.0a3
python -m twine check --strict dist/0.1.0a3/*
python tools/check_dist.py dist/0.1.0a3/*
```

The expected suite contains 84 tests with the required extras installed. Read any skip reasons. Use the versioned artifact folder above so older local releases are not included accidentally. Inspect metadata/licenses, dependency locks, allowed contents, synthetic examples, and source hashes; preserve LICENSE and NOTICE.md. `check_dist.py` is a limited structural/credential-pattern check, not a complete security audit. Dependency audits can be run with `python -m pip_audit -r requirements.lock --require-hashes --disable-pip` and the equivalent development lock command; inspect actual findings.

Before tagging, ensure README documents the intended version and distinguishes the published package from source-only features. Do not claim remote CI results or uploads until confirmed. The public-file manifest excludes itself and generated/private files and must match the reviewed tree.

## 2. Commit and push the reviewed source

Review the changed files before staging. These commands stage the tracked release changes/deletions plus the known public additions; ignored environments and local datasets remain outside the commit.

```sh
git status --short
git add -u
git add -- .github docs examples/synthetic src tests tools requirements-compat.lock
git --no-pager diff --cached --stat
git diff --cached --check
git commit
git push origin main
```

Suggested subject: `feat: make transcription workflows reusable across host applications`.

Inspect the actual CI run for this commit before continuing. Disable the GitHub CLI pager to avoid the suspended-pager behavior previously observed:

```sh
export GH_PAGER=cat
gh run list --workflow tests.yml --branch main --limit 5
```

Use `gh run watch RUN_ID --exit-status` with the displayed run ID, or inspect the run in GitHub Actions. Continue only after the matching commit's required jobs succeed. No successful remote matrix run is inferred from local tests.

## 3. Create the new release tag

```sh
git tag -a v0.1.0a3 -m "herbarium-labels 0.1.0a3"
git push origin v0.1.0a3
```

The tag must point to the reviewed commit. Keep `v0.1.0a2` intact; do not force or move published tags. A correction after uploading a version requires another version.

## 4. Publish to TestPyPI

```sh
gh workflow run publish.yml --ref v0.1.0a3 -f target=testpypi
gh run list --workflow publish.yml --branch v0.1.0a3 --limit 5
```

Wait for the TestPyPI run to finish successfully before downloading. The workflow builds wheel/source archives, checks them, tests the installed wheel, and publishes only to the selected index. Run listing is read-only; do not trigger another upload just to inspect status.

## 5. Test the actual TestPyPI wheel

Use new environment/demo directories. Download only this package from TestPyPI, install its reviewed dependencies separately, and unset `PYTHONPATH` when checking the installed wheel:

```sh
python -m pip download --index-url https://test.pypi.org/simple/ \
  --no-deps --only-binary=:all: --dest dist/testpypi-0.1.0a3 \
  "herbarium-labels==0.1.0a3"
python -m venv data/release-a3-testpypi
data/release-a3-testpypi/bin/python -m pip install --require-hashes -r requirements.lock
data/release-a3-testpypi/bin/python -m pip install --no-deps \
  dist/testpypi-0.1.0a3/herbarium_labels-0.1.0a3-py3-none-any.whl
data/release-a3-testpypi/bin/python -m pip check
env -u PYTHONPATH data/release-a3-testpypi/bin/python -m unittest discover -s tests -v
env -u PYTHONPATH data/release-a3-testpypi/bin/python -m herbarium_labels profiles
env -u PYTHONPATH data/release-a3-testpypi/bin/python -m herbarium_labels demo \
  --output data/release-a3-testpypi-demo --pdf
```

Expect 84 passing tests and demo verification with `all_passed: true`. The demo and mock SDK tests make no paid requests. Confirm imports resolve to the new environment's `site-packages` if needed. TestPyPI and PyPI are separate services; using `--index-url` explicitly selects the index, while the separate lock installation avoids mixing dependency resolution between them.

## 6. Publish to PyPI

After the uploaded TestPyPI wheel passes validation:

```sh
gh workflow run publish.yml --ref v0.1.0a3 -f target=pypi
gh run list --workflow publish.yml --branch v0.1.0a3 --limit 5
```

Wait for this production run to finish successfully. Each workflow run rebuilds from the tag; identical source does not by itself establish identical archive hashes. Record actual URLs, artifact hashes, CI results, and remaining limitations after publication.

## 7. Verify installation from production

```sh
python -m venv data/release-a3-pypi
data/release-a3-pypi/bin/python -m pip install --index-url https://pypi.org/simple/ \
  "herbarium-labels[all]==0.1.0a3"
data/release-a3-pypi/bin/python -m pip check
env -u PYTHONPATH data/release-a3-pypi/bin/python -m herbarium_labels profiles
env -u PYTHONPATH data/release-a3-pypi/bin/python -m unittest discover -s tests -v
```

Check the published project page and release notes. A GitHub prerelease may then be created from the verified tag with `gh release create v0.1.0a3 --verify-tag --prerelease --title "herbarium-labels 0.1.0a3" --notes-file RELEASE_NOTES_FILE`, substituting the reviewed notes file.

## Existing research folders

Publication does not migrate real data or replace the private Taxa application. To continue a legacy batch, explicitly select its actual output folder:

```sh
herbarium-labels batch --profile po-bryophytes --images ./input \
  --output ./input/transcricao --accept-existing --pdf \
  --messages-json examples/synthetic/report-messages-po-pt.json
```

Acceptance preserves old JSON and records historical-source verification separately. It does not import Excel-only edits or bypass recorded image mismatches. New photographs require authorized API use and a budget; this is separate from release verification.

Reference: [GitHub CLI workflow dispatch](https://cli.github.com/manual/gh_workflow_run), [TestPyPI usage](https://packaging.python.org/en/latest/guides/using-testpypi/), and [Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/).
