# M0 Part B: cloud workspace

## Step 1: add two files to Project-StarGate-Meta-Hackathon (on github.com)
Use **Add file → Create new file** for each one, then commit to `main`.

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
The image pins Python 3.12. The `repositories` block makes GitHub ask you, when the codespace is created, to give it read-only access to the plan repo. Say yes.

## Step 2: settings (github.com)
- [Codespaces settings](https://github.com/settings/codespaces): set the default idle timeout to 30 minutes. Add a secret `MODEL_API_KEY` (your Meta key) with repository access set to **Project-StarGate-Meta-Hackathon only**.
- [Billing](https://github.com/settings/billing): confirm the Codespaces spending limit is $0, and note how many hours remain.

## Step 3: create the codespace
On the repo: **Code → Codespaces → ⋯ → New with options → 4-core**. When asked, authorise read access to Project-Stargate.

## Step 4: install Muse inside the codespace
In the codespace terminal, follow Muse's official **Linux** install and sign-in steps from [dev.meta.ai/docs/muse-code](https://dev.meta.ai/docs/muse-code). This install happens in the cloud, not on your Mac. If sign-in needs a browser, use the device-code or link option it offers (this answers Q9). Then start it with approvals on: `muse --approval-mode on-request --approval-judge on`.

## Step 5: paste this into Muse
```
StarGate M0 Part B. The approved plan is the repo gabriellporfirio/Project-Stargate, milestone plan/milestones/M0-clean-reset.md, Part B (v3.1). Do only M0. Build no product features.

You are in a GitHub Codespace created from gabriellporfirio/Project-StarGate-Meta-Hackathon. Rules: keep command approvals and the sandbox on. Never push. Never touch my Mac, a phone, or my private StarGate/VPN work. The Meta key is only in the MODEL_API_KEY environment variable: never print it, log it, or write it to a file.

1. Pre-flight (read-only): show `python3 --version` and its path, `git remote -v`, and whether MODEL_API_KEY is set (yes/no only).
2. Clone https://github.com/gabriellporfirio/Project-Stargate to /workspaces/Project-Stargate and check out the newest merge commit on main that contains M0 spec v3.1. Show its hash. Verify the origin and a clean checkout. Read plan/master-plan.md and plan/milestones/M0-clean-reset.md, and follow them over anything here if they conflict.
3. Bootstrap proposal: list every install you need in this codespace (tool, version, source, exact command). Stop and wait for my approval. Expect only what's needed for a standard-library Python package.
4. After approval, follow Part B (B2 and B3) of the spec exactly: the product files, `python3 -m venv .venv` with the 3.12 interpreter, `.venv/bin/pip install -e .`, and `stargate doctor` with the full result-code contract and offline tests. Before coding the Meta call, check the endpoint, auth and inference path against the current dev.meta.ai docs, and record the URLs.
5. Run `stargate doctor` once live, then once with MODEL_API_KEY unset. Run `python -m unittest -v`. Record the live result in docs/m0-live-check.md.
6. Make one checkpoint commit. Do not push.

Finish with a short plain-English report in exactly these sections: Plan commit used · Installed in this codespace · Doctor live result (endpoint, model requested and returned) · Doctor without key · Tests (count, pass/fail) · Not done or unknown.
```
Paste the report back into the project thread for review.
