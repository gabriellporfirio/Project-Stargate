# M0: Clean reset (spec)

Status: draft for ChatGPT review · Planned for Fri 30 Oct · Depends on plan v2 (PR #17)

## Goal
Start from a clean, understandable workspace. You can see where everything lives, what got installed, and that Muse can reach Meta's models. No product features are built in M0.

## Decisions this spec makes (please check)
1. **Product code repo:** `gabriellporfirio/Project-StarGate-Meta-Hackathon` on GitHub, which is still empty. It gets a fresh `main` locally at `~/Downloads/Projects/stargate`. Pushing needs your OK each time.
2. **Old work is archived, not deleted.** `~/Downloads/Projects/Project-StarGate-Meta-Hackathon` (v1) and `~/Downloads/Projects/stargate-v2` move to `~/Downloads/Projects/_archive/`.
3. **Python:** the Mac's built-in Python 3.9.6, with one `.venv` inside the project and the standard library only for now. Any new dependency must be justified in `docs/decisions.md`.
4. **The plan is linked, not copied.** The product repo's `AGENTS.md` points at this plan repo (master plan + milestone specs). Muse reads the plan from a local clone at `~/Downloads/Projects/Project-Stargate`.

## Steps
1. **Install audit (read-only).** List anything earlier Muse sessions installed outside a project folder: Homebrew packages, `pip --user` packages, `~/.local/bin`, global npm, and shell profile changes. Write it to `INSTALL-LOG.md` under "Found before M0" and change nothing. You decide later what to remove.
2. **Archive** the two old folders as in decision 2, using a move only. Confirm both open from the new path.
3. **Create the product repo** at `~/Downloads/Projects/stargate` with the files below, `git init`, remote set, no push.
4. **Clone the plan repo** to `~/Downloads/Projects/Project-Stargate` (read-only for Muse).
5. **Implement `stargate doctor`**, the only code in M0.
6. **Checkpoint commit** and a plain-English report.

## Files in the new product repo
- `README.md`: what StarGate is, how to run `stargate doctor`, and where the plan lives.
- `AGENTS.md`: rules for Muse. Read the master plan and the current milestone spec first. Never install outside the project without asking. Log every install. Never touch the production phone or the VPN project. Never push.
- `INSTALL-LOG.md`: every install with the date, exact command, location and how to undo it.
- `docs/decisions.md`: a decision log.
- `pyproject.toml`, `.gitignore`, `stargate/` (package), `tests/`.

## `stargate doctor` checks
Each check prints OK / MISSING / FAILED plus one line saying what that means and what to do.

| Check | How |
|---|---|
| Python version and venv active | `sys.version`, `sys.prefix` |
| git present | `git --version` |
| Plan repo found | path exists, and print its latest commit |
| Keychain usable | read a dummy item with `security`. Never print key values |
| Meta API key | a real minimal call. Print the model name the API returns or lists (answers Q2) |
| Baseten key (optional) | skipped if not set. Otherwise a real minimal call with the configured model |
| Network to allowlisted domains | HEAD request to each domain the plan will use |
| Disk free | for the project folder's volume |
| Android tools (report only) | adb, fastboot, emulator presence. Not installed in M0 |

## Done when (you can check each yourself)
- [ ] `ls ~/Downloads/Projects/_archive` shows both old folders, and the old work still opens.
- [ ] `INSTALL-LOG.md` exists and lists what earlier sessions installed, or says "none found" with the commands used to check.
- [ ] `cd ~/Downloads/Projects/stargate && source .venv/bin/activate && stargate doctor` runs and shows a real result for the Meta key, including the model name.
- [ ] `python -m unittest` passes, including tests that keys never appear in output or logs.
- [ ] `git log` shows one checkpoint commit, and `git status` is clean. Nothing was pushed.
- [ ] Muse's report states plainly what is real, what is simulated, and what is unknown.

## Out of scope
Probes, research, strategy, UI, emulator, any Android SDK install, anything touching a phone.

## Open questions this milestone answers
Q2 (Meta model IDs and endpoint). Partly Q3 (Baseten: whether a key works, and which model).
