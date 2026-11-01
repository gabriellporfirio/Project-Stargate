# M4c: Assistant cloud mode (spec)

Status: v2, 1 Nov 2026. It folds in [ChatGPT's review of v1](../../reviews/2026-11-01-chatgpt-m4c-assistant-cloud-mode.md) (four must-fix, one should-fix). It follows the owner's direction on 1 Nov: the phone is limited by its hardware, so the Assistant offers a small local model **and** cloud models, the way a model picker lists several providers.

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
| 429 | "Too many requests, try later" | once, after the provider's wait time if given (at most 10 s) |
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

## 6. Limits (enforced in code, shared across everything)
- **Attempts:** at most **5 per provider** for all of M4c, counting every compatibility probe, retry, emulator demo and rerun. Each attempt is recorded in `docs/m4c-calls.md` (time, provider, model, status, tokens, estimated cost) and in a local counter the code checks **before** sending. When the count is used up, the call is refused before it leaves the device or codespace.
- **Input:** one question, at most 2,000 characters, no history.
- **Output:** `max_completion_tokens` (Meta) and `max_tokens` (Baseten) at most **4096**, and a reply body over 256 KB is cut off and labelled.
- **Time:** 60 seconds per request, including the one retry.
- **Spend:** before the first Baseten call, the owner reads the remaining balance on Baseten's billing page and records it. M4c may use at most **$5** of Baseten credit and **$2** of Meta credit. The estimated cost of each call is recorded from its `usage`.
- The first Baseten attempt is the compatibility probe: it confirms the endpoint, the model ID and the response shape in one call.

## 7. Tests (offline, in the codespace)
- Variants: the local APK has no permissions; the cloud APK has exactly INTERNET; a wrong permission in either fails the contents check with 8; `--assistant-cloud` without the Assistant stops with 6 before building.
- Local mode in the cloud variant makes zero requests (fake network layer).
- Credential routing: with two dummy keys, each request carries only its own provider's key and goes only to its own host. Redirects are refused.
- Errors: each row of the section 3 table with a fake server, including truncation, empty and malformed replies. No substitution, and no response body shown.
- Limits: attempt counting includes retries; the sixth attempt is refused before dispatch; the input, output and time caps apply.
- Privacy: switching to a cloud mode sends no earlier conversation.
- Logs: a dummy key, a question and an answer never appear in logs.

## 8. Proof on the Mac (owner-run, reusing M4 section 6)
For one Files + Assistant build with `--assistant-cloud`, using M4's transfer hash checks, a **fresh dedicated 6 GB AVD**, `-no-snapshot -wipe-data`, the build-ID read-back and the ADB safety rules:
- **Key handling with dummy keys:** save, restart the app (the key is still there, last four characters shown), delete (gone), and `adb -s <serial> shell bmgr` shows the app is excluded from backup.
- **Local mode** answers with networking off.
- **Meta mode** answers one question.
- **Meta open-weight mode** answers one question through `meta-models/muse-spark-open-1026`, with the model ID shown.
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
- [ ] The section 8 records exist, and every live call is in `docs/m4c-calls.md` within the limits.
- [ ] One checkpoint commit per part, reviewed by the reviewer Muse. Nothing pushed without the owner's OK.

## Out of scope
Muse Glimmer (outside the demo budget), automatic switching between modes, sending conversation history to the cloud, a custom provider with a typed web address, and real phones.
