# M0: Clean reset (spec)

Status: v2, with ChatGPT's review reconciled ([review](../../reviews/2026-10-29-chatgpt-m0-clean-reset.md)) · Planned for Fri 30 Oct · Built on plan v2

## Goal
Start from a clean, understandable workspace. At the end of M0 you can see where everything lives and what's installed, and Muse has proven it can get a real answer from a Meta model. No product features are built in M0.

## Decisions
1. **Product code repo:** `gabriellporfirio/Project-StarGate-Meta-Hackathon` on GitHub. At execution, Muse checks it still has no branches. A fresh repo is created at `~/Downloads/Projects/stargate` with `main` set explicitly. If that folder already exists, Muse stops and reports it instead of overwriting. Pushing needs your OK each time.
2. **Old work is archived by moving, safely.** `~/Downloads/Projects/Project-StarGate-Meta-Hackathon` (v1) and `~/Downloads/Projects/stargate-v2` move to `~/Downloads/Projects/_archive/`. Before moving, Muse records each folder's resolved path, git remote, current branch, last commit, and any uncommitted or untracked files, written to `_archive/ARCHIVE-LOG.md`. It refuses to move if the destination already exists. After the move it checks the same facts again and confirms they match. The old `.venv` folders inside are kept but treated as not runnable, since moved virtual environments break.
3. **Supported Python, kept inside the project.** Python 3.9 reached end of life on 31 Oct 2025, so the Mac's built-in 3.9.6 stays untouched and unused. Target **Python 3.12**. Muse first looks for an existing 3.12 or newer interpreter and records which one and where. If none exists, it **asks you in the chat before installing anything**, proposing a project-local runtime under `stargate/tools/` (for example via `uv` with its install directory set inside the project). Product code stays standard-library only. Setup is exactly: `python3.12 -m venv .venv` → `.venv/bin/pip install -e .` → `stargate doctor`, all recorded in the README.
4. **The plan is pinned, not "latest".** Muse uses a local clone of this plan repo at `~/Downloads/Projects/Project-Stargate`, checked out at the **exact commit named in the M0 prompt** (the merge commit of this spec). Before starting, it checks the clone's origin, that commit, and that the checkout is clean. If the folder holds something else, it stops and reports. `AGENTS.md` in the product repo records that commit.

## Steps
1. **Pre-flight (read-only):** check the plan clone (decision 4), the product repo state on GitHub (decision 1), and the archive destination (decision 2).
2. **Install inventory (read-only).** Write `INSTALL-LOG.md` with three separate sections:
   - **Current inventory:** what's installed now in Homebrew, `pip --user`, `~/.local/bin`, global npm and the Python interpreters found, with the exact commands used to check.
   - **Changes linked to earlier Muse sessions:** only what a record shows (for example Muse's own transcripts or logs, if Muse can read them), each with the record it came from.
   - **Unknown origin:** everything else. Missing history means "unknown", never "none installed".
   It never copies shell profiles, credentials or commands containing secrets, only package names, versions and locations. It never invents install or uninstall commands, and removes nothing.
3. **Archive** per decision 2, and verify.
4. **Python** per decision 3. Stop and ask if an install is needed.
5. **Create the product repo** with the files below. Checkpoint commit, no push.
6. **Implement `stargate doctor`**, the only product code in M0.
7. **Run the live Meta check once**, record its result in `docs/m0-live-check.md`, and write the plain-English report.

## Files in the new product repo
- `README.md`: what StarGate is, the exact setup commands, and where the plan lives (repo + pinned commit).
- `AGENTS.md`: rules for Muse. Read the pinned master plan and the current milestone spec first. Never install outside the project without asking in the chat. Log every install in `INSTALL-LOG.md`. Never touch the production phone or the VPN project. Never push.
- `INSTALL-LOG.md`, `docs/decisions.md`, `docs/m0-live-check.md`.
- `pyproject.toml`, `.gitignore`, `stargate/`, `tests/`.

## `stargate doctor` contract

**Checks that must pass (each one failing gives a non-zero exit):**

| Check | Pass means |
|---|---|
| Interpreter | the venv is active and running Python 3.12 or newer |
| Plan pin | the plan clone is at the pinned commit and clean |
| Meta credential | a key was found in the configured source: Keychain item `stargate-meta-api-key`, or `MODEL_API_KEY` if set. It reports which source was used, never the value |
| Meta inference | one real, small, authenticated request to the documented Meta API (`https://api.meta.ai/v1`, bearer auth) for a configured model. It returns a valid, non-empty answer within the limits below. It reports the endpoint, the model requested and the model returned |

Before coding, Muse checks the endpoint, auth header and model-list vs inference paths against the current docs at dev.meta.ai, and records the URLs it checked in `docs/decisions.md`. Listing models counts as discovery only and doesn't pass the inference check.

**Limits:** 20-second timeout, at most 1 retry, and a maximum of 16 output tokens. The key is sent only to the Meta API's host.

**Result codes it must tell apart:** `ok`, `missing-credential`, `auth-failed`, `quota-or-rate-limited`, `network-error`, `bad-response`, and `model-not-available`. Each one comes with a one-line plain-English explanation and what to do next.

**Report-only checks (never block):** git version, free disk, and whether adb/fastboot/emulator are present. Baseten runs only if both `BASETEN_API_KEY` (or its Keychain item) and `STARGATE_BASETEN_MODEL` are set. Otherwise it reports "skipped: not configured".

**Removed after review:** blanket network checks of future domains and the dummy Keychain test. Neither one proves model access.

## Tests (offline)
- Each result code, using a fake HTTP server or a mocked transport. Tests never make a real network call.
- The secret never appears in stdout, stderr, logs or any written file.
- An exit code other than zero when a required check fails. Zero only when all required checks pass.
- An interpreter below 3.12 fails the interpreter check.
- The test run must report how many tests ran. Zero tests counts as a failure.

## Done when (you can check each yourself)
- [ ] `cat ~/Downloads/Projects/_archive/ARCHIVE-LOG.md` shows both folders with matching before and after facts, and `git -C ~/Downloads/Projects/_archive/<folder> log -1` works for each.
- [ ] `INSTALL-LOG.md` has the three sections, the commands used, and no secrets.
- [ ] `cd ~/Downloads/Projects/stargate && .venv/bin/python --version` shows 3.12 or newer.
- [ ] `source .venv/bin/activate && stargate doctor` exits 0 and shows `Meta inference: ok` with the endpoint and model.
- [ ] Running `stargate doctor` with the key removed (`env -u MODEL_API_KEY`, Keychain item absent) shows `missing-credential` and exits non-zero.
- [ ] `python -m unittest -v` passes with a test count above zero.
- [ ] `git log` shows the checkpoint commit, `git status` is clean, and nothing was pushed.
- [ ] `docs/m0-live-check.md` records the live result with the date and model, and no key.

## Out of scope
Probes, research, strategy, UI, emulator, any Android SDK install, anything touching a phone, and removing anything found in the inventory.

## Open questions this milestone answers
Q2 (Meta endpoint and model IDs that work for your key). Q3 only if Baseten is configured.
