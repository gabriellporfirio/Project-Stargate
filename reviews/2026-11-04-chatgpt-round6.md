# StarGate round 6 review

Reviewed 4 November 2026. PR #37 at `6e96bff39c5b33fc6e066f5524779ebc012a8b37`, based on PR #36's merge `79a6453c574f0f8ea507c016ad7fdb7957fae4af`.

R6 means the supplied `Pasted text(4).txt` (69 lines). Media line references use the five newly attached files, whose local names end in `(1).md`. All five were read in full. The [round-5 review](2026-11-04-chatgpt-round5.md) remains the baseline.

The actual PR diff was checked against the pasted diff. The supplied prompt word diffs were compared with the previous full prompts; their removed text matches apart from spacing introduced by the annotation. This approves the submitted changes composed with those baselines, not unseen copies elsewhere. Product results remain owner/report evidence; no product code, build, device operation, inference or diagnostic page request was run. No live-run approval is given.

| Item | Verdict |
|---|---|
| 1. 5l v3 | GO offline. |
| 2. 5m v4 | GO offline under the existing Now-track handover. |
| 3. Live-proof v3 | GO on design; execution stays on hold for completed, reviewed 5m pins. |
| 4. Grok round-5 correction prompt | GO. |
| 5. PR #37 at 6e96bff | APPROVE / GO to merge. |
| 6. Media package after Grok rounds 4/5 | GO for preparation; NO-GO as a complete export package until the simulated-profile disclosure survives every permitted cut. |

## 1. 5l v3 — GO

**Must fix:** none. **Should fix:** none remaining in this diff. **Optional:** none added.

R6:13–16 adds exactly the requested failure-trace clarification and the previously suggested range convention: explicit versioned extraction failures, replay of both failures to the original exit and reason, source bodies retained for reconstruction, existing 5j replay cases preserved, half-open code-point ranges, gap markers counted, and existing decoding/apostrophe handling retained. No broader model, budget or network permission is added. Keep the pinned merged spec and the clean product-start check.

## 2. 5m v4 — GO

**Must fix:** none. **Should fix:** none remaining in this diff. **Optional:** none added.

R6:23 makes the two missing acceptance checks explicit: a late callback cannot overwrite a timeout, and a second transport cannot overlap an unfinished first one. R6:24 separates static password-field evidence from the later real dummy-key Mac proof. The existing deadline, cancellation, cloud-only build, release checks and frozen artifacts remain required. Approval is for the fix prompt; the resulting APK/report still needs review.

## 3. Live-proof v3 — design GO, execution HOLD

**Must fix in the word diff:** none. **Should fix:** none remaining in this diff. **Optional:** none added.

R6:29–38 correctly makes reviewed 5m v4/out-byok3 the active prerequisite; keeps 5c/5k as history; fetches a missing commit locally before the exact-pair merge checks; preserves 5m's corrected docs; and explicitly saves the dummy key before restarting. The extra-conflict stop and immutable local-image evidence remain intact.

FILL_5M_TIP and FILL_5M_SHA must still come from the completed, reviewed 5m result before execution. That is the existing gate, not a new defect. The separate owner go for the Mac live calls remains unchanged.

## 4. Grok round-5 correction prompt — GO

**Must fix:** none. **Should fix:** none in the instructions. **Optional:** none added.

R6:43–47 correctly adds all four A/B proof combinations and narrows the remaining broad verification sentence. This completes the requested wording correction without authorizing a new claim or publication. The submitted final media is reviewed separately below.

Only Grok's intermediate round-4 summary was supplied, not a separate complete round-4 snapshot. Its reported 374 words is therefore a historical report, not an independently recounted intermediate file. The actual final files supplied here were checked.

## 5. PR #37 — APPROVE

**Must fix:** none. **Should fix:** none blocking or substantive. **Optional:** none needed.

The GitHub diff changes only the three stated planning files:
- `m6-parallel-safety.md:52,55`: the search is a hint, not completion evidence; uncertainty keeps the marker. This preserves the fail-closed handover.
- `M5-real-phone-plan.md:34,118,136`: selected excerpts; no obsolete $5 budget; different cited results, including `do_not_install`.
- `master-plan.md:190`: a dated decision and reason.

The version/status wording accompanies those edits. No acceptance rule, budget, provider, execution permission or parallel-work boundary was broadened. Owner merges.

## 6. Media package — one remaining must-fix

**Must fix — preserve the simulated-profile disclosure when the optional profile shot is cut.**

`script.md:66,85` and `claims-check.md:188` allow removing 0:12. That removes the explicit spoken/captioned “simulated profiles, not live handset readings” disclosure. The retained refusal at `script.md:118–120`, `captions.md:25–31` and `shot-capture-list.md:34–37` then describes “the old phone” and its memory without requiring a SIMULATED label. Emulator footage later establishes where the image ran, not how those device facts were obtained.

Keep **SIMULATED phone profile** visible on the refusal and other profile-based shots in every state; if 0:12 is omitted, preserve a short explicit disclosure in a retained caption. Carry this through the shot list and the four-state checklist. This is a caption/label fix, with no new product work or extra scene required.

**Should fix:**
- `script.md:11,87`; `claims-check.md:10,54,165`: Muse Code is a coding agent/tool, not a third model. Use “two models and the coding tool” or “tools and models” in the working notes.
- `captions.md:33,52,80,89,98` and the four-state table: identify master timecodes as shot references and retime captions with the selected cut. After removing A/B, the final diagram and credits no longer start at 2:35/2:50. See the verified table below.

**Optional:** no further rewrite is needed for pace. The 0:12 line is 26 words: about 12 seconds at 130 wpm, then roughly six seconds to read the labels. Its whole-slot average is about 87 wpm; that is a deliberate reading pause.

**Name check:** “Muse Code CLI” is valid. Meta's [product page](https://dev.meta.ai/products/muse-code) calls the product **Muse Code**, its [overview](https://dev.meta.ai/docs/muse-code) describes a terminal/CI coding agent, and its [official subscriptions documentation](https://dev.meta.ai/docs/muse-code/subscriptions) uses **Muse Code CLI** explicitly. The credit need not be marked unknown. “Wrote the product code” is supported by the supplied project fact base, not independently established by the naming documentation.

## Media verification

Every factual sentence and caption was checked against the supplied fact base and its subsequent corrections. Coverage:

| Facts | Result |
|---|---|
| 1–2: simulated profiles, status labels, 1 GiB versus 1.6 GiB refusal | Wording/numbers match; the optional-cut disclosure defect is identified above. |
| 3: two builds | cc8f48d6 and 1f8f2553 match; different contents/IDs and model-after-boot wording are correct. No unproved size difference remains. |
| 4: Mac emulator and file round trip | Matches the fact base; emulator labels are required. No real flashing is claimed. |
| 5: offline Llama answer | Correctly tied to the earlier recording. 0.4 s is described as a screen statistic, not an end-to-end latency measurement. New runs must use their own output. |
| 6–7: verification scope and no handset flashed | Quotes/fixed rules wording is appropriately narrow; the handset statement is retained in every video state. |
| A/B: M5 and cloud answer | Success text is conditional; working statuses remain pending; real outcomes replace expectations. The X drafts carry PENDING PROOF. No invented cloud reply. |
| C: polished screens | No mockup is presented as working product footage. Actual CLI/readable output is allowed. |
| Roster/credits | The four model/tool credit combinations match A/B status. Correct the working-note classification of Muse Code. |
| Deadline/judging weights | Match the supplied brief/owner guide; no new contest eligibility or prize claim was introduced or independently certified here. |

With the profile shot retained, the four states select consistent narration, captions, diagram and credits:

| Proof state | Words | Duration | Average pace | Diagram / credits start | Credits |
|---|---:|---:|---:|---|---|
| A and B | 367 | 3:00 | 122.3 wpm | 2:35 / 2:50 | Muse Spark, Muse Spark Open, Muse Code CLI |
| A only | 335 | 2:45 | 121.8 wpm | 2:20 / 2:35 | Muse Spark, Muse Code CLI |
| B only | 296 | 2:25 | 122.5 wpm | 2:00 / 2:15 | Muse Spark Open, Muse Code CLI |
| Neither | 263 | 2:10 | 121.4 wpm | 1:45 / 2:00 | Muse Code CLI |

The install-plan box is included exactly when A is proven, with its limit visible. B never depends on A. All states retain the offline answer and no-handset-flashed statement. If 0:12 is omitted, subtract 18 seconds from later timestamps and 26 words, **while retaining the mandatory disclosure**. If another genuine M5 outcome is inserted, match its words and recount that actual cut; the four fixed totals above describe the written success/omit variants.

Independent counts:
- Main narration rows: 28, 26, 45, 69, 43, 45, 31, 29, 29, 22 = **367** words, using the package's space-separated convention.
- X versions 1–3 and thread posts 1–4: **277, 275, 278, 274, 222, 277, 274** characters, including line breaks. These blocks are ASCII, with no URL or emoji weighting ambiguity.
- Longest line anywhere in `captions.md`: **37 characters**, below 42.
- Captions' default end credit is the neither-proven version; the alternative credits correctly replace it when the chosen proof state changes.

The earlier full files and previous reviews remain the historical record. The newer state does not erase earlier overstatements, failed runs or missing evidence.
