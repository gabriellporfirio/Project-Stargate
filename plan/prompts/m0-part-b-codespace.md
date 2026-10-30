# M0 Part B: cloud workspace

## Step 1: product repository prepared

Completed on 30 Oct 2026: [`main` at `5917696`](https://github.com/gabriellporfirio/Project-StarGate-Meta-Hackathon/commit/59176961f59970e7192dd61a93ddcdba96897fd1) contains the requested README and `.devcontainer/devcontainer.json`. Do not recreate them.

The devcontainer uses the verified `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm` tag and requests only `contents: read` for the private `gabriellporfirio/Project-Stargate` planning repo. The tag selects the Python 3.12/Bookworm line, rather than an immutable image digest. See the [completed preparation task](../tasks/2026-10-30-prepare-product-repo.md) for verification.

## Step 2: settings (github.com)

- [Codespaces settings](https://github.com/settings/codespaces): set the default idle timeout to 30 minutes. Add a secret `MODEL_API_KEY` (your Meta key) with repository access set to **Project-StarGate-Meta-Hackathon only**.
- [Billing](https://github.com/settings/billing): confirm the Codespaces spending limit is $0, and note how many hours remain.

## Step 3: create the codespace

On the product repo: **Code → Codespaces → ⋯ → New with options → 4-core**, from `main`. When asked, authorise read access to Project-Stargate. Create a **new codespace**: these additional repository permissions are not applied to an existing one by rebuilding it. The planning repo can stay private. If a previous codespace has work in it, preserve that work before retiring it.

## Step 4: install Muse inside the codespace

In the codespace terminal, follow Muse's official **Linux** install and sign-in steps from [dev.meta.ai/docs/muse-code](https://dev.meta.ai/docs/muse-code). This install happens in the cloud, not on your Mac. If sign-in needs a browser, use the device-code or link option it offers (this answers Q9). Then start it with approvals on: `muse --approval-mode on-request --approval-judge on`.

## Step 5: pin the approved plan, then paste into Muse

After [PR #19](https://github.com/gabriellporfirio/Project-Stargate/pull/19) is merged, copy its full 40-character merge commit SHA. Replace `REPLACE_WITH_PR_19_MERGE_COMMIT_SHA` below with that value before sending the prompt. Use that exact approved commit, not a moving branch or whichever commit looks newest.

```
StarGate M0 Part B. The approved plan is the repo gabriellporfirio/Project-Stargate, milestone plan/milestones/M0-clean-reset.md, Part B (v3.1).
Approved plan commit: REPLACE_WITH_PR_19_MERGE_COMMIT_SHA
If this value is still a placeholder or not a full commit SHA, stop before setup and report the missing pin. Do only M0. Build no product features.

You are in a GitHub Codespace created from gabriellporfirio/Project-StarGate-Meta-Hackathon. Rules: keep command approvals and the sandbox on. Never push. Never touch my Mac, a phone, or my private StarGate/VPN work. The Meta key is only in the MODEL_API_KEY environment variable: never print it, log it, or write it to a file.

1. Pre-flight (read-only): confirm this is the product repo in a Codespace. Show `python3 --version` and its path, the git origin with any credentials redacted, and whether MODEL_API_KEY is set (yes/no only).
2. Use the Codespace's existing GitHub authentication to clone https://github.com/gabriellporfirio/Project-Stargate to /workspaces/Project-Stargate and check out the exact approved plan commit above. If the destination already exists, verify and reuse the matching clean checkout; never overwrite unrelated work. Verify the origin, full HEAD SHA and clean checkout, then read plan/master-plan.md and plan/milestones/M0-clean-reset.md from that commit. Follow them if they conflict with this prompt. If access fails, report the missing Codespaces repository permission; do not change repository visibility or print tokens.
3. Bootstrap proposal: list every install you need in this codespace (tool, version, source, exact command). Stop and wait for my approval. Expect only what's needed for a standard-library Python package.
4. After approval, follow Part B (B2 and B3) of the spec exactly: the product files, `python3 -m venv .venv` with the 3.12 interpreter, `.venv/bin/pip install -e .`, and `stargate doctor` with the full result-code contract and offline tests. Before coding the Meta call, check the endpoint, auth and inference path against the current dev.meta.ai docs, and record the URLs.
5. From the product repo, run `.venv/bin/stargate doctor` once live, then `env -u MODEL_API_KEY .venv/bin/stargate doctor` for the missing-key case. Run `.venv/bin/python -m unittest -v`; zero tests is a failure. Use these explicit paths so success does not depend on shell activation persisting between commands. Record the live result in docs/m0-live-check.md.
6. Make one checkpoint commit. Do not push.

Finish with a short plain-English report in exactly these sections: Plan commit used · Installed in this codespace · Doctor live result (endpoint, model requested and returned) · Doctor without key · Tests (count, pass/fail) · Not done or unknown.
```
Paste the report back into the project thread for review.
