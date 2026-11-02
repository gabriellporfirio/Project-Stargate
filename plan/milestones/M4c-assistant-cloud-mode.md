# M4c: Assistant cloud mode (spec)

Status: v2.5, 2 Nov 2026 (revised after GPT's review the same day: an owner-run preflight for the development attempt limit, clearer retry rules, test fixes). v2.5 follows the owner's decision that users bring their own key and the app never tracks money: prices, dollar limits and cost reservations are removed, and the per-request caps and a small attempt log for our own development stay (section 6). v2.4, 1 Nov 2026. v2.4 separates what the ledger limits (recorded and reserved costs) from what providers actually charge ([ChatGPT's re-review of v2.3](../../reviews/2026-11-01-chatgpt-m4c-assistant-cloud-mode-v2.3.md)). v2.2 replaced the characters-equal-tokens guess with byte caps and a token ceiling ([ChatGPT's re-review of v2.1](../../reviews/2026-11-01-chatgpt-m4c-assistant-cloud-mode-v2.1.md)). v2.3 fixes that ceiling's arithmetic and says plainly that it's a conservative estimate, not a guarantee ([ChatGPT's re-review of v2.2](../../reviews/2026-11-01-chatgpt-m4c-assistant-cloud-mode-v2.2.md)). v2 folded in [ChatGPT's review of v1](../../reviews/2026-11-01-chatgpt-m4c-assistant-cloud-mode.md) (four must-fix, one should-fix). v2.1 folds in [ChatGPT's re-review of v2](../../reviews/2026-11-01-chatgpt-m4c-assistant-cloud-mode-v2.md): one shared budget ledger with reserve-before-send (section 6), a Keystore-failure test and a real per-package backup check (sections 7 and 8). It follows the owner's direction on 1 Nov: the phone is limited by its hardware, so the Assistant offers a small local model **and** cloud models, the way a model picker lists several providers.

**Time-box:** at most **4 hours** of Muse work, started only after M4's local Assistant answers in the emulator. M4c never holds up M4, M5, M6 or the recorded core demo. If it runs out of time, it's reported as partial or blocked (section 9).

## Why
- **For the user:** the phone runs a small model offline, and hands harder questions to a bigger Meta model in the cloud.
- **For the hackathon:** the open-weight bonus counts only Muse Glimmer or Muse Spark Open, "served on participants' own hardware or through partner-provided inference" ([participant guide](../../docs/participant-guide-excerpt.md)). Muse Glimmer has 30B parameters, and its [model card](https://huggingface.co/meta-models/Muse-Glimmer-30B) lists 24–32 GB deployment targets, far outside the approved demo budget (a 6 GB emulator on a 16 GB Mac). Muse Spark Open through partner inference is the realistic route.
- **The local model** is the one M4b chose: ExecuTorch 1.5.1 running Llama 3.2 1B on a 6 GB emulator (master plan section 7, 1 Nov; evidence in the product repo's `docs/m4-assistant.md` on branch `m4b-assistant`, commits e5ef6ce to 31512ba).

## 1. The three Assistant modes
| Mode | Model | Provider | Key |
|---|---|---|---|
| **Local** (default) | the model the plan's handoff names | on the phone, no network | none |
| **Meta** | `muse-spark-1.3` by default; the user may type another Meta model ID | Meta Model API | the user's Meta key |
| **Meta open-weight** | exactly `meta-models/muse-spark-open-1026`, fixed | Baseten (partner inference) | the user's Baseten key |

The Assistant's settings have one **Model** drop-down with these three entries. The user picks a provider from the list and never types a web address. A custom provider is a later idea, out of scope here. The screen always shows which mode and model answered.

**How the modes are explained (owner, 2 Nov).** Short, fixed text in the app:
- **On this phone:** "Picked to fit your phone. Works offline."
- **Meta cloud** and **Meta open-weight:** "Uses your own API key. Your provider's terms and usage limits apply." followed by the provider's name (Meta or Baseten) linked to its terms page. The same line appears on the screen where the key is entered.

The links are fixed in the app. The app never reads or shows prices.

## 2. Keys (Q16 answered)
[Meta's model catalog](https://dev.meta.ai/docs/models) says Muse Spark Open isn't served through the Meta Model API (cited in ChatGPT's review, 1 Nov). So:
- StarGate **needs** only the user's Meta key. Local and Meta modes work with nothing else.
- The **Meta open-weight** mode is **optional** and needs a Baseten key the user adds. For the demo, that's the owner's hackathon Baseten key. The hackathon email says: "Use exactly meta-models/muse-spark-open-1026. Your key only works with this hackathon model."
- This replaces the earlier rule that Baseten is development-only (Q3): Baseten is now an optional, user-supplied partner provider inside the Assistant, and nowhere else.

## 3. Providers, pinned
| | Meta | Baseten |
|---|---|---|
| Endpoint | `POST https://api.meta.ai/v1/chat/completions` (Q2, live in M0) | `POST https://inference.baseten.co/v1/chat/completions` ([Baseten docs](https://docs.baseten.co/reference/inference-api/chat-completions)) |
| Authentication | `Authorization: Bearer <Meta key>` | `Authorization: Bearer <Baseten key>` |
| Request | `model`, `messages` (one user message), `max_completion_tokens` | `model`, `messages` (one user message), `max_tokens` |
| Response used | first choice's message text, `finish_reason`, `usage` | the same fields |

- **Credential routing:** each key has its own slot and is only ever sent to its own provider's host. The request builder takes a provider, and the key comes from that provider's slot, never from a shared variable (tested with two dummy keys).
- **Redirects are refused,** not followed. TLS certificate checks stay on, with no custom trust settings.
- **Errors** show a short message, the provider and the HTTP status, never the response body or headers:

| Case | What the user sees | Retry? |
|---|---|---|
| 401 or 403 | "Key rejected by <provider>" | no |
| 402 or a billing error | "<provider> account needs payment" | no |
| 400 or 404 naming the model | "Model not available" | no |
| 429 | "Too many requests, try later" | once, after the provider's wait time. If the provider asks for more than 10 s, no retry: it shows "try later" and never retries sooner than asked |
| 5xx or timeout | "<provider> not reachable" | once |
| Empty or malformed reply | "No usable answer" | no |
| `finish_reason` other than `stop` | the text, labelled "incomplete" | no |

No case ever switches to another model or provider by itself.

## 4. The Assistant APK: two variants
A library module can't hold a permission on its own, because Android merges library manifests into the app's manifest. So the Assistant is built as **two variants of the same package** `com.stargate.assistant`, and a build contains exactly one:
- **Local variant** (M4b's APK): requests **no** permissions.
- **Cloud variant:** requests exactly one permission, `android.permission.INTERNET`, and nothing else.

Build contract:
- `stargate build --assistant-cloud` picks the cloud variant. Given without the Assistant selected, it stops with exit 6 **before any build step**.
- `build-manifest.json` records `assistant_variant` (`local` or `cloud`) and the APK's package, version and SHA-256. M4's `build-v1` schema gains these two fields.
- The section 5 contents check of M4 reads the **real** permissions from the APK inside the artifact and compares them with the variant: none for local, exactly INTERNET for cloud. Anything else fails with exit 8.
- The cloud variant's local mode makes **zero** network requests even while networking is available (tested with a fake network layer that counts requests, and on the emulator).

## 5. Keys on the phone
- No key is ever baked into an image, an APK, a build manifest, a log or a screenshot (M4's key scan covers APKs too).
- The user pastes a key into settings at runtime. It's encrypted with an Android Keystore key (AES-GCM) and stored in the app's private storage. If the Keystore fails, the key is **not saved** and an error is shown. There's no plain-text fallback.
- **No backups:** the app sets `android:allowBackup="false"` and a data-extraction rule that excludes everything from cloud backup and device transfer.
- The settings screen shows only the last four characters, and a Delete button removes the key and its Keystore entry.
- **Logs** hold metadata only: provider, model, HTTP status, time taken and token counts. Never the key, headers, the question or the answer.
- **Local history stays local.** A cloud mode sends only the current question, never earlier local conversation. Switching modes doesn't upload anything.

## 6. Limits (v2.5: the user's own key, no money tracking)
**Owner's decision (2 Nov):** the user brings their own key, and their own provider plan decides what they can use and what it costs. The app never tracks prices or money. So v2.5 removes the pinned prices, the dollar limits, the cost reservations and the "unpriced model refused" rule. What stays are plain limits that protect any key, including the owner's during the demo, from a bug that keeps calling.

**Limits on every request (in the app and in the codespace):**
- **Input:** one question, at most 2,000 characters **and** at most 8,000 bytes once encoded as UTF-8, no history. The whole request body is capped at **16 KB**; a bigger body is refused before sending.
- **Output:** `max_completion_tokens` (Meta) and `max_tokens` (Baseten) at most **4096**, and a reply body over 256 KB is cut off and labelled.
- **Time:** 60 seconds per request, including its one retry.
- **One at a time:** a second question while one is running is refused. There's at most **one** retry per question, only for the retryable errors in section 3, and never a loop.
- **Model IDs:** the open-weight mode always sends exactly `meta-models/muse-spark-open-1026`. Meta mode sends `muse-spark-1.3` unless the user typed another Meta model ID (section 1); a typed ID must be non-empty, at most 100 characters, and use only letters, digits, `.`, `-`, `_` and `/`, or it's refused before sending. Whether that model is available, and what it costs, is up to the user's own Meta plan.

**Development and demo attempts (an owner-run procedure, not a product limit).** While we build and record, live calls use the owner's keys. The product itself has no attempt allowance; this procedure only protects our own development budget.
- **The log.** `docs/m4c-calls.md` in the product repo holds one row per send: time, provider, model, where it ran (codespace or phone), HTTP status, token counts from `usage`, and its state. It never holds a key, question, answer or money amount. It's committed, so totals survive restarts, new hosts and fixups.
- **The limit:** at most **5 sends per provider** across all of M4c's development and the Mac proof, retries included.
- **States:** `planned` (written before a send is allowed), `sent` (a reply or HTTP status came back), `uncertain` (a timeout, a dropped connection, or anything where the request may have reached the provider). `planned` and `uncertain` both count as used until the owner reconciles them, and an `uncertain` row is never given back.
- **In the codespace,** code writes the `planned` row before sending and refuses any send that would make the total pass 5.
- **Before the phone proof (preflight):** the owner stops all other development calls, counts the rows for each provider, and writes **two** `planned` rows per cloud mode to be tested (the question plus its one possible retry). If that would pass 5, that mode isn't tested and the record says so. After the run, the owner turns each planned row into `sent` or `uncertain` from the app's screen and its metadata log, and deletes a planned row only if the app's log shows that send never happened. No more live work starts until this is reconciled.
- So with four sends already used, the phone proof for that provider can't start: one question and its retry need two.

**The provider's own limits apply.** A hard refusal (401 or 403 key rejected, 402 or a billing or quota-exhausted error) is shown and never retried. A transient 429 follows section 3: at most one retry, only after the provider's wait time, and none if it asks for more than 10 seconds. Across every layer (the app and its HTTP client), a question makes at most **two** sends, and the 60-second limit includes any wait and the retry.


**Moving the v2.4 code over (follow-up fixup).** One fixup on `m4c-cloud` updates everything together: the app's Java code, the codespace Python code, the old ledger and phone-share tests, `docs/m4c-integration.md` and the Mac proof steps. It builds the cloud APK into a new folder, with fresh hashes and an updated Assistant manifest entry. The builder's approved local APK (`1936549b…`) is left untouched. Approving this spec proves nothing live.

The first Baseten attempt is the compatibility probe: it confirms the endpoint, the model ID and the response shape in one call.

## 7. Tests (offline, in the codespace)
- Variants: the local APK has no permissions; the cloud APK has exactly INTERNET; a wrong permission in either fails the contents check with 8; `--assistant-cloud` without the Assistant stops with 6 before building.
- Local mode in the cloud variant makes zero requests (fake network layer).
- Credential routing: with two dummy keys, each request carries only its own provider's key and goes only to its own host. Redirects are refused.
- Errors: each row of the section 3 table with a fake server, including truncation, empty and malformed replies. No substitution, and no response body shown.
- Limits, each refused **before** the fake network layer sees a request:
  - question length, where a "character" is one Unicode code point: 2,000 four-byte characters (exactly 8,000 UTF-8 bytes) are accepted; 2,001 characters are refused; a question of 8,001 bytes is refused;
  - a request body over 16 KB;
  - a typed Meta model ID that's empty, too long or has other characters; any open-weight ID other than the fixed one;
  - a second question while one is running;
  - a second retry for the same question (only one is ever made).
- The development log: the sixth send for a provider is refused in the codespace; a retry counts; the `planned` row is written before sending and survives a restart; a timeout leaves an `uncertain` row that still counts; with four sends already used, the preflight refuses the phone proof for that provider; the log never holds a key, question, answer or money amount.
- Retries: a 402 or quota error is never retried; a 429 is retried at most once and not at all when the wait is over 10 s; a question never makes more than two sends across the app and HTTP-client layers; the 60-second limit includes the wait.
- **Removal check:** no active pricing field, cost calculation, cost or share gate, or per-build allowance remains in the app, the codespace code, the APK or the ledger files (a scan for the old v2.4 field and function names). Documentation that describes the removal, and negative tests that check it, are allowed and listed in the scan's exceptions.
- The input, output and time caps apply.
- Keystore failure: with a fake Keystore that fails on save, the key is not saved anywhere in plain text (the app's files, preferences and logs are searched for the dummy key), an error is shown, and pressing Ask in a cloud mode sends no request.
- Privacy: switching to a cloud mode sends no earlier conversation.
- Logs: a dummy key, a question and an answer never appear in logs.

## 8. Proof on the Mac (owner-run, reusing M4 section 6)
For one Files + Assistant build with `--assistant-cloud`, using M4's transfer hash checks, a **fresh dedicated 6 GB AVD**, `-no-snapshot -wipe-data`, the build-ID read-back and the ADB safety rules:
- **Key handling with dummy keys:** save, restart the app (the key is still there, last four characters shown), delete (gone).
- **No backups, checked two ways:**
  - In the codespace, `aapt2 dump xmltree` of the cloud APK shows `android:allowBackup` set to false and a `dataExtractionRules` file; dumping that file shows both a `cloud-backup` and a `device-transfer` section, each excluding every domain (root, file, database, sharedpref, external).
  - On the emulator, `adb -s <serial> shell dumpsys package com.stargate.assistant` is run and its `flags=[ ... ]` line saved. **Expected:** `ALLOW_BACKUP` is not in that line. If it is there, the check fails.
- **Local mode** answers with networking off.
- **Meta mode** answers one question.
- **Meta open-weight mode** answers one question through `meta-models/muse-spark-open-1026`, with the model ID shown.
- **Before** any live question: the section 6 preflight (other development calls stopped, two `planned` rows per cloud mode tested). **After:** the planned rows reconciled to `sent` or `uncertain`.
- A screenshot of each answer, with no key visible. Each live answer counts against section 6.

## 9. Results
- **Complete:** sections 7 and 8 all pass.
- **Partial:** the local mode and at least one cloud mode pass, and the record names what didn't. For example, Baseten rejects the key or the time-box ran out.
- **Blocked:** neither cloud mode works, or a needed approval or the time-box ran out first.
Whatever the result, the core demo uses M4's build, and the video only shows modes that actually worked.

## Done when (complete)
- [ ] The owner approved the key wording in section 2 (by merging this PR).
- [ ] Both APK variants build, and the cloud build passes M4's contents check with the variant recorded.
- [ ] All section 7 tests pass offline, and the key scan is clean on every artifact.
- [ ] The section 8 records exist; every live call is in `docs/m4c-calls.md` within the attempt limit.
- [ ] One checkpoint commit per part, reviewed by the reviewer Muse. Nothing pushed without the owner's OK.

## Out of scope
Muse Glimmer (outside the demo budget), automatic switching between modes, sending conversation history to the cloud, a custom provider with a typed web address, and real phones.
