# M3: Strategy and fit engines (spec)

Status: v2.1, 1 Nov 2026, for review. v1 was reviewed by ChatGPT (`reviews/2026-11-01-chatgpt-m3-strategy-fit.md`), and v2 fixed all five findings. v2.1 fixes the re-review (`reviews/2026-11-01-chatgpt-m3-strategy-fit-v2.md`): the handoff now carries the decision, and M4 must check the whole plan before building. Builds on M1 (device profiles, final commit `1210cd92e12f64f1d64c399c003e287584ac78c1`) and M2 (research reports, commit `7c73173de9de36a1a88d15da338612c5a836aa08`, under review). The M3 prompt pins the reviewed M2 commit.

## Goal
For one phone and one selection of services, StarGate answers two questions with plain, predictable code:
1. **Strategy:** which ways of building StarGate OS for this phone are worth trying, ranked, with reasons, risks, signing implications and what is still unchecked.
2. **Fit:** do the chosen services fit this phone (memory, storage, CPU, AI model size)? A selection that definitely doesn't fit is **refused with a reason**. A selection that can't be confirmed is **labelled unconfirmed**, never shown as fitting.

A Meta model then explains the result in plain English. It never makes or changes a decision. M3 is the one place fit conclusions are made, and only by code.

**What M3 does not prove.** A strategy marked `candidate` means "the facts we have don't rule it out". It does not prove that a build will work on the phone. Only M4 (and later hardware testing) can show that.

## 1. Inputs, and checking that they belong together
- **Profile** (`profile-v1`, from M1): `--sim <fixture>`, or a saved profile file.
- **Research** (`research-v1`, from M2): `--research <file>`. Only the **typed facts** layer is read. Model notes and repo candidates are ignored. Simulated phones are invented, so each M1 fixture gets a matching **synthetic research file** in M3, with `provenance: synthetic` and labelled SIMULATED.
- **Selection:** `--services files`, `--services files,assistant`, and so on. Only `files` and `assistant` exist in M3. Anything else is invalid input.
- **Model catalog** (for the Assistant): a pinned local file listing candidate on-device models. Each entry has `{id, source, revision, files: [{name, bytes}], format, runtime, abi, licence}`. Every value has a source or is `unknown`. Real entries come from M2's `ai.candidates` or official model pages. Test entries are synthetic and labelled so. Whether Muse Glimmer can be an entry is still an open question, and its values stay `unknown` until checked.

**Checks before anything else runs** (all fail with exit 6, before any model call):
- Each input validates against its schema (`profile-v1`, `research-v1`, the catalog schema).
- The research file is about **the same phone** as the profile: its subject codename must equal the profile's `identity.device_codename`. A valid report for a different phone is refused.
- Provenance is kept as it is. A synthetic, replayed or live input keeps that label all the way into the plan.

## 2. Bootloader lock: a new inference rule
M1 left `boot.bootloader_locked` as `unknown` / `deferred`, because no official source documents the property it read. M3 adds an **inference rule** instead, `R-LOCK-FROM-VBS`, listed in `docs/inference-rules.md` with its source. AOSP's boot-flow documentation (https://source.android.com/docs/security/features/verifiedboot/boot-flow) defines the boot states: green and yellow mean the bootloader is locked, and orange means it's unlocked.

| `boot.verified_boot_state` | `boot.bootloader_locked` |
|---|---|
| `green` or `yellow` | `true`, status `inferred` |
| `orange` | `false`, status `inferred` |
| `red`, `unknown` or `conflicting` | stays `unknown` |

- The result keeps `status: inferred` and names the rule. It's never relabelled as measured.
- The rule **never overwrites** a value from another source. If another source gives a lock value that disagrees, the fact becomes `conflicting`, both pieces of evidence are kept, and it's treated as unknown.
- Muse quotes the exact documentation sentence and URL in `docs/inference-rules.md`. If it can't find one, the rule isn't added, and the lock stays `unknown`.

## 3. Strategy engine
Five strategies, each judged by fixed rules written as a table in `docs/strategy-rules.md`. Each rule names the fact IDs it reads.

### 3a. Unlock state (one answer only)
Code works out a single **unlock state**, checking these rows **in order** and stopping at the first match. Exactly one row always applies.

| Order | When | Unlock state | Meaning |
|---|---|---|---|
| 1 | The lock fact is `conflicting` | `unknown` | The evidence disagrees. Both pieces are shown |
| 2 | `bootloader_locked` is `false` | `already_unlocked` | No unlock step needed |
| 3 | Locked is `true`, `oem_unlock_supported` is `true`, `oem_unlock_allowed` is `true` | `allowed_now` | Unlocking is possible today |
| 4 | Locked is `true`, supported is `true`, allowed is `false` | `not_allowed_now` | Blocked **for now** (for example, the setting is off or a carrier lock applies). This may change |
| 5 | Locked isn't `false`, and supported is `false` | `no_official_path` | The phone reports no official unlock. Blocked, but labelled "no official path found", not "impossible forever" |
| 6 | Anything else | `unknown` | A needed fact is missing |

Strategies that need an unlocked bootloader treat `already_unlocked` and `allowed_now` as "unlock OK". `not_allowed_now` gives `blocked` with `blocker_kind: current`. `no_official_path` gives `blocked` with `blocker_kind: no_official_path`. `unknown` gives `unknown`.

### 3b. Strategy rules
Each strategy ends up as one of:
- `candidate`: the rules are met. It lists the fact IDs that met them **and the checks still open** (for example "vendor compatibility not checked").
- `blocked`: names the fact, its value and the blocker kind.
- `unknown`: names the missing or unproven facts. An `unknown` is **never** treated as a candidate.
- `not_covered`: M3 doesn't judge this strategy.

| Strategy | `candidate` when (all true) | `blocked` when (any true) | Otherwise `unknown`, including | Always listed as still open |
|---|---|---|---|---|
| `community_build` (e.g. a LineageOS device tree) | `lineage.support` is `current`; `repos.device_tree` has an established repo; unlock OK | Unlock blocked (3a) | LineageOS support is `historical_only` or `not_listed` (other community builds weren't checked, so this isn't proof it's impossible) | The tree still builds; the vendor files are available |
| `generic_system_image` (GSI) | `boot.treble_enabled` is `true`; unlock OK; `resources.cpu_abis` names an ABI that a GSI is published for | `treble_enabled` is `false`; unlock blocked | ABI unknown | Launch and vendor version compatibility (Android's GSI rules also check these, and M3 has no fact for them) |
| `linux` (postmarketOS-style) | `pmos.status` is `listed`; unlock OK | Unlock blocked | `pmos.status` is `not_found` (not being listed isn't proof a port can't exist) | A listed wiki page shows a page exists, not that the port works: which features work isn't checked |
| `stock_rebuild` | Never in M3 | Never | Never | Always `not_covered` (M2 doesn't research stock firmware) |
| `on_top_of_android` | `identity.sdk_level` is at least the app minimum; `resources.cpu_abis` includes an ABI the apps support | `identity.sdk_level` is below the app minimum | SDK or ABI unknown | The app modules don't exist yet (they're built in M4). The minimum Android version and ABIs are **planning estimates** in `docs/strategy-rules.md`, labelled so, until M4 sets them |

**Ranking:** candidates come first, in a fixed, documented order: community build, then GSI, then Linux, then on top of Android. `unknown` ones come next, then `blocked` ones (`current` blockers before `no_official_path`), then `not_covered`. Every strategy carries fixed, code-owned text for its **risks** (for example "unlocking wipes the phone's data" or "some GSI hardware features may not work") and its **signing implication** (for example "verified boot shows orange after unlocking; relocking needs your own signing key, if the phone supports it"). Each piece of text cites its source in `docs/strategy-rules.md`, or is labelled "StarGate's own guidance".

## 4. Fit engine
The requirements live in `docs/fit-budgets.md`, one row each, with a source or the label **"planning estimate"**. All sizes are whole bytes.

### 4a. Resource budgets for the whole selection
Memory and storage add up **every selected service**, not just one:
- **Memory needed** = OS baseline + Files app overhead (if Files is selected) + Assistant app overhead (if selected) + the model's total file bytes × runtime factor (if the Assistant is selected).
- **Storage needed** = Files budget (if Files is selected) + the Assistant app size and the model's total file bytes (both only if the Assistant is selected).

The baseline, overheads, factor and budgets are planning estimates unless a source is found.

### 4b. Per-check results
| Check | Phone fact | Requirement |
|---|---|---|
| Memory | `resources.ram_total` | At least "memory needed" |
| Storage | `resources.data_free` | At least "storage needed" |
| CPU (Assistant) | `resources.cpu_abis` | Includes the ABI the model's runtime needs |
| Kernel features | `kernel.config.*` | Only checked if a service in M3 needs one. Otherwise listed as "not needed yet" |

Each check gives `fits`, `does_not_fit` (with both numbers, in bytes and in readable units) or `unknown` (naming the missing fact). If any number in a check is a planning estimate, the check is labelled **"estimated"**.

### 4c. Choosing the Assistant's model
Code checks **each catalog model separately** against the checks above (with that model's bytes and ABI), then:
1. If one or more models **fit**, it picks the one with the **largest total file bytes**. Ties go to the alphabetically first `id`. The plan says why it was chosen.
2. If none fit but **some are unknown** (for example, their size is unknown), the Assistant is `unconfirmed` with **no chosen model**, and the unknown models are listed.
3. Only if **every** catalog model definitely **does not fit** is the Assistant `refused`, with each model's reason.
4. An **empty catalog** gives `unknown` ("no candidate models listed"), never a refusal. A missing value never counts as "too big".

### 4d. Selection result
- **`refused`** if any check (or the model choice) is definitely `does_not_fit`, with each reason. The CLI exits with code 7.
- **`unconfirmed`** if nothing fails but something is `unknown`. This allows planning and a clearly labelled **emulator experiment** only. It never claims the build will work on a real phone, and it never allows putting anything on a real phone.
- **`fits`** only if every applicable check is `fits`. If any are estimated, it says "fits (estimated)".

### 4e. Build checks for M4 (kept apart from the fit result)
- **Image size** (`capacity.system_image_max`): always `unknown` in M3, because M1 doesn't collect it. It's listed as "not checked yet" and passed to M4 as an unresolved check. It doesn't make the selection `unconfirmed` by itself, but it's always shown.

## 5. Meta explanation (optional, `--explain`)
One Meta call (`muse-spark-1.3`, `max_completion_tokens` 2048, one retry) receives the plan's decisions and fact IDs, and writes a short plain-English explanation of the risks for a non-specialist. It's stored as **model notes**, labelled "model explanation, not checked", exactly as in M2. Code checks that every fact ID it cites exists. The explanation never changes a status, a ranking or the selection result. Without `--explain`, M3 makes no network calls. The input checks in section 1 run **before** the Meta call, so invalid input never reaches the model.

## 6. `stargate plan`
```
stargate plan --sim <fixture> --services files,assistant [--research <file>] [--explain] [--json] [--json-out <file>]
```
- It prints a readable plan: the strategies in ranked order with status, reasons, open checks and risks; then the fit table; then the model choice; then the selection result; then the build checks for M4; then the labelled explanation.
- `--json` / `--json-out` give a validated **`plan-v1`** report with: `schema_version`, `subject`, `inputs` (the profile, research and catalog, each with its SHA-256 and provenance), `rules` (the SHA-256 of `docs/strategy-rules.md`, `docs/fit-budgets.md` and `docs/inference-rules.md`), `unlock_state`, `strategies`, `fit`, `selection_result`, `build_allowed`, `explanation_status`, `handoff`, `notes`, and `provenance`.
- **The handoff to M4**, a `handoff` block in `plan-v1`: the selected services; the chosen model (`id`, `source`, `revision`, each file's name and bytes, `format`, `runtime`, total bytes), or `null` with the reason; the candidate strategies in order; and every **unresolved check** (image size, the open checks from 3b, and any `unknown` fit check). The handoff also carries the **decision itself**, so it can never be read without it:
  - `selection_result` (`fits`, `unconfirmed` or `refused`) and every refusal reason;
  - `build_allowed`: `emulator_only` for `fits` and `unconfirmed`, and `none` for `refused`. In M3 nothing is ever allowed onto a real phone;
  - the provenance of each input (live, replay or synthetic).

**M4's rule for using a plan:** M4 first validates the **whole** `plan-v1` file against its schema, then checks that the handoff's `selection_result` and `build_allowed` match the top-level ones. It starts a build only if `build_allowed` is `emulator_only`. A refused plan, a plan that fails validation, or a handoff that disagrees with the rest of the plan stops M4 before any build step. M4's spec will repeat this rule and test it.

**Exit codes, in priority order** (the first that applies wins):
1. **6**: invalid input (schema, wrong phone, unknown service). Checked before any model call.
2. **7**: the selection is refused. This wins even if `--explain` also failed.
3. **2 or 5**: only when `--explain` was asked for, the selection is not refused, and the Meta call failed (M0's codes).
4. **0**: the plan is `fits` or `unconfirmed`.

Whenever `--explain` fails, `explanation_status` records it (`failed` with the M0 code), and the plan itself is still printed and saved.

## 7. Tests (offline)
- **The inference rule:** every row of the table in section 2, including that `red` and `unknown` don't become locked or unlocked, the result keeps `status: inferred`, and a disagreeing value from another source gives `conflicting` with both kept.
- **Unlock state:** every row of the 3a table, and that exactly one row applies. These include `locked=false, supported=false` (gives `already_unlocked`, not both) and `locked=true, supported=true, allowed=false` (gives `not_allowed_now`, blocked for now).
- **Strategies:** each rule in 3b has a test for candidate, blocked and unknown. `historical_only`/`not_listed` and `pmos not_found` give `unknown`, not `blocked`. GSI with an unknown ABI is `unknown`. Every candidate lists its open checks. `stock_rebuild` is always `not_covered`.
- **Two different phones give different rankings:** for example `flagship` (Treble, 64-bit, current LineageOS support in its synthetic research) against `old32`.
- **Input checks:** a valid research file for a different phone gives exit 6. An invalid schema gives exit 6. Both happen before any model call (the recorded-response stub is never reached). Synthetic and replay provenance appear unchanged in `plan-v1`.
- **Model choice:** one fits, so it's chosen; two fit, so the larger is chosen; a tie goes to the first `id`. None fit but one is unknown gives `unconfirmed` with no model. All definitely fail gives `refused`. An empty catalog gives `unknown`.
- **Refusals:** `old32` with the Assistant is refused when every catalog model needs a 64-bit ABI. `budget` with the Assistant is refused when RAM is below every model's need. Each refusal names the fact and both numbers. Selecting Files and the Assistant together needs more memory and storage than the Assistant alone.
- **Unknowns:** a missing fact gives `unconfirmed`, never `fits`. Image size is always listed as unresolved in the handoff.
- **Exit precedence:** refused plus a failed `--explain` gives 7, with `explanation_status: failed`. Not refused plus a failed `--explain` gives 2 or 5.
- **Handoff:** `fits` and `unconfirmed` plans have a complete `handoff` block, the chosen model's files and bytes match the catalog, and the rule-file hashes match the docs. **A Files-only pair:** the same phone with enough storage and with too little storage gives one plan with `build_allowed: emulator_only` and one with `selection_result: refused`, `build_allowed: none` and the storage reason, both inside the handoff. The two handoffs are not equal. The schema rejects a plan whose handoff `selection_result` or `build_allowed` disagrees with the top level, or that pairs `refused` with `emulator_only`.
- **The model can't change decisions:** a recorded model response claiming "this phone can run GSI" leaves the GSI status unchanged. A note citing a missing fact ID is flagged.
- **Research layers:** repo candidates and model notes in the research file are ignored, and only typed facts are read.
- **Bytes:** sizes are compared in whole bytes. A value like "2 GB" in a requirement file is rejected.
- **CLI and schema:** exit codes, `--json` parsed from real stdout, and valid and invalid `plan-v1` examples.
- **Network:** the full suite runs with sockets blocked. The `--explain` tests use recorded responses.

## Done when
- [ ] `R-LOCK-FROM-VBS` is documented with its official source and tested, or reported as not found (with the lock left `unknown`).
- [ ] `docs/strategy-rules.md`, `docs/fit-budgets.md` and `docs/inference-rules.md` exist, every number has a source or is labelled "planning estimate", and every risk and signing text is cited or labelled.
- [ ] `stargate plan --sim flagship --services files,assistant` and `stargate plan --sim old32 --services files,assistant` give clearly different rankings, and the second refuses the Assistant with a reason (exit 7).
- [ ] `--json-out` validates against `plan-v1` for all four fixtures with `--services files`, and each has a `handoff` block.
- [ ] One live `--explain` run on `flagship` shows a labelled explanation, and every fact ID it cites exists.
- [ ] All tests pass offline (count above zero), and `stargate doctor` still passes.
- [ ] No installs, one checkpoint commit, nothing pushed, and the reviewer Muse checks the commit before M4.

## Out of scope
Building anything (M4), real phones, research beyond what M2 saved, the Files and Assistant apps themselves, and any new Meta model besides `muse-spark-1.3` for explanations.

## Network use allowed in M3
- **Product runs:** `stargate plan` makes no network calls unless `--explain` is used. Validation allows **one** live `--explain` run and **one** `stargate doctor` regression run.
- **Development reads (Muse, while writing the docs):** at most **15** read-only fetches of official pages, to find the citations for the inference rule, the strategy rules and the catalog entries. Allowed hosts are `source.android.com`, `developer.android.com`, `wiki.lineageos.org`, `wiki.postmarketos.org`, `wiki.nura.eco` and `huggingface.co`. Each URL fetched is listed in `docs/m3-sources.md`, with the date. No downloads of models or images, and no other hosts.
- Nothing else.

## Demo (under 5 minutes)
```
.venv/bin/stargate plan --sim flagship --services files,assistant; echo "flagship exit $?"
.venv/bin/stargate plan --sim old32 --services files,assistant; echo "old32 exit $? (expect 7)"
.venv/bin/stargate plan --sim flagship --services files,assistant --explain --json-out /tmp/p.json; echo "explain exit $?"
.venv/bin/python -m stargate.plan validate /tmp/p.json; echo "validate exit $?"
.venv/bin/python -m unittest; echo "tests exit $?"
```
