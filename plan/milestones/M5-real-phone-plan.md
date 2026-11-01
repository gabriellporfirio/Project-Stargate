# M5: Real-phone install plan, drafted by a Meta model and checked by code (spec)

Status: v2, 1 Nov 2026, for review. v2 fixes ChatGPT's review of v1 ([night batch, item 1](../../reviews/2026-11-01-chatgpt-night-batch-pr34.md)): code now walks the draft step by step with an explicit phone state, partitions are a closed list, unknown facts stop the plan, the profile is bound to the plan by hash, citations are tied to rules, the second source uses its canonical address, and replay equality is defined. Builds on M1 (profiles), M2 (fetch boundary and report layers), M3 (`plan-v1`) and M4 (the emulator image). It carries the owner's demo requirement from master-plan section 7 (1 Nov): **a Meta model visibly makes a real, useful decision, and code checks it before it counts.**

## Goal
For one phone profile and its accepted M3 plan, StarGate writes a **limited install-routing proposal**: the order of the unlock, reboot and flash steps a person would follow to put the image on that real phone. A Meta model drafts the steps from official Android pages that code has fetched. Code then checks every step against the phone's facts and the fetched pages, and rejects any draft that breaks a rule.

**What it is not.** It isn't a validated install procedure for any handset. Whether the image suits the phone, signing and verified-boot (vbmeta) handling, A/B slot choice and every other M7 prerequisite stay unresolved, and the plan lists them as unresolved every time.

The plan is a document. **Nothing in M5 runs on a phone**: no adb, fastboot or flashing commands are executed, and the plan says "not run" at the top. The demo still boots the image in the Android Emulator (M4), and the screen says so.

**Why this decision.** Generic install guides often say "flash the system image from the bootloader". On a phone with dynamic partitions, Android's own documentation says that doesn't work. The model has to notice this from the phone's facts and the source, and change the steps. Code then confirms the change against a fixed rule, and a viewer can open the source. (Idea from Grok's review, picked by the owner on 1 Nov.)

## 1. Inputs
- **Profile** (`profile-v1`, M1): `--sim <fixture>` or a saved profile. Simulated profiles keep their SIMULATED label everywhere, including on screen.
- **Plan** (`plan-v1`, M3): validated in full, as M4 does. M5 runs only if `build_allowed` is `emulator_only`. **The profile is bound to the plan by hash:** the SHA-256 of the supplied profile must equal the profile hash recorded in the plan's `inputs`. A different profile for the same phone name exits 6. A refused plan exits 7.
- **Starting steps** (`docs/generic-install-steps.md`, checked into the product repo): a short, fixed list of the usual generic steps (reboot to bootloader, unlock, flash system from the bootloader, wipe, reboot). It's labelled "generic starting steps, not specific to any phone". The model edits this list for the phone. On screen, the steps it removes are shown crossed out and the steps it adds are highlighted.
- **Sources:** fetched by code only, through M2's fetch boundary. M5 adds **one host** to the allowlist, `source.android.com`, GET only and HTTPS only, with **exactly these canonical pages**:
  - `/docs/core/architecture/bootloader/fastbootd` ("Move fastboot to userspace": fastbootd and dynamic partitions)
  - `/docs/setup/test/running` ("Flash with Fastboot": unlocking the bootloader, and OEM unlocking). The old address `/docs/setup/build/running` redirects here (checked 1 Nov), so M5 requests the canonical one directly.

  **Redirects:** a response whose final URL isn't exactly the requested canonical URL fails that fetch (outcome `refused`). Every request, including a redirect hop, counts toward the budget of 2. M2's other limits apply (10 s, 1 MiB, the 24-hour cache, page content treated as untrusted data). The fetch records (requested URL, final URL, status, SHA-256) are written into the plan.

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
| `check_is_logical` | a partition from the closed list |
| `stop_for_check` | none: the plan ends here, because what comes next depends on a check the plan can't know the answer to |
| `flash` | a partition from the closed list, and a mode, `bootloader` or `fastbootd` |
| `wipe_data` | none |
| `reboot_system` | none |

**Closed partition list:** `system` only. StarGate's image replaces the system partition, and nothing else is flashed in M5. Any other partition name rejects the draft.

Each step has a short plain-English reason, plus a **citation**: a fetch record ID, an **exact, non-empty quote** from that page, and the ID of the rule it relies on (section 3). Each change from the starting steps (removed, added or changed) has its own reason and citation. The model may also return `do_not_install`, with a reason and citation.

The model cannot write free-text commands, change a fact, change M3's selection or `build_allowed`, or edit an image. Its output is stored as **model notes** (M2 3c) until code accepts it.

## 3. What code checks (the accept or reject rules)
Every rule lives in `docs/install-rules.md`, with the fact IDs it reads and its **anchor quote**: the exact sentence from one of the two pages that justifies the rule, fixed by us, and checked to exist in the fetched page on every run (if it's missing, the run stops with exit 6, because the source changed). A draft is **accepted** only if every rule passes.

**Code walks the draft step by step with an explicit phone state:** the current mode (`system`, `bootloader` or `fastbootd`), whether the bootloader is known to be unlocked, whether OEM unlocking was checked, and whether the erase warning was given. It starts from the profile: mode `system`; unlocked only if `boot.bootloader_locked` is `false` (measured or inferred). Each step must be allowed in the current state, and then changes it:

| Step | Allowed only when | Then |
|---|---|---|
| `check_oem_unlocking` | mode `system` | OEM unlocking was checked |
| `reboot_bootloader` | mode `system` | mode `bootloader` |
| `unlock_bootloader` | mode `bootloader`, OEM unlocking checked, the erase warning already given, and the phone not already unlocked | unlocked |
| `reboot_fastbootd` | mode `bootloader` and unlocked | mode `fastbootd` |
| `check_is_logical` | mode `bootloader` or `fastbootd` | the next step must be `stop_for_check` |
| `stop_for_check` | directly after `check_is_logical` | the plan ends; result `unconfirmed` |
| `flash` | unlocked, and the step's mode equals the current mode | (no change) |
| `wipe_data` | mode `bootloader` or `fastbootd`, and unlocked | (no change) |
| `reboot_system` | the last step | mode `system` |

So "flash, then unlock" fails: flashing needs the unlocked state, which only `unlock_bootloader` (or an already-unlocked profile) gives. Android's fastbootd page also says flashing needs an unlocked device.

| Rule | Check |
|---|---|
| `I-FORMAT` | The reply parses against `install-draft-v1`, and the provider says it finished normally (`finish_reason` `stop`). A truncated, malformed or non-stop reply is a rejected draft, never repaired by code |
| `I-QUOTE` | Every quote is non-empty and appears **word for word** in the page its record names (after whitespace is normalised). Each step cites the rule it relies on, and for `unlock_bootloader`, `reboot_fastbootd`, `flash` and the erase warning, the quote must be that rule's anchor quote |
| `I-TYPES` | Only the step types above, and only partitions from the closed list |
| `I-STATE` | Every step passes the state table above |
| `I-DYNAMIC` | If `boot.dynamic_partitions` is `true`: `flash system` must use mode `fastbootd`. If `false`: mode `bootloader`. Anchor: the fastbootd page's sentence that the bootloader must not allow flashing dynamic partitions |
| `I-UNKNOWN` | If `boot.dynamic_partitions` is `unknown` or `conflicting`, the plan must not contain `flash`. It must stop with `check_is_logical system` then `stop_for_check`, and the result is `unconfirmed`. The same applies if `boot.bootloader_locked` is `unknown` or `conflicting`: the plan stops after `check_oem_unlocking` with `stop_for_check`'s explanation, and the result is `unconfirmed` |
| `I-UNLOCK` | If the phone is already unlocked (`boot.bootloader_locked` is `false`), the plan must not contain `unlock_bootloader`, and it is valid even when `boot.oem_unlock_supported` is `false` (M3's already-unlocked case). If the phone is locked and `boot.oem_unlock_supported` is `false`, only `do_not_install` is accepted. If it's locked and `boot.oem_unlock_allowed` isn't `true`, the plan must say unlocking may be unavailable, quoting the source's advice, and never claim it is allowed |
| `I-WIPE` | Before `unlock_bootloader`, the plan warns that unlocking erases the phone, quoting the "Flash with Fastboot" page's sentence ("For privacy reasons, unlocking the bootloader deletes user data.") |

**Unresolved, always listed:** image compatibility with this phone, signing and verified boot, the A/B slot to flash, and the M7 prerequisites. No rule can resolve them in M5.

**Repair round.** If the draft is rejected (including by `I-FORMAT`), code sends the model the failed rule IDs and their plain-English reasons once, and asks for a new draft. If the second draft also fails, M5 exits 10 and shows both drafts with the failed rules. Code never fixes a draft itself, and never falls back to a hand-written plan.

**What counts as the visible decision.** These are the model's edits to the generic starting steps, each shown with its source quote and the rule that confirmed it. If the model's first draft is rejected, that rejection is shown too, because it happened. A rejection is never staged. `do_not_install`, `unconfirmed` and `no_valid_plan` are real outcomes to show as they are: a run is never repeated to get a nicer screenshot.

## 4. Output: `install-plan-v1`
- `subject`, `inputs` (profile, plan, starting steps and pages, each with SHA-256 and provenance), `fetch_records`, `facts_used` (ID, value, status), `drafts` (each draft, with its rule results), `accepted_steps` or `null`, `result` (`accepted`, `unconfirmed`, `do_not_install` or `no_valid_plan`), `unresolved` (the list in section 3), `runs: "never"`, `provenance` (`live`, `replay` or `synthetic`), and `model` (ID and provider).
- A readable view shows: "Install-routing proposal: not a validated install procedure"; the phone (with the SIMULATED label when it applies); the starting steps with the model's edits (crossed out, added); each edit's quote and a link to the page; each rule's result; and "Install plan only: not run on any phone. The demo boots this image in the Android Emulator."

## 5. CLI
```
stargate install-plan --sim flagship --plan plan.json [--record trace.json | --replay trace.json] [--json-out install-plan.json]
```
`--record` and `--replay` work as in M2, so the video can come from one live run. A replay makes **no** network request, starts no process and touches no device, and its output and readable view say "Replay of a live run on <date>".

**Replay equality.** A replay matches its live run when the **decision payload** is identical: `subject`, every input's SHA-256, each fetch record's requested URL, final URL, status and SHA-256, `facts_used`, every draft and its rule results, `accepted_steps`, `result`, `unresolved` and `model`. Only these may differ: `provenance` (`live` or `replay`), timestamps, durations, and cache-hit flags. A test compares exactly this.

**Exit codes, in priority order:** 6 invalid input; 7 refused plan, or unlock not supported (with `do_not_install` shown); 2 or 5 Meta key missing or call failed (M0 codes); 10 no valid draft after the repair round; 0 `accepted` or `unconfirmed`.

**Budget:** at most 3 Meta calls per run (the draft, one repair, one network retry), `max_completion_tokens` 4096 each (2048 was cut short in earlier runs), input capped at 24,000 characters of page text, 2 page requests (redirects included), 60 s per run. **For the owner's live runs in total:** at most two runs (one per demo profile), so at most 6 Meta calls and 4 page requests. Replays use none.

## 6. Which Meta model makes the decision (owner chose `muse-spark-1.3`, 1 Nov)
- **Chosen: `muse-spark-1.3` on the Meta API** (owner, 1 Nov 19:50). It's the same key and route as M2 and M3, whether it returns reliable JSON is recorded in M2's spike notes (`docs/m2-spike.md`, Q14; still marked open in the master plan, so Muse reads the spike result first, and if JSON isn't reliable, code parses and validates plain text against the same schema), and it counts for Meta tooling. Spend comes from the existing Meta allowance.
- Not chosen: Muse Spark Open on Baseten. It counts for the open-weight bonus, which the Assistant's cloud mode (M4c) is planned to show on camera (its live proof is still pending), and the Baseten budget is small (M4c: 5 attempts, $5 recorded).

Muse builds behind a provider interface and tests with a fake model. Only `muse-spark-1.3` gets a live run.

## 7. Tests (offline, with a fake model)
- Each rule in section 3 passes and fails on purpose, including:
  - "check OEM unlocking, flash, then unlock" on a locked phone (rejected by `I-STATE`);
  - a bootloader-mode `flash system` on a dynamic-partition phone (rejected);
  - `flash vendor` or any partition outside the closed list (rejected);
  - a quote changed by one word, an empty quote, or a step citing the wrong rule (rejected);
  - a truncated or malformed reply, or `finish_reason` other than `stop` (rejected by `I-FORMAT`);
  - dynamic partitions unknown: only "check, then stop", result `unconfirmed`; a `flash` after `check_is_logical` is rejected;
  - locked with unlock not supported: only `do_not_install`; already unlocked with unlock not supported: an install plan without `unlock_bootloader` is accepted;
  - a profile whose SHA-256 differs from the plan's recorded profile hash (exit 6).
- The repair round: first draft rejected, second accepted. Both drafts rejected gives exit 10, with no fallback plan.
- Two profiles give different accepted plans: `flagship` (dynamic partitions: fastbootd) and one named profile whose fixture really has `boot.dynamic_partitions` `false` and whose M3 plan isn't refused (Muse checks `old32` first and names the one it uses; fixtures are never edited).
- The fetch boundary: only the two canonical paths; a redirect to anywhere else fails the fetch; the request budget counts redirect hops; page text containing instructions doesn't change the rules; a missing anchor quote stops the run.
- No adb, fastboot or other device command is ever started: the device transport stays M1's stub, and a test checks that no process is spawned.
- Replay: the decision payload equals the recorded run's, only the listed fields differ, and replay makes zero network requests.

## Done when
- `stargate install-plan` for `flagship` and for the named second profile produce different, cited results from a live run (or a replay of one), shown in the readable view, whatever the outcomes are.
- All rules and tests in sections 3 and 7 pass, and the full existing suite still passes.

## Out of scope (hackathon cut line)
The rest of the original M5 (base source, kernel, partition sizes and signing steps for a real build) stays a plan for later. No real-phone build or install runs, and no Linux build machine is used (Q6). Running these steps on a phone is M7, and only with the owner's explicit approval.

## Demo (about 20 seconds of video)
The flagship (SIMULATED) profile shows "Dynamic partitions: yes". Then the generic step "flash system from the bootloader" is crossed out, "reboot to fastbootd, then flash" is added, Android's quote and link appear, and the rules `I-STATE` and `I-DYNAMIC` show as passed. One line says: "Install-routing proposal only, not run. This demo boots the image in the Android Emulator."
