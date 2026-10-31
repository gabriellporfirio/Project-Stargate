# M3: Strategy and fit engines (spec)

Status: v1, 31 Oct 2026, for review. Builds on M1 (device profiles, final commit `1210cd92e12f64f1d64c399c003e287584ac78c1`) and M2 (research reports). The M3 prompt pins the final M2 commit.

## Goal
For one phone and one selection of services, StarGate answers two questions with plain, predictable code:
1. **Strategy:** which ways of building StarGate OS for this phone are possible, ranked, with reasons, risks and signing implications.
2. **Fit:** do the chosen services fit this phone (memory, storage, CPU, kernel features, AI model size)? A selection that doesn't fit is **refused with a reason**.

A Meta model then explains the result in plain English. It never makes or changes a decision. This is M1's "no fit conclusions" rule in reverse: M3 is the one place fit conclusions are made, and only by code.

## 1. Inputs
- **Profile** (`profile-v1`, from M1): `--sim <fixture>`, or a saved profile file.
- **Research** (`research-v1`, from M2): `--research <file>`. Only the **typed facts** layer (3b) is read. Model notes and repo candidates are ignored. Simulated phones are invented, so each M1 fixture gets a matching **synthetic research file** in M3, with `provenance: synthetic` and labelled SIMULATED.
- **Selection:** `--services files`, `--services files,assistant`, and so on. Only `files` and `assistant` exist in M3. Anything else is invalid input.
- **Model catalog** (for Assistant): a pinned local file listing candidate on-device models, each with `{id, source, revision, file_bytes, licence, runtime, abi}`. Every value has a source or is `unknown`. Real entries come from M2's `ai.candidates` or official model pages. Test entries are synthetic and labelled so. Whether Muse Glimmer can be an entry is Q15, and its values stay `unknown` until checked.

## 2. Bootloader lock: a new inference rule
M1 left `boot.bootloader_locked` as `unknown` / `deferred`, because no official source documents the property it read. M3 adds an **inference rule** instead, `R-LOCK-FROM-VBS`, listed in `docs/inference-rules.md` with its source. Android's verified-boot documentation defines the boot states: green and yellow are locked, and orange is unlocked. So:

| `boot.verified_boot_state` | `boot.bootloader_locked` |
|---|---|
| `green` or `yellow` | `true`, status `inferred` |
| `orange` | `false`, status `inferred` |
| `red`, `unknown` or `conflicting` | stays `unknown` |

Muse quotes the exact documentation sentence and URL in `docs/inference-rules.md`. If it can't find one, the rule isn't added, and the lock stays `unknown`.

## 3. Strategy engine
Five strategies, each judged by fixed rules written as a table in `docs/strategy-rules.md`. Each rule names the fact IDs it reads.

| Strategy | Possible when (all true) | Blocked when (any true) |
|---|---|---|
| `community_build` (e.g. LineageOS device tree) | `lineage.support` is `current`; `repos.device_tree` has an established repo; unlock possible (below) | Unlock impossible; support is `historical_only` or `not_listed` |
| `generic_system_image` (GSI) | `boot.treble_enabled` true; unlock possible | Treble false; unlock impossible |
| `linux` (postmarketOS-style) | `pmos.status` is `listed`; unlock possible | `pmos.status` is `not_found`; unlock impossible |
| `stock_rebuild` | Never in M3 | Always `not_covered` (M2 doesn't research stock firmware) |
| `on_top_of_android` | Always possible: no unlock, StarGate runs as apps on the existing Android | Never |

**Unlock possible** means `boot.bootloader_locked` is `false`, or (`boot.oem_unlock_supported` is true **and** `boot.oem_unlock_allowed` is true). **Unlock impossible** means `boot.oem_unlock_supported` is false. Anything else is `unknown`.

Each strategy ends up as one of:
- `possible`, with the fact IDs that made it possible.
- `blocked`, with the fact ID and value that blocked it.
- `unknown`, naming the missing facts. An `unknown` is **never** treated as possible.
- `not_covered`.

**Ranking:** possible strategies are listed in a fixed, documented order: community build, then GSI, then Linux, then on top of Android. `unknown` ones come after, and `blocked` ones last. Every strategy carries fixed, code-owned text for its **risks** (for example "unlocking wipes the phone's data" or "a GSI may have hardware features that don't work") and its **signing implication** (for example "verified boot shows orange after unlocking; relocking needs your own signing key, if the phone supports it"). Each piece of text cites its source in `docs/strategy-rules.md`, or is labelled "StarGate's own guidance".

## 4. Fit engine
For each selected service, code compares requirements with the phone's facts. The requirements live in `docs/fit-budgets.md`, one row each, with a source or the label **"planning estimate"**:

| Check | Phone fact | Requirement |
|---|---|---|
| Files: storage | `resources.data_free` | At least the Files budget (planning estimate) |
| Assistant: CPU | `resources.cpu_abis` | Includes the ABI the runtime needs (from the catalog entry) |
| Assistant: memory | `resources.ram_total` | At least OS baseline + model `file_bytes` × runtime factor (factor and baseline are planning estimates) |
| Assistant: storage | `resources.data_free` | At least the model's `file_bytes` plus the Files budget, if Files is selected too |
| Kernel features | `kernel.config.*` | Only checked if a service in M3 needs one. Otherwise listed as "not needed yet" |
| Image size | `capacity.system_image_max` | Always `unknown` (M1 doesn't collect it). Shown as "not checked yet", never as fits |

Each check gives `fits`, `does_not_fit` (with both numbers, in bytes and in readable units) or `unknown` (with the missing fact). The **selection result** is:
- **`refused`** if any check is `does_not_fit`, with each reason. The CLI exits with code 7.
- **`unconfirmed`** if nothing fails but something is `unknown`. Allowed, but labelled "can't confirm" everywhere.
- **`fits`** only if every applicable check is `fits`.

If no catalog model fits, the Assistant is refused with that reason. Code picks the largest model that fits, and the choice is explained.

## 5. Meta explanation (optional, `--explain`)
One Meta call (`muse-spark-1.3`, `max_completion_tokens` 2048, one retry) receives the plan's decisions and fact IDs, and writes a short plain-English explanation of the risks for a non-specialist. It's stored as **model notes**, labelled "model explanation, not checked", exactly as in M2. Code checks that every fact ID it cites exists. The explanation never changes a status, a ranking or the selection result. Without `--explain`, M3 makes no network calls. A missing key or Meta failure only affects the explanation, using M0's result codes, and the plan itself is still printed.

## 6. `stargate plan`
```
stargate plan --sim <fixture> --services files,assistant [--research <file>] [--explain] [--json] [--json-out <file>]
```
- It prints a readable plan: the strategies in ranked order with status, reasons and risks, then the fit table, then the selection result, then the labelled explanation.
- `--json` / `--json-out` give a validated **`plan-v1`** report: `schema_version`, `subject`, `inputs` (the profile, research and catalog, each with its SHA-256), `strategies`, `fit`, `selection_result`, `notes`, and `provenance`.
- **Exit codes:** 0 the plan is `fits` or `unconfirmed`, 7 the selection is refused, 6 invalid input, 2 or 5 only when `--explain` was asked for and the Meta call failed. In that case the plan is still printed and saved.

## 7. Tests (offline)
- **The inference rule:** every row of the table in section 2, including that `red` and `unknown` don't become locked or unlocked.
- **Strategies:** each rule in section 3 has a test for possible, blocked and unknown. `unknown` never becomes possible. `stock_rebuild` is always `not_covered`. `on_top_of_android` is always possible.
- **Two different phones give different rankings:** for example `flagship` (Treble, 64-bit, current LineageOS support in its synthetic research) against `old32`.
- **Refusals:** `old32` with Assistant is refused (no 64-bit ABI). `budget` with Assistant is refused when RAM is below the requirement. Each refusal names the fact and both numbers.
- **Unknowns:** a missing fact gives `unconfirmed`, never `fits`.
- **The model can't change decisions:** a recorded model response claiming "this phone can run GSI" leaves the GSI status unchanged. A note citing a missing fact ID is flagged.
- **Research layers:** repo candidates and model notes in the research file are ignored, and only typed facts are read.
- **Bytes:** sizes are compared in whole bytes. A value like "2 GB" in a requirement file is rejected.
- **CLI and schema:** exit codes, `--json` parsed from real stdout, and valid and invalid `plan-v1` examples.
- **Network:** the full suite runs with sockets blocked. The `--explain` tests use recorded responses.

## Done when
- [ ] `R-LOCK-FROM-VBS` is documented with its official source and tested, or reported as not found (with the lock left `unknown`).
- [ ] `docs/strategy-rules.md` and `docs/fit-budgets.md` exist, every number has a source or is labelled "planning estimate", and every risk and signing text is cited or labelled.
- [ ] `stargate plan --sim flagship --services files,assistant` and `stargate plan --sim old32 --services files,assistant` give clearly different rankings, and the second refuses the Assistant with a reason (exit 7).
- [ ] `--json-out` validates against `plan-v1` for all four fixtures with `--services files`.
- [ ] One live `--explain` run on `flagship` shows a labelled explanation, and every fact ID it cites exists.
- [ ] All tests pass offline (count above zero), and `stargate doctor` still passes.
- [ ] No installs, one checkpoint commit, nothing pushed, and the reviewer Muse checks the commit before M4.

## Out of scope
Building anything (M4), real phones, research beyond what M2 saved, the Files and Assistant apps themselves, and any new Meta model besides `muse-spark-1.3` for explanations.

## Network use allowed in M3
One live `--explain` run and one `stargate doctor` regression run. Nothing else.

## Demo (under 5 minutes)
```
.venv/bin/stargate plan --sim flagship --services files,assistant; echo "flagship exit $?"
.venv/bin/stargate plan --sim old32 --services files,assistant; echo "old32 exit $? (expect 7)"
.venv/bin/stargate plan --sim flagship --services files,assistant --explain --json-out /tmp/p.json; echo "explain exit $?"
.venv/bin/python -m stargate.plan validate /tmp/p.json; echo "validate exit $?"
.venv/bin/python -m unittest; echo "tests exit $?"
```
