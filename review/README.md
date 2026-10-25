# English API review materials

The main working tree now has English documentation filenames and public synthetic images/reports. The runtime migration itself remains a maintainer-applied proposal.

[english-api.patch](english-api.patch) is the updated cumulative code/release proposal against the current repository tree. It supersedes the earlier temporary-directory patches. Do not apply it on top of an older patch. Only the maintainer applies changes, commits, or pushes unless explicitly delegated; no automatic application is performed.

The maintainer can check applicability before choosing to apply it:

```sh
git apply --check review/english-api.patch
```

Once the maintainer has reviewed/applied the proposal, follow [the testing guide](../docs/TESTING.md). Before that, the English `demo` command is not yet available in the main runtime. The already-generated [synthetic artifacts](../examples/synthetic/README.md) can be opened immediately without Python or an API key.

The proposal was previously tested with 42 offline tests on source and the installed wheel; the current pre-migration runtime has its own suite. Results and limits are recorded separately in [VALIDATION.md](../VALIDATION.md). The translated scientific prompts still need an authorized live comparison; mock outputs do not prove transcription accuracy.

This directory is a maintainer handoff and is excluded from Python distributions. It is not required for library users after the migration is applied.
