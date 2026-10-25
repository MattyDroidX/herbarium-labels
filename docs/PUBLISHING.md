# Testing, building, and publishing

The maintainer selected `MattyDroidX/herbarium-labels` and GitHub plus TestPyPI followed by PyPI. The proposed English API version is `0.1.0a2` (transcription/catalogue schema `0.2.0`). The SSH remote is `git@github.com:MattyDroidX/herbarium-labels.git`.

**Maintainer control:** only the maintainer applies repository changes, commits, tags, pushes, or initiates publication unless they explicitly delegate an action. Commands below are instructions for the maintainer, not authorization for an assistant to execute them. An assistant can prepare patches and test isolated copies without applying changes to this repository.

## 1. Review the release scope

This alpha shares two existing transcription workflows and documentary catalogue models. It does not implement automatic handwriting attribution, example retrieval, a review interface, or the planned v2 schema. Preserve the research-use evidence and its limits in [EVIDENCE.md](EVIDENCE.md).

Documentation is English. The proposed English API renames CLI commands, fields, enum values, and report labels; prompt instructions are translated with original-language evidence preserved. Read `MIGRATION.md` and `PROMPT_CHANGES.md`. Legacy JSON remains readable without rewriting it. The wheel contains runtime modules and license notices; the source distribution also includes documentation, tests, tools, and the draft catalogue. It contains no collection images or private research results.

Review any proposed patch before applying it. The Pillow 13 requirement and regenerated lock are part of the current review proposal, following advisory findings for Pillow 12.3.0. A change in codec version invalidates content/configuration cache reuse and requires a fresh transcription output directory.

## 2. Install and test locally

From an applied and reviewed source tree, create a virtual environment and activate it using the instructions in [README.md](../README.md):

```sh
python -m pip install --require-hashes -r requirements.lock
python -m pip install --no-deps -e .
python -m unittest discover -s tests -v
```

Ordinary tests are offline, use synthetic images, and simulate the provider, including the installed SDK's HTTP transport. No real key is needed. Run `python -m herbarium_labels demo --output ./demo-output --pdf` to inspect a full synthetic delivery; see `TESTING.md`. Record actual results in [VALIDATION.md](../VALIDATION.md). The configured CI matrix requests Linux and Windows with Python 3.11–3.14; local preparation alone does not establish those remote results.

A live transcription is a separate integration check. Select permitted images, verify the configured model and prices, and define a spending limit before running it. Do not silently reuse a private application's key or images. Until performed, describe live provider behavior and real HEIF decoding as unverified in this extracted alpha.

## 3. Build and inspect distributions

```sh
python -m pip install --require-hashes -r requirements-dev.lock
python -m build --no-isolation
python -m twine check --strict dist/*
python tools/check_dist.py dist/*
python -m pip_audit -r requirements.lock --require-hashes --disable-pip
python -m pip_audit -r requirements-dev.lock --require-hashes --disable-pip
```

The development lock includes the tested setuptools backend. `--no-isolation` uses those locked build tools; a default isolated build may resolve another allowed backend version. Dependency auditing contacts public advisory services, unlike ordinary offline tests. Inspect findings rather than suppressing them to obtain a passing result.

`MANIFEST.in` declares source-distribution inputs. `tools/check_dist.py` checks allowed paths, required modules/license notices, metadata, archive integrity, and common credential patterns without extraction. Review the actual member list as well; this limited scanner does not replace an external audit.

Rebuild after documentation or metadata changes. Refresh `MANIFEST.sha256` from the explicit public-file list, excluding the manifest itself and all generated/private files. Do not treat an old distribution manifest as hashes of a new source tree.

## 4. Test the installed wheel

Use a fresh environment that has never installed the source tree in editable mode:

```sh
python -m venv .wheel-venv
.wheel-venv/bin/python -m pip install --require-hashes -r requirements.lock
.wheel-venv/bin/python -m pip install --no-deps dist/*.whl
.wheel-venv/bin/python -m unittest discover -s tests -v
.wheel-venv/bin/python -m herbarium_labels --help
```

These shell commands use Linux/macOS paths; on Windows use `.wheel-venv\Scripts\python.exe` and the exact wheel filename. Check `herbarium_labels.__file__` to confirm imports come from that environment's `site-packages`, not `src/`. Tests do not insert the source directory automatically.

Check the source distribution too: build its wheel in isolation or in a clean copy with the locked backend. Do not trust an editable-install-only test as evidence that a wheel contains the required modules.

## 5. Review and publish source on GitHub

Preserve the existing Git repository and any remote history. Do not reinitialize it or force-push. Before the first commit, review the public-file list, secrets, license/provenance, package contents, author identity, and test results. The maintainer then stages only intended public files and creates the commit.

The configured remote is already `origin`. The maintainer can verify it and inspect remote branches before pushing:

```sh
git remote -v
git ls-remote --heads origin
git status --short
# After reviewing and committing the intended files:
git push -u origin main
```

No commit/push is implied by this guide. Resolve existing remote content without overwriting it. After the maintainer's push, inspect the actual Actions results. Enable the repository's private vulnerability-reporting feature and update `SECURITY.md` with the verified route. Configure repository protections appropriate to the maintainer's workflow.

## 6. Configure Trusted Publishing

Create/use accounts on TestPyPI and PyPI; they are independent services. Do not share passwords, API tokens, SSH private keys, or recovery codes in chat or commit them.

For a new project, configure a pending GitHub Trusted Publisher on each index. A pending publisher does not reserve the package name; verify name availability when publishing. Use these exact settings:

| Setting | TestPyPI | PyPI |
| --- | --- | --- |
| Project name | `herbarium-labels` | `herbarium-labels` |
| GitHub owner | `MattyDroidX` | `MattyDroidX` |
| Repository | `herbarium-labels` | `herbarium-labels` |
| Workflow filename | `publish.yml` | `publish.yml` |
| GitHub environment | `testpypi` | `pypi` |

Create matching GitHub environments. The manual workflow requests `id-token: write` only in the publishing job and uses PyPA's publishing action. It does not store a long-lived PyPI token. See [PyPI's new-project instructions](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) and [publishing workflow documentation](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## 7. Validate on TestPyPI

After applying/reviewing changes, passing CI, and selecting the release commit, the maintainer creates and pushes `v0.1.0a2`. The workflow requires a tag exactly matching `pyproject.toml`'s version; running it on `main` fails before publication.

The workflow file must already be on the default branch. The maintainer can run it for the tag using GitHub CLI, if installed/authenticated:

```sh
gh workflow run publish.yml --ref v0.1.0a2 -f target=testpypi
```

This is a manual publication action. The workflow builds wheel/source archives, checks them, tests the installed wheel, and uploads to TestPyPI only when the selected target is `testpypi`.

Test the uploaded package rather than substituting a local wheel. Download only this project from TestPyPI, then resolve runtime dependencies from the reviewed lock/public PyPI in a fresh environment:

```sh
python -m pip download --index-url https://test.pypi.org/simple/ --no-deps --only-binary=:all: --dest testpypi-wheel 'herbarium-labels==0.1.0a2'
python -m venv .testpypi-venv
.testpypi-venv/bin/python -m pip install --require-hashes -r requirements.lock
.testpypi-venv/bin/python -m pip install --no-deps testpypi-wheel/*.whl
.testpypi-venv/bin/python -m herbarium_labels --help
.testpypi-venv/bin/python -m unittest discover -s tests -v
```

Use exact wheel paths and `Scripts/python.exe` on Windows. This avoids mixing dependency resolution between package indexes. Record the real TestPyPI URL, version, artifact hashes, and test results. Uploading an existing filename/version again is not a repair mechanism; increment the version when a correction requires a new release.

## 8. Publish the alpha on PyPI

Only after the TestPyPI installation checks and review, the maintainer triggers the same tagged source with `target=pypi`:

```sh
gh workflow run publish.yml --ref v0.1.0a2 -f target=pypi
```

Each manual run rebuilds from that tag; do not claim identical archive hashes unless measured. Verify the actual PyPI page, fresh-environment installation, module/CLI imports, and release notes. Alpha releases use prerelease versions; an exact version such as `herbarium-labels[all]==0.1.0a2` selects it explicitly.

Publish GitHub release notes with the actual artifacts/results and known limitations. Record URLs/CI runs only after success. No TestPyPI or PyPI upload has been made by this preparation.
