# M4c: Assistant cloud mode (spec)

Status: v1 draft, 1 Nov 2026, for review. It follows the owner's direction on 1 Nov: the phone is limited by its hardware, so the Assistant offers a small local model **and** cloud models, the way a model picker lists several providers. It's built **only after M4's local Assistant answers in the emulator**, so it never delays M4.

## Why
- **For the user:** the phone runs a small model offline, and hands harder questions to a bigger Meta model in the cloud.
- **For the hackathon:** the open-weight bonus counts only Muse Glimmer or Muse Spark Open, "served on participants' own hardware or through partner-provided inference" ([participant guide](../../docs/participant-guide-excerpt.md)). Muse Glimmer has 30B parameters (owner, from Meta's developer page, 1 Nov), far too big for the 4 GB emulator phone or a 16 GB Mac. Muse Spark Open through partner inference is the realistic route.

## 1. The three Assistant modes
| Mode | Model | Where it runs | Key |
|---|---|---|---|
| **Local** (default) | the small model M4 chose (from the plan's handoff) | on the phone, no network | none |
| **Meta cloud** | `muse-spark-1.3` (the product's model, Q2) | Meta API, `api.meta.ai` | the user's own Meta API key |
| **Open-weight cloud** | Muse Spark Open (`meta-models/muse-spark-open-1026`) | partner inference: Baseten for the hackathon (Q3) | see section 2 |

The home screen and the Assistant always show which mode answered, and the model ID.

## 2. The key question (Q16, unknown)
The Meta API key's model list (Q2, 30 Oct) doesn't include Muse Spark Open. If the user's Meta key can't call it, the open-weight mode needs a partner key. That bends the product principle ("the only key a user needs is their Meta key"). Proposed wording, **for the owner to approve by merging this PR**:
- StarGate still **needs** only the user's Meta key. Local and Meta cloud modes work with nothing else.
- Open-weight cloud mode is **optional** and uses a partner key the user adds themselves. For the hackathon demo, that's the owner's development Baseten key.
- If Q16 shows the Meta key can call Muse Spark Open, the open-weight mode uses the Meta key instead, and the exception isn't needed.

**The Baseten key (hackathon email, quoted by the owner on 1 Nov):** "Use exactly meta-models/muse-spark-open-1026. Your key only works with this hackathon model." So the open-weight mode's model ID is exactly `meta-models/muse-spark-open-1026`.

**Owner's direction (1 Nov):** the demo uses Baseten for the open-weight mode either way, to show the hackathon's partner resources in use. The owner's Meta developer page offers `muse-spark-1.2-contributor` (owner, 1 Nov). That isn't Muse Spark Open, and whether it counts for the bonus is unknown, so Q16 stays open.

## 3. Keys on the phone
- No key is ever baked into an image, an APK, a build manifest, a log or a screenshot.
- The user types the key into the Assistant's settings at runtime (in the demo, on the emulator). It's stored in the app's private storage only, encrypted with the Android Keystore, and can be deleted from the same screen.
- Requests go only to the two hosts in section 1, over HTTPS. No other host is allowed (tested).
- The demo video never shows a key. The settings screen shows only the last four characters.

## 4. Network
This is the one change to M4's Assistant rule ("no network permission"):
- The **local** mode is unchanged and still proven with networking off (M4 section 6).
- Cloud modes need Android's network permission. That permission goes into a **separate cloud module**, added only by a new build option `stargate build --assistant-cloud`, allowed only when the plan selects the Assistant and recorded in `build-manifest.json`. A build without it has no network permission in any Assistant part (checked by M4's section 5 contents check).
- A cloud mode with no network shows "cloud not reachable" and never falls back silently. A switch to local mode is offered, and shown as such.

## 5. Limits
- Live calls during M4c: at most **5** Meta cloud calls and **5** Muse Spark Open calls in total, each with `max_completion_tokens` at most 4096 and one retry, logged without prompts that contain personal data.
- The Baseten spend for the demo stays within the hackathon's $100 key.
- Any finish reason other than `stop` is shown as incomplete (M3 carry-over).

## 6. Tests (offline, in the codespace)
- Local-only builds contain no cloud module and no network permission.
- Key handling: no key in any artifact, manifest, log or test output (the key scan covers APKs and images too).
- Host allow-list: requests to any other host are refused.
- No network: a cloud mode reports "cloud not reachable", and nothing falls back silently.
- The UI label always names the mode and model that answered.

## 7. Boot proof on the Mac (owner-run)
For one Files + Assistant build with cloud mode included:
- the local mode answers with networking off (as in M4);
- the Meta cloud mode answers one question;
- the open-weight cloud mode answers one question through Muse Spark Open, with the model ID shown;
- a screenshot of each answer, with the key never visible.

## Done when
- [ ] Q16 is answered, and the owner has approved the key wording in section 2 (by merging this PR).
- [ ] The three modes work in the emulator with the section 7 records.
- [ ] All section 6 tests pass offline, and the key scan is clean on every artifact.
- [ ] One checkpoint commit, reviewed by the reviewer Muse. Nothing pushed without the owner's OK.

## Out of scope
Muse Glimmer (too big for the phone), automatic switching between modes, any other cloud provider, and real phones.
