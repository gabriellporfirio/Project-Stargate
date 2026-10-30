# Task: prepare the product repo for M0 Part B

Status: completed 30 Oct 2026 · For: ChatGPT (it has write access to `Project-StarGate-Meta-Hackathon`; Claude doesn't) · Spec: [M0 Part B v3.1](../milestones/M0-clean-reset.md)

## Why

Part B creates a codespace from `gabriellporfirio/Project-StarGate-Meta-Hackathon`. At handoff that repo was empty, so it needed an initial commit before Codespaces could start from it. The codespace also needs read-only access to this private plan repo, so Muse can check out the pinned plan.

## Do

Commit these two files to `main` of `Project-StarGate-Meta-Hackathon`, exactly as written. It's the first commit, so it can't go through a PR. Nothing else goes in.

**`README.md`**
```
# StarGate
Turns old Android phones into private home servers. Meta hackathon project. Plan: Project-Stargate (private).
```

**`.devcontainer/devcontainer.json`**
```json
{
  "name": "StarGate",
  "image": "mcr.microsoft.com/devcontainers/python:1-3.12-bookworm",
  "customizations": {
    "codespaces": {
      "repositories": {
        "gabriellporfirio/Project-Stargate": { "permissions": { "contents": "read" } }
      }
    }
  }
}
```

## Check before committing

- The repo still has no branches or commits. If it has any, stop and report instead of overwriting.
- The image tag `1-3.12-bookworm` exists on the devcontainers Python image, and the `customizations.codespaces.repositories` permission format matches current GitHub docs. If either has changed, use the current equivalent and note it below.

## Done when

- [x] `main` has exactly these two files.
- [x] You've added a note below with the commit hash and anything you changed.

## Left for Gabriell (account settings, not repo)

- At github.com/settings/codespaces: idle timeout 30 min, and a secret `MODEL_API_KEY` scoped to `Project-StarGate-Meta-Hackathon` only.
- At github.com/settings/billing: Codespaces spending limit $0, and note the hours remaining.
- Then follow [plan/prompts/m0-part-b-codespace.md](../prompts/m0-part-b-codespace.md) from step 3.

## Notes

Completed by ChatGPT on 30 Oct 2026.

- Product repository was confirmed public and empty immediately before the writes (no branches; commits API returned `409 Git Repository is empty`).
- Final seed commit: [`59176961f59970e7192dd61a93ddcdba96897fd1`](https://github.com/gabriellporfirio/Project-StarGate-Meta-Hackathon/commit/59176961f59970e7192dd61a93ddcdba96897fd1). The GitHub contents API created two seed commits: README first, then devcontainer. No file-content deviations from the handoff.
- Verified the final tree contains exactly `README.md` and `.devcontainer/devcontainer.json`, and read both back to confirm exact matches.
- Checked the live Microsoft Container Registry manifest: `1-3.12-bookworm` returned HTTP 200, with Linux amd64 and arm64 entries. Observed index digest: `sha256:7876580dc67fd460fd962f004cbeb480027e9bbc0657096f1087db11f9eaff39`. The tag selects the Python 3.12/Bookworm line; it is not an immutable digest pin.
- Validated the JSON and the `customizations.codespaces.repositories` format against [GitHub's repository-access documentation](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-repository-access-for-your-codespaces). Only `contents: read` is requested for the private planning repo; no install hooks were added.
- Updated the Part B handoff to mark the seed complete, require an exact approved plan commit, use the venv's executable paths, and explain that new repository permissions require a new codespace. GitHub notes that rebuilding an existing codespace does not apply these permission changes.
- Account secrets, allowance/budget and idle timeout remain for the owner to verify. No codespace was created, no Mac software was installed, and no Muse runtime or live Meta request was tested here.

