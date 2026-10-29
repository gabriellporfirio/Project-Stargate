# M0: Clean slate + cloud workspace (spec)

Status: v3, draft. Folds in the [cloud-reset addendum](../../reviews/2026-10-29-chatgpt-m0-cloud-reset.md). Assumes the hosting choice "cloud dev, Mac emulator for M4" is still awaiting your pick. Replaces the local-workspace approach in v2. Planned for Fri 30 Oct.

## Goal
1. The Mac is cleaned: the old Muse hackathon folders go to the Trash, and you get a truthful inventory of what's installed.
2. A fresh cloud workspace exists, with Muse running in it, and it has proven it can get a real answer from a Meta model.

No product features are built in M0, and nothing new is installed on the Mac.

## Part A: Mac cleanup (no installs)
Use the prompt in [plan/prompts/muse-clean-slate-and-install-guard.md](../prompts/muse-clean-slate-and-install-guard.md) as written. In summary:
- Muse resolves and verifies the two old folders (`~/Downloads/Projects/Project-StarGate-Meta-Hackathon`, `~/Downloads/Projects/stargate-v2`), then moves them to the macOS Trash. No wildcards, nothing overwritten, and Trash isn't emptied, so it's reversible. Ambiguous folders are reported, not moved.
- It takes a read-only inventory of installs in three groups: present now, attributable to Muse by a record, and unknown origin. No secrets, no raw shell profiles.
- Any uninstall is proposed separately, with its impact, and waits for your OK.
- The planning repo clone (if any) and your private StarGate/VPN work are left untouched.

**Done when:** both folders are in the Trash (restorable), you have the cleanup report, and nothing was installed or removed beyond those two moves.

## Part B: Cloud workspace proposal, then setup

### B1. Proposal: you approve this before anything is created

| Item | Proposal | To verify before approval |
|---|---|---|
| Provider | GitHub Codespaces (browser or VS Code) | Muse CLI runs on Linux in Codespaces (Muse documents Linux support) |
| Starting point | A **blank-template** codespace, so nothing has to be pushed to the empty product repo first. It gets connected to `Project-StarGate-Meta-Hackathon` later, at a push you approve | Whether that repo is private (Q10) |
| Machine | 4-core / 16 GB RAM / 32 GB storage | Enough for M0–M3, with no Android builds |
| Cost | Covered by your account's included Codespaces hours and storage while they last | Your remaining included usage on GitHub's billing page |
| Spending cap | Codespaces spending limit set to **$0**, so it stops rather than bills | That the limit is $0 on your account |
| Idle shutdown | 30 minutes | |
| Persistence | Work lives in git. Checkpoint commits stay in the codespace until you approve a push. A stopped codespace keeps its files (and uses storage) until deleted | Retention period setting |
| Secrets | `MODEL_API_KEY` as a Codespaces user secret scoped to this codespace's repo. It's never written to files. No Mac Keychain, no Mac folder mounts | |
| Muse login | Muse CLI's own sign-in is separate from the product's Meta API key, and kept separate | How Muse authenticates on a headless Linux machine (Q9) |

### B2. Bootstrap (one reviewable plan inside the codespace)
Muse proposes a single bootstrap plan: every install in the codespace with its version, source and command. That's one approval, then nothing extra without asking. It runs with its command approvals and sandbox turned on. After bootstrap:
- the planning repo is cloned read-only and checked out at the **pinned commit named in the prompt**, with the origin and a clean checkout verified
- `python3 -m venv .venv` runs with the codespace's actual Python (3.12 or newer, path recorded), then `.venv/bin/pip install -e .`
- the product files are `README.md`, `AGENTS.md`, `INSTALL-LOG.md` (codespace installs), `docs/decisions.md`, `docs/m0-live-check.md`, `pyproject.toml`, `stargate/` and `tests/`

### B3. `stargate doctor`
Same contract as v2, with these changes:
- **Credential:** read only from the `MODEL_API_KEY` environment variable (the Codespaces secret). There's no Keychain lookup.
- **Required checks:** the interpreter (3.12+), the plan pin, the Meta credential present, and Meta inference. Inference means one real authenticated request to the documented Meta API that returns a valid, non-empty answer. It reports the endpoint and the model requested/returned. Listing models doesn't count.
- **Limits:** 20-second timeout, 1 retry, and a small output-token cap within what the model accepts (record the value used).
- **Result codes:** `ok`, `missing-credential`, `auth-failed`, `quota-or-rate-limited`, `network-error`, `bad-response`, `model-not-available`. Any required failure exits non-zero.
- **Report-only:** git, free disk, and Baseten (only if both key and model are configured).
- **Tests:** offline, covering each result code, a secret never appearing in output or logs, exit codes, and a test count above zero.

**Done when:**
- [ ] B1 is approved by you, and the codespace exists with a $0 spending limit and a 30-minute idle timeout.
- [ ] `INSTALL-LOG.md` lists every codespace install from the approved bootstrap and nothing else.
- [ ] `stargate doctor` exits 0 with `Meta inference: ok`, the endpoint and the model, and exits non-zero with `missing-credential` when the variable is unset.
- [ ] `python -m unittest -v` passes with a test count above zero.
- [ ] There's a checkpoint commit in the codespace, and nothing has been pushed.

## Out of scope
Probes, research, strategy, UI, emulator, any Android SDK, anything touching a phone, any Mac install, and any uninstall you haven't approved.

## Open questions this milestone answers
Q2 (Meta endpoint and model IDs), Q9 (Muse sign-in in the cloud), Q10 (product repo visibility), and Q3 if Baseten is configured.
