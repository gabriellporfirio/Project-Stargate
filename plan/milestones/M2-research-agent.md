# M2: Research agent (spec)

Status: v1 draft for ChatGPT review. Planned for Sat 31 Oct. Builds on the M1 checkpoint (full SHA to be pinned in the M2 prompt, after the M1 report is reviewed).

## Goal
Given a phone's identity (manufacturer, model, codename, Android version, platform), StarGate uses a Meta model to research what exists for that phone, and returns a **cited research report**. Code checks every citation before anything trusts it. Unverified or invented claims stay visible, marked as rejected or unverified, and can never drive a build.

This is the main "use of Meta AI tooling" piece of the demo ([scoring plan](../scoring-plan.md)), so the live steps must be clear enough to film.

## 0. Spike first (30 minutes, recorded in `docs/m2-spike.md`)
Before building, Muse checks against the live Meta API and the current docs:
1. Does `muse-spark-1.3` support **tool calling** (function calls) on `https://api.meta.ai/v1/chat/completions`? Record the request and response shape, with the key redacted.
2. Does it support **structured JSON output** (a response format or schema)?
3. What does a research-sized call cost in tokens and time? Use a cap with headroom, as M0 showed.

The result picks the mode:
- **Agent mode** (if tool calling works): the model decides which allowed tool to call next, and code runs it.
- **Pipeline mode** (fallback): code fetches a fixed set of sources, then the model reads them and writes the cited report.

Both modes produce the same report format and the same live step display. This is Q14 in the master plan.

The spike also checks the **Baseten** model (Q3). The owner's hackathon Baseten key works only with `meta-models/muse-spark-open-1026` (owner, 30 Oct). Muse checks against Baseten's current docs, without assuming anything:
4. the endpoint URL and auth for that model, with the key read from a `BASETEN_API_KEY` Codespaces secret and never printed
5. whether it accepts the same chat request shape, and whether it supports tool calling or JSON output
6. how billing works for this key (per token or per running deployment), so the $100 credit isn't burned by an idle deployment
7. whether "open" means downloadable weights, and if so, the model's size. That decides whether it could ever be a candidate for the on-phone Assistant (M3 fit engine), which is unlikely but worth recording

## 1. Inputs and privacy
- **Input:** either `--sim <fixture>` (identity taken from an M1 profile) or `--device "<manufacturer> <model>"` / `--codename <codename>`.
- Simulated fixtures carry invented identities, so live research uses a **real, public device name** for the demo, for example a well-documented older phone. Muse proposes one and the owner approves it. It must not be the owner's own phones.
- **Only the identity fields leave the machine:** manufacturer, model, codename, Android release, SDK level and platform. Never serials, IMEIs, accounts or anything else from a profile. A test proves this.

## 2. Tools (deterministic code, never the model)
Each tool has an allowlisted domain, a timeout (10 s), a response size cap (1 MiB), and a per-run budget (at most 20 tool calls and 3 minutes in total). Every fetch is cached per codename, with the URL, fetch time, HTTP status and SHA-256 of the content.

| Tool | Source | What it answers | To verify in the spike |
|---|---|---|---|
| `lineage_device` | LineageOS wiki device pages | Is there an official LineageOS build, and for which versions? | URL pattern and page structure |
| `github_repos` | GitHub REST API (search and repo lookup) | Device trees, kernel and vendor repos: existence, default branch, last push | Unauthenticated rate limits. **No codespace token is used** |
| `pmos_device` | postmarketOS wiki | postmarketOS support status | URL pattern |
| `hf_models` | Hugging Face models API | Small quantised **Meta Llama** builds for the Assistant: size, licence, format | Query parameters and licence fields |
| `fetch_page` | Only the domains above | Read one cited page | |

The model can only ask for these tools. Any URL outside the allowlist is refused by code, and the refusal shows in the steps.

## 3. The report (`research-v1`)
A versioned JSON format with a validator, in the same style as `profile-v1`:
- **`claims`**: each one has a topic (`community_os`, `device_tree`, `kernel_source`, `vendor_blobs`, `stock_firmware`, `treble_gsi`, `ai_model`), a statement, a typed value where possible, and one or more **citations** (`url`, `fetched_at`, `sha256`, `excerpt`).
- **`status` per claim:**
  - `verified`: code fetched the cited URL, it returned 200, and the excerpt appears in the fetched content. For a repo, the GitHub API confirms it exists.
  - `unverified`: the citation couldn't be checked (timeout, rate limit, page changed).
  - `rejected`: the URL isn't allowlisted, doesn't exist, or the excerpt isn't in the page. The reason is kept.
- **`steps`**: the ordered log of what was asked, which tool ran, what came back (status and size), and what was rejected and why.
- **Rule:** only `verified` claims may be used by M3. "Verified" means the citation checks out. It does **not** mean the claim is true in every respect (for example, a device tree existing doesn't prove it builds). The report says so.

## 3b. Second-opinion audit with Baseten (development only)
**Product rule:** the product users run needs only a Meta API key. Baseten (`muse-spark-open-1026`) is never called by `stargate` itself. It's used only during development, through a separate script outside the product package. Its exact role (auditing research data and/or reviewing code) is being decided by the owner, and this section gets filled in before M2 starts.

## 4. `stargate research`
- `stargate research --device "<name>"` (or `--codename`, or `--sim`) shows the steps **live**, one line each: searching, fetched, verified, rejected and why. It ends with a readable summary grouped by topic, with each claim's status and its link.
- `--json` prints the validated report.
- `--offline <recording>` replays recorded tool responses, labelled SIMULATED, so the demo has a safe fallback.
- If the Meta call fails, it says so with the M0 result codes. It never invents a report.

## 5. Tests (offline, using recorded responses labelled SIMULATED)
- A model citing a non-allowlisted URL → refused, shown as rejected.
- A model inventing a repo → GitHub lookup returns 404 → rejected.
- An excerpt that isn't on the page → rejected.
- A tool timeout and a rate limit → unverified, with the reason.
- The budget is exceeded → the run stops cleanly with a partial report, clearly marked.
- Only identity fields are sent to the model. No serial-like value appears in any request.
- Report validation: valid and invalid examples, as for `profile-v1`.
- Model output never becomes a command: there is no code path from report text to execution.

## Done when
- [ ] `docs/m2-spike.md` records the tool-calling and structured-output results, the mode chosen, and the Baseten findings (spike points 4–7).
- [ ] A test proves the `stargate` package never calls Baseten and never reads `BASETEN_API_KEY`.
- [ ] A live `stargate research` run on the approved public device shows live steps and ends with at least one `verified` claim per topic it found, each with a working link.
- [ ] The same run, or a recorded test, shows at least one `rejected` claim with its reason.
- [ ] `--json` output validates against `research-v1`.
- [ ] `--offline` replays a recorded run without any network.
- [ ] All tests pass offline (count above zero). `stargate doctor` still passes.
- [ ] No installs (or each one listed and approved). One checkpoint commit, and nothing pushed without the owner's OK.

## Out of scope
Ranking strategies (M3), fit decisions (M3), building anything, real phones, and voice and photo features.

## Network use allowed in M2
Product: the Meta API and the allowlisted research domains in section 2, within the budgets. Development-only scripts may also call Baseten (section 3b). Nothing else.

## Demo (under 5 minutes)
```
.venv/bin/stargate research --device "<approved public device>"
.venv/bin/stargate research --device "<approved public device>" --json > /tmp/r.json && .venv/bin/python -m stargate.research validate /tmp/r.json; echo "validate exit $?"
.venv/bin/stargate research --offline <recording>; echo "offline exit $?"
.venv/bin/python -m unittest; echo "tests exit $?"
```
