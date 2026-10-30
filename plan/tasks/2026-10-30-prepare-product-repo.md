# Task: prepare the product repo for M0 Part B

Status: open · For: ChatGPT (it has write access to `Project-StarGate-Meta-Hackathon`; Claude doesn't) · Spec: [M0 Part B v3.1](../milestones/M0-clean-reset.md)

## Why
Part B creates a codespace from `gabriellporfirio/Project-StarGate-Meta-Hackathon`. That repo is empty, and GitHub can't create a codespace from an empty repo. The codespace also needs read-only access to this private plan repo, so Muse can check out the pinned plan.

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
- [ ] `main` has exactly these two files.
- [ ] You've added a note below with the commit hash and anything you changed.

## Left for Gabriell (account settings, not repo)
- At github.com/settings/codespaces: idle timeout 30 min, and a secret `MODEL_API_KEY` scoped to `Project-StarGate-Meta-Hackathon` only.
- At github.com/settings/billing: Codespaces spending limit $0, and note the hours remaining.
- Then follow [plan/prompts/m0-part-b-codespace.md](../prompts/m0-part-b-codespace.md) from step 3.

## Notes
_(ChatGPT: add the commit hash and any deviations here.)_
