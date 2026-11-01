# M5: Real-phone install plan, drafted by a Meta model and checked by code (spec)

Status: v1, 1 Nov 2026, for review. Builds on M1 (profiles), M2 (fetch boundary and report layers), M3 (`plan-v1`) and M4 (the emulator image). It carries the owner's demo requirement from master-plan section 7 (1 Nov): **a Meta model visibly makes a real, useful decision, and code checks it before it counts.**

## Goal
For one phone profile and its accepted M3 plan, StarGate writes the **steps a person would follow to install the image on that real phone**. A Meta model drafts the steps from official Android pages that code has fetched. Code then checks every step against the phone's facts and the fetched pages, and rejects any draft that breaks a rule.

The plan is a document. **Nothing in M5 runs on a phone**: no adb, fastboot or flashing commands are executed, and the plan says "not run" at the top. The demo still boots the image in the Android Emulator (M4), and the screen says so.

**Why this decision.** Generic install guides often say "flash the system image from the bootloader". On a phone with dynamic partitions, Android's own documentation says that doesn't work. The model has to notice this from the phone's facts and the source, and change the steps. Code then confirms the change against a fixed rule, and a viewer can open the source. (Idea from Grok's review, picked by the owner on 1 Nov.)

## 1. Inputs
- **Profile** (`profile-v1`, M1): `--sim <fixture>` or a saved profile. Simulated profiles keep their SIMULATED label everywhere, including on screen.
- **Plan** (`plan-v1`, M3): validated in full, as M4 does. M5 runs only if `build_allowed` is `emulator_only` and the plan is about the same phone as the profile. Otherwise it exits 6 (bad input) or 7 (refused plan).
- **Starting steps** (`docs/generic-install-steps.md`, checked into the product repo): a short, fixed list of the usual generic steps (reboot to bootloader, unlock, flash system from the bootloader, wipe, reboot). It's labelled "generic starting steps, not specific to any phone". The model edits this list for the phone. On screen, the steps it removes are shown crossed out and the steps it adds are highlighted.
- **Sources:** fetched by code only, through M2's fetch boundary. M5 adds **one host** to the allowlist, `source.android.com`, GET only and HTTPS only, with **exactly these pages**:
  - `/docs/core/architecture/bootloader/fastbootd` (fastbootd and dynamic partitions)
  - `/docs/setup/build/running` (unlocking the bootloader, and OEM unlocking)

  M2's limits apply (10 s, 1 MiB, the 24-hour cache, page content treated as untrusted data). The fetch records are written into the plan.

## 2. What the model may propose
One Meta call (model chosen in section 6) receives:
- the profile facts listed below, with their status (`measured`, `inferred`, `unknown` or `conflicting`);
- the generic starting steps;
- the fetched pages, clearly marked as data.

The facts sent are `identity.manufacturer`, `identity.model`, `identity.device_codename`, `identity.android_release`, `boot.bootloader_locked`, `boot.oem_unlock_supported`, `boot.oem_unlock_allowed`, `boot.ab_slots` and `boot.dynamic_partitions`. These are the same fields M2 may send, plus boot facts. No serials or other identifiers are sent.

The model returns JSON (`install-draft-v1`). It holds an ordered list of steps, each picked from a **closed set of step types**:

| Step type | Arguments |
|---|---|
| `reboot_bootloader` | none |
| `check_oem_unlocking` | none (a manual check in Settings, with the source's advice if the switch is unavailable) |
| `unlock_bootloader` | none |
| `reboot_fastbootd` | none |
| `check_is_logical` | a partition name |
| `flash` | a partition name and a mode, `bootloader` or `fastbootd` |
| `wipe_data` | none |
| `reboot_system` | none |

Each step has a short plain-English reason, plus a **citation**: a fetch record ID and an **exact quote** from that page. Each change from the starting steps (removed, added or changed) has its own reason and citation. The model may also return `do_not_install`, with a reason and citation.

The model cannot write free-text commands, change a fact, change M3's selection or `build_allowed`, or edit an image. Its output is stored as **model notes** (M2 3c) until code accepts it.

## 3. What code checks (the accept or reject rules)
Every rule lives in `docs/install-rules.md`, with the fact IDs it reads and its source quote. A draft is **accepted** only if every rule passes.

| Rule | Check |
|---|---|
| `I-QUOTE` | Every quote appears **word for word** in the fetched page its record names (after whitespace is normalised). A missing or altered quote rejects the draft |
| `I-TYPES` | Only the step types above, with valid arguments. Anything else rejects the draft |
| `I-DYNAMIC` | If `boot.dynamic_partitions` is `true`, no `flash` of `system`, `vendor` or `product` may use mode `bootloader`. Those flashes must come after `reboot_fastbootd`. Source: the fastbootd page says the bootloader must not allow flashing dynamic partitions, and must return an error |
| `I-DYNAMIC-UNKNOWN` | If `boot.dynamic_partitions` is `unknown` or `conflicting`, each `flash` of those partitions must come after a `check_is_logical` step for that partition. The plan is then marked **unconfirmed** |
| `I-UNLOCK` | If `boot.oem_unlock_supported` is `false`, only `do_not_install` is accepted. If `boot.bootloader_locked` is `true`, `unlock_bootloader` must come after `check_oem_unlocking`. If `boot.oem_unlock_allowed` isn't `true`, the plan must say unlocking may be unavailable, with the source's advice, and never claim it is allowed |
| `I-WIPE` | Any plan with `unlock_bootloader` must warn that unlocking erases the phone, before that step |
| `I-ORDER` | `reboot_bootloader` comes before any bootloader step, and `reboot_system` comes last |

**Repair round.** If the draft is rejected, code sends the model the failed rule IDs and their plain-English reasons once, and asks for a new draft. If the second draft also fails, M5 exits 10 and shows both drafts with the failed rules. Code never fixes a draft itself, and never falls back to a hand-written plan.

**What counts as the visible decision.** These are the model's edits to the generic starting steps, each shown with its source quote and the rule that confirmed it. If the model's first draft is rejected, that rejection is shown too, because it happened. A rejection is never staged.

## 4. Output: `install-plan-v1`
- `subject`, `inputs` (profile, plan, starting steps and pages, each with SHA-256 and provenance), `fetch_records`, `facts_used` (ID, value, status), `drafts` (each draft, with its rule results), `accepted_steps` or `null`, `result` (`accepted`, `unconfirmed`, `do_not_install` or `no_valid_plan`), `runs: "never"`, `provenance` (`live`, `replay` or `synthetic`), and `model` (ID and provider).
- A readable view shows: the phone (with the SIMULATED label when it applies); the starting steps with the model's edits (crossed out, added); each edit's quote and a link to the page; each rule's result; and "Install plan only: not run on any phone. The demo boots this image in the Android Emulator."

## 5. CLI
```
stargate install-plan --sim flagship --plan plan.json [--record trace.json | --replay trace.json] [--json-out install-plan.json]
```
`--record` and `--replay` work as in M2, so the video can come from one live run. A replay never calls the network, and its output says `provenance: replay`.

**Exit codes, in priority order:** 6 invalid input; 7 refused plan, or unlock not supported (with `do_not_install` shown); 2 or 5 Meta key missing or call failed (M0 codes); 10 no valid draft after the repair round; 0 `accepted` or `unconfirmed`.

**Budget:** at most 3 Meta calls per run (the draft, one repair, one network retry), `max_completion_tokens` 2048 each, input capped at 24,000 characters of page text, 2 page fetches, 60 s per run.

## 6. Which Meta model makes the decision (open, owner's call)
- **Recommended: `muse-spark-1.3` on the Meta API.** It's the same key and route as M2 and M3, whether it returns reliable JSON is recorded in M2's spike notes (`docs/m2-spike.md`, Q14; still marked open in the master plan, so Muse reads the spike result first, and if JSON isn't reliable, code parses and validates plain text against the same schema), and it counts for Meta tooling. Spend comes from the existing Meta allowance.
- Alternative: Muse Spark Open on Baseten. It counts for the open-weight bonus, but the Assistant's cloud mode (M4c) already shows Spark Open on camera, and the Baseten budget is small (M4c: 5 attempts, $5 recorded).

Until the owner picks, Muse builds with a provider interface and tests with a fake model. Only the chosen model gets a live run.

## 7. Tests (offline, with a fake model)
- Each rule in section 3 passes and fails on purpose, including: a bootloader-mode `flash system` on a dynamic-partition phone (rejected); a quote changed by one word (rejected); an unknown step type (rejected); unlock not supported (only `do_not_install` accepted); dynamic partitions unknown (needs `check_is_logical`, result `unconfirmed`).
- The repair round: first draft rejected, second accepted. Both drafts rejected gives exit 10, with no fallback plan.
- Two profiles give different accepted plans: `flagship` (dynamic partitions: fastbootd steps) and `old32` (no dynamic partitions: bootloader flash allowed).
- The fetch boundary refuses any other `source.android.com` path, and page text containing instructions doesn't change the rules.
- No adb, fastboot or other device command is ever started: the device transport stays M1's stub, and a test checks that no process is spawned.
- Replay produces the same `install-plan-v1` as the recorded run, with no network.

## Done when
- `stargate install-plan --sim flagship` and `--sim old32` produce different, accepted, cited plans from a live run (or a replay of one), shown in the readable view.
- All rules and tests in sections 3 and 7 pass, and the full existing suite still passes.
- The owner has picked the model in section 6.

## Out of scope (hackathon cut line)
The rest of the original M5 (base source, kernel, partition sizes and signing steps for a real build) stays a plan for later. No real-phone build or install runs, and no Linux build machine is used (Q6). Running these steps on a phone is M7, and only with the owner's explicit approval.

## Demo (about 20 seconds of video)
The flagship (SIMULATED) profile shows "Dynamic partitions: yes". Then the generic step "flash system from the bootloader" is crossed out, "reboot to fastbootd, then flash" is added, Android's quote and link appear, and the rule `I-DYNAMIC` shows as passed. One line says: "Install plan only. This demo boots the image in the Android Emulator."
