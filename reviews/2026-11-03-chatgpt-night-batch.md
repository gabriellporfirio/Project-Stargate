# StarGate: review of the 2 November batch
Reviewed 3 November 2026. Planning PR #36: d63131c8f7ca94b848423e7b9f9c2375fefb0eb7.

This reviews all supplied versions, their change logs, and the supplied reports. Earlier versions remain part of the findings below. The earlier complete Grok outputs and intermediate draft snapshots were not supplied; their instructions and documented changes were reviewed, not unseen bytes.

Evidence boundary: I read the planning files directly at the pinned commits and the 17 supplied files. Product commits/APKs and the two saved diagnostic HTML bodies were not available for an independent source/build audit. Product test totals, measurements and Mac results below are attributed to the reports/owner. I independently checked the media counts and current primary API documentation. No product code, build, device operation, inference or diagnostic page request was run.

Line references are to the supplied files. D1 = Pasted text(2).txt (M4c live proof); D2 = Pasted text (2).txt (M6 next stages); G6 = Pasted text (3).txt (run history and 5m). M5 v2.2/5l references use the named paragraph/item in the pasted draft.

| Item | Decision |
|---|---|
| 1. PR #36 round 4 | NO-GO as written; the previous dead-helper cleanup defect is fixed. New code-informed prompt corrections remain. |
| 2. M4c live proof | NO-GO until the corrected 5m handoff and fresh-build input instructions are incorporated. Base and bounded proof approach approved. |
| 3. M6 join / platform Part 2 / phone Part B | NO-GO as written. Shared reviewed join approved; real Assistant integration must wait for Part B. |
| 4. M5 v2.2 and 5l | GO on whole-section excerpts, 8192 and 180 seconds as a bounded trial. NO-GO on pasting the current implementation prompt until the contract corrections below are included. No live-run approval. |
| 5. Media | GO for preparing/capturing already proven material with the corrections below. NO-GO for publishing the current package or treating A/B/C as proved. |
| 6. Runs and 5m | Historical work accepted only to the extent evidenced below. 5m v1 and v2: NO-GO as written; O2 and O4 are must-fix. |

## 4. M5 v2.2 and fix 5l — urgent

**Must fix**

- **Historical explanation, “the model never saw them … couldn't have quoted them.”** Correct this. The reconstructed prompt included the anchors in its Rules section (m5-report.md:885–890); the running-page excerpt omitted their surrounding source context. The v2 raw response usage was not retained, so do not assert that 4096 reasoning tokens were measured or that page truncation alone caused the four empty answers. Keep the failed run and reconstruction caveat.
- **Excerpt definition / 5l item 1.** “Innermost” elements can discard direct text in an enclosing aside/list item when it contains another selected element. Preserve all visible section text once, including warnings, headings and commands; exclude scripts/comments; keep entity decoding once. Merge overlapping sections in page order. Fail closed if an anchor cannot be located/mapped. Add nested-container and overlapping-section tests.
- **Quote/range/replay contract / 5l items 1–2, 4–5.** Define ranges against the canonical decoded, normalized page text; record the exact sent excerpt and its UTF-8 hash, source ranges and extraction version. Validate quotes within a real source range, never across an inserted gap. Replay must validate/reconstruct that same evidence without network and detect changed excerpt/hash/ranges. Align existing spec §2, I-QUOTE in §3, output §4 and tests §7; “sections 1 and 5 only” is insufficient. Preserve old traces under their original interpretation or explicitly reject unsupported versions. Keep the new anchor/excerpt exit-6 traces and non-skipping saved-body fixtures.
- **Budget / 5l item 3.** Specify one monotonic 180-second run deadline across fetches, requests, waits and repair, with remaining time enforced during I/O. It is not 180 seconds per call. Keep three sends maximum, one repair, one transport retry; malformed/empty/non-stop model answers are not transport retries.

**Should fix**

- Explicitly pin and record top-level reasoning_effort="low" for the next trial, with a fake-request test. Meta now documents this parameter; do not use "none", silently substitute models, or automatically raise the cap after failure. Record usage when returned, otherwise unknown.
- Make the planning fetch the sole stated network exception, or have the owner prefetch PLAN_V22_SHA before the offline task.

**Optional / decisions**

Whole sections win over ±2 blocks: the measured 642/2553 characters retain unlock commands. Mechanical source selection is legitimate; describe it as a constrained, source-grounded proposal checked against fixed rules, not independent discovery of a safe handset procedure. 8192 and 180 seconds are reasonable next ceilings, not a success guarantee. Defer 16384. No additional live attempt follows this review automatically.

## 1. PR #36 round 4

**Must fix**

- **m6-part1-platform.md:41 — P2.** A fresh image needs launcher/Files APKs built for its current selection/build ID. The code review reports that the CLI otherwise takes frozen M4 APKs (m6-prompts-review.md:29). Approve rebuilding into the platform's own output/tools directories and calling the existing build entry point with explicit inputs. Verify the embedded launcher config and build manifest agree. Do not write to the frozen M4 output.
- **m6-phone-a-link-files.md:51,54 — H1.** Replace “none beyond M4's”: M4 Files requests INTERNET. Explicitly remove that requested permission in M6, test zero requested permissions for Files, and allow its own signature-permission declaration separately. Align the spec's ambiguous Files wording too.
- **Platform:25 / phone:23 — interference.** Treat individual tests that invoke aapt2/d8/build tooling as heavy. The read-only review identifies a concrete collision with build_apps.sh's process guard (m6-prompts-review.md:65). A test being small does not make it safe during Now work; an avoidable build failure is interference.

**Should fix**

- **P1, platform:41.** Approve fresh-only Part 1. Missing provenance prevents old images satisfying the strict reuse gate; that is safe refusal, not permission to weaken it. Defer reuse and new shared build-schema fields, or assign their ownership explicitly to avoid both Muses editing them. Existing images retain their historical M4 labels.
- **Safety:31–32,52 / G6:211.** Do not start heavy work before creating the marker. Create it first, with an explicit unknown/pending group if needed; recheck the flag, then start the isolated group and atomically record its verified identity. Unknown/malformed identity or a failed process inspection must keep the marker. Launch once: the safety note currently describes “runs the step” twice.
- Guard the API-29 settings panel on the API-28 minimum; label static listener/layout checks as static and retain owner runtime checks. Defer chat tests explicitly to Part B. The missing M2 replay should show the honest placeholder, never an invented hash binding. Update the Now-track table to current work.

**Optional**

Keep worker limits conditional on using Gradle. No need to add tooling.

**Assessment:** fixed bases and separate outputs give dependency isolation. The revised marker protocol fixes round 3's automatic deletion on a dead wrapper. Shared resources still require the handshake and tooling-test correction; “no shared locks” in G6:203 is inaccurate. Browser rules, streaming, selected-service composition and pending runtime evidence otherwise match M6 v2.1. Part A is not the combined §7 proof.

## 2. M4c live-proof prompt, DRAFT 1

**Must fix**

- **D1:3,21,27,69.** Make corrected, reviewed 5m a prerequisite and replace all old commit/APK/path pins together. 5k fixes URLs but is not proof-ready: the current proof sheet/test still selects the old APK, and the reported timeout/double-send issues remain. Never infer approval of O4 from the draft.
- **D1:25–35.** Add the fresh launcher/Files build and explicit input selection described in item 1. Build them in m4c-tools under the lock, preserve the approved Assistant/model snapshots, and check that the launcher selection/build ID matches the image manifest. A cloud switch plus a new image alone does not update a baked launcher.
- **D1:35,43 / 5m verification.** Scan the extracted APK entries as well as the surrounding artifacts; scanning only compressed bytes can miss strings. Use the final manifest's APK for all transfer instructions. Stop recording before key entry, use the masked field, save/clear it, clear the clipboard, then resume recording. Masking is not a reason to film real-key entry.

**Should fix**

- **D1:22.** The “take theirs” permission is limited to the exact verified pair and the two known hunks. Repeat that check after repinning 5m. Preserve validation of the actual builder-selected snapshot, not merely an identically hashed sibling APK. Any unexpected conflict stops; remove the competing instruction to resolve “any other conflict.”
- **D1:32.** Revalidate the historical local image against its original manifest/handoff context; do not rewrite its evidence to use a new cloud handoff.
- **D1:31.** Measure actual remaining space/inodes for the chosen placement, including native-library extraction; old stock free-space figures alone are not current fit evidence.

**Optional / decisions**

The fresh 5a9c7e6 worktree is the right base; M5 is unnecessary. Keep this pre-Link proof as the early fallback clip. One question per provider, with at most its single automatic retry and two planned development rows, is appropriate. Four rows already used means skip that provider. Keep uncertain rows consumed until reconciled; later Link proof uses the same development log. Owner wait-for-CLEAR and the separate Mac “go” are already correctly present. “BUILD READY, MAC PROOF PENDING” is the correct builder verdict.

## 3. M6 join, platform Part 2 and phone Part B, DRAFT 2

**Must fix**

- **D2:25.** The old diff e90edfa..5a9c7e6 does not authorize replacing tests after Phone A adds code. Check conflicts using the actual pinned Phone-A, M5 and final BYOK tips and merge bases. Preserve new Part-A checks; do not use blanket checkout --theirs based on an earlier baseline.
- **D2:28,42,56.** The -v2 traces do not exist: those live runs exited 5 and replay failed for missing files (m5-report.md:696–758). Replace the glob with an explicit reviewed artifact list when v3 exists, or the no-record state. A usable replay bundle needs its exact saved profile/plan and provenance inputs, not just a trace hash. A freshly scanned same-name profile can have different bytes. Keep hash equality; do not match by name or relabel synthetic data as live.
- **D2:48,56,67–88.** The join has Phone A and the pre-Link Assistant. Part B adds its service, changes its signing and creates new APKs. Platform Part 2 may develop Files-only integration and labelled fake tests in parallel, but cannot claim a real Files+Assistant Link build before the reviewed Part-B handoff is merged. The BYOK app merge also does not supply the separate cloud-builder hook. Name the final integration owner/commit and those dependencies.
- **D2:84,87.** “New handoff beside old” needs explicit selection: wire the new manifest/APKs into the builder instead of its old hard-coded snapshot; record their hashes/signing in the resulting build. Revalidate the M3 plan against unchanged model metadata; regenerate through M3 only if its inputs actually changed. Do not hand-edit hashes or overwrite old handoffs.
- **D2:26.** Update active M6 instructions, not historical M4 evidence that correctly says Files listened on 8080.

**Should fix**

Resolve “same independence block applies in full” versus the newly authorized merges. Pin the planning revision containing these decisions and M5 v2.2. Repin 5m everywhere, including “5c report's hash.” Specify Unicode code points, a shared single-question gate across UI/service, and one end-to-end 60-second deadline. Retain requested versus declared permission checks.

**Optional / decisions**

One reviewed join is preferable to divergent merges. Phone-only key entry is correct; the browser mode switch can remain. Keep pre-Link M4c footage as fallback, identified as that build. --allow-live plus CSRF, per-step opt-in and budgets is an appropriate implementation boundary; it grants no permission to run live now. Both later cloud proofs share the five-attempt development accounting.

## 5. Grok's video and X package

**Must fix**

- **x-post.md:24–26,36–38,62–66.** Replace “On the phone” with “In the emulator.” “No real handset flashed” does not establish where inference ran: a real handset can run an app without flashing. Version 3 already names the emulator. Keep the emulator label throughout offline/cloud emulator footage.
- **shot-capture-list.md:21,51–60 / script.md:71.** “Current phone page/current welcome” is assumed ready but not established by this evidence. Use actual CLI/readable outputs, or keep those UI shots under C/PENDING until the screen exists; do not recreate a mockup as product evidence.
- **shot-capture-list.md:89–99 / script.md:143.** The exact planet answer and “7 tokens, 0.4 s” belong to the owner's recorded earlier build. They may be shown as that evidence. If capturing a new APK/run, record its actual answer/stats and update the script; do not force the previous output, overlay its timing, or repeat calls to obtain it.
- **claims-check.md:53,183,261.** “This app … builds a system” is a product claim, not a general truth. Bind it to proven emulator builds (fact 3). Keep the simulated-profile and emulator scope clear; neither the hook nor “It reads the phone” establishes a tested real-USB reader.

**Should fix**

- **script.md:52–53,167–181.** The diagram and credits also depend on A/B even though their rows say READY. Mark their working status conditional and select a consistent success/fallback script, captions, diagram and credits before export. Success voice-over is fine only when its corresponding proof exists. No need to narrate “pending.”
- **script.md:168 / captions.md:88 / X thread 4.** “Every step is checked” maps to fact 6 but can overstate scope. Prefer “The model proposes steps; code checks the quotes and fixed rules.” Preserve M5's visible “not a validated install procedure” limitation.
- Use the actual accepted/unconfirmed/do-not-install/no-valid-plan outcome. The two proposed M5 scenes are expectations, not required results to manufacture.

**Optional / pace**

All seven posts count correctly: 274, 272, 278, 271, 214, 277, 278 characters. Burn-in lines checked are at most 42 characters. The ten voice rows total 368 written words over 180 seconds, about 123 wpm. The 0:12 row is 25 words/18 seconds, 83 wpm: speak naturally and leave time to inspect labels, rather than stretching the delivery. The 3:00 structure works on paper; time a read with spoken numbers. If A/B fail, shorten the cut instead of padding 50 seconds with repeated refusals/holds.

## 6. Unreviewed runs and 5m v1/v2

**Must fix before 5m is sent**

- **G6:232,254 / byok-review.md:54 — O2.** This is mandatory, not optional. Catching TypeError around send can cause a second raw send after the first already happened, while logging one attempt. Remove the fallback; require the two-argument interface. An internal TypeError must produce one send and an uncertain row, not a compatibility retry.
- **G6:234,261 / byok-review.md:56 — O4.** I do not approve deferral. Separate connect/read timeouts are not the promised 60-second question deadline; slow trickling can extend it further. Enforce one monotonic deadline across request I/O, response reads, wait and retry, with cancellation/cleanup and no late answer or overlapping generation. Test slow connect followed by slow read, trickled body, retry wait, and busy-slot release using offline fakes. Apply the contract to phone and codespace paths. Merely splitting connect/read allowances is insufficient.
- **G6:226–237.** After building out-byok3 and obtaining its hash, refresh the concrete Mac proof path/hash and manifest-derived guard, then run the final suite. Items 1–7 before the build cannot know that final hash. Mandatory release checks must actually read the new APK: generic missing-artifact skips are not proof. Scan its ZIP entries and updated docs for key-shaped strings; report scan results without secret text. Keep all frozen outputs unchanged.
- **m5-report.md:418–425.** Missing diagnostic files after interruption do not establish zero attempted pre-stop requests. If durable evidence establishes zero, name it; otherwise record that part as uncertain. Keep the two observed resumed diagnostic requests separate. This is an evidence correction, not a claim that extra requests definitely happened.

**Should fix**

The password field is worth the new APK. Its source check is limited evidence: verify masking with a dummy key on the Mac, and film no real-key entry. Use exact terms URL values, the whole-string Baseten old-URL check, expanded historical-doc labels and code-version-qualified builder paths from v2. Correct report claims of complete 60-second enforcement and screenshot safety until their fixes/proofs pass. Keep future reports outside /tmp.

**Optional / decisions**

Approve deferring O5's generic 4xx wording: the report says it does not retry. O3 dead constants can be removed. This does not approve deferring O2/O4. 5f/5j are consistent with the intended offline fixes on the supplied evidence, with their known trace/fixture gaps carried into 5l. Neither establishes a successful M5 live plan.

## Version and run ledger — earlier faults remain visible

### Planning and drafts

| Version | Assessment |
|---|---|
| PR36 R1, 68633b5 | NO-GO then: plan-hash-only reuse, insufficient shared-resource controls, and treating manifests as runtime listener proof. |
| PR36 R2, b69c5df | Reuse/content and runtime-evidence wording improved; active/queued heavy work could still overlap Now work. |
| PR36 R3, dcec74f | Normal handshake improved, but dead-wrapper cleanup could print CLEAR while a child survived. The earlier review recorded a local reproduction. |
| PR36 R4, d63131c | Automatic deletion removed; that failure is addressed. This review adds the code-informed P2/H1/tool-test findings, rather than pretending they were previously checked. |
| D1 20:42 | 5c/f4d6798d pin included wrong terms links; not a proof-ready release. |
| D1 21:30 | 5k/6ecb88e0 corrects URL constants; stale proof instructions and underlying limits still need review fixes. |
| D1 21:47 | Same question in all three modes is a valid improvement, not proof of any future answer. |
| D1 22:10 | Conflict, stale input docs and missing builder scan identified. “Keep every old test literally” did not describe a workable merge. |
| D1 22:33 | Known two-hunk resolution is reasonable only for its verified commits; preserve validation of actual consumed inputs. |
| D1 pending 5m | Not reviewed as an existing artifact. Repin only after corrected 5m passes. |
| D2 20:42 / 21:30 | Same old-to-5k pin history as D1. Neither supplies Link's Assistant service/signing or a successful M5 replay. |
| D2 22:10 / 22:33 | Baseline merge analysis does not generalize to future Phone-A edits. Actual-tip conflict review remains necessary. |
| D2 pending 5m | New pins and final Assistant integration dependencies remain outstanding. |
| M5 draft 20:25 | ±2 blocks is not approved after evidence that it cuts unlock commands. 6000/page, 8192 and 180 seconds are reasonable bounded choices. |
| M5 draft 22:12 | Adding anchor-failure traces and non-skipping body fixtures correctly exposes earlier coverage gaps. |
| M5 draft 22:48 | Whole sections and fresh anchor matching are preferable; lossless extraction/provenance and the historical explanation need the corrections above. |
| Grok round 1 | Withdraw image-size differences and whole-answer 0.4-second latency claims. A/B/C were pending; model input must be described as relevant sections. |
| Grok round 2 | Conditional success/fallback scripts, corrected stats/size wording and conditional credits improve accuracy. Mapping the app's build claim to “general truth” is still wrong. |
| Grok round 3 | Version 3's emulator wording and reduced profile repetition are improvements. Versions 1/2/thread 1 still need explicit emulator wording. Only current output files were supplied for line-by-line checking. |
| 5m v1, 22:25 | NO-GO: unclear proof-doc source, Baseten prefix trap, incomplete historical-doc range and deferred timeout. |
| 5m v2, 22:58 | First three issues clarified; NO-GO remains for mandatory O2/O4, post-build doc refresh and non-skipped release evidence. “Deferred, approved by GPT” is not authorized for O4. |

### Runs, in supplied order

| Run / source lines in G6 | What can be accepted; what remains |
|---|---|
| Earlier M5 build d17f82f / anchor pin c730dd5, m5-report.md:18–24 | Reported offline implementation and owner-supplied anchor corrections; not a successful live plan. Original live batch exited 6, zero Meta calls, page requests conservatively four; no traces. |
| 5c BYOK, G6:18–45 | 82353ee + cf12140, 460 reported tests, isolated cloud output and frozen local APK. Money removal/development-log work reported complete; incorrect links and later O2/O4 findings prevent a blanket release approval. Separate folders alone did not prove parallel non-interference. |
| 5e resume, G6:47–53 | Owner explicitly waived clean-tree start to preserve interrupted edits. Persistent report location is good. Absence of diag files is not evidence that no request was attempted. |
| 5d diagnosis resumed, m5-report.md:450–550 | Two recorded requests, zero Meta calls. Actual marker was DevPro__enable_devsite_captcha, not a reCAPTCHA script. Missing entity-decoded anchor correctly caused STOP under the original instruction. |
| 5f, G6:55–67 | 17b1be8, 706 reported tests. Owner separately authorized entity decoding; no anchor re-pin. Shared detector/once-only decoding and saved-body tests reported passing. Fetch failure traces added; anchor failure trace and portable fixture coverage remained incomplete. |
| 5g live, G6:69–76 | Four HTTP Meta sends and four page requests, not two sends. All four empty/length; two live exits 5, two missing-trace replay exits 6. No successful model decision or replay. Keep this failed evidence. |
| 5i diagnosis, G6:78–95 | Corrects attempt accounting and explains the reply-handling gap. Rebuilt prompt used earlier saved bodies; its size is an estimate of the live prompt, not a retained exact live request. Anchors were still in Rules. |
| 5j, G6:97–111 | 0f3ef23, 713 reported tests with one existing skip. Empty/non-stop model messages enter I-FORMAT/one repair; usage/failed-call traces improved; shared M2 behavior reportedly unchanged. Remaining exit-6/fixture gaps belong in 5l. |
| 5k, G6:113–127 | f7e080d, cloud out-byok2/6ecb88e0, local unchanged. Corrected URL constants; proof sheet/test still selected out-byok/f4d6798d. 460 passing tests did not catch that mismatch. |
| 2d M5 review, G6:129–145 | Useful offline corroboration; accept its trace/fixture findings. No independent successful live artifacts were produced. |
| 2f preflight, G6:147–167 | Useful pinned paths, certificates, merge/space inventory. Static test-definition counts are not executed suite totals. Its “live hasn't happened” statement is stale: the appended report records the failed live run. Port searches and old free-space readings do not prove current availability. |
| 2h BYOK review, G6:169–185 | Finds stale proof pin and real O2/O4 risks. Reclassify those two from Optional to Must fix; “overall passes” must not hide the explicit deadline exception. |
| 2i preflight round 2, G6:187–198 | Explains why two old test hunks cannot be retained literally. Does not authorize discarding later Part-A tests or checking a sibling APK instead of consumed input. |
| Preflight round 3, preflight-3.md | Whole-section measurement supports 642/2553 chars; exact counts remain reported, not independently reproduced here. Fresh matching beats stale stored anchor-found flags. |
| 2l M6 code review, G6:201–217 | Accept P1 fresh-only, P2 explicit fresh inputs, H1 remove Files INTERNET. Reject start-work-before-marker wording. Tool-invoking single tests need serialization. Static checks do not replace runtime evidence. |
| 5m preflight, 5m-preflight.md | Helpful v1-to-v2 clarification. Its suggestion to defer O4 does not satisfy the existing 60-second requirement. No 5m build/result is yet supplied. |

## Primary-source checks

- [Meta reasoning documentation](https://dev.meta.ai/docs/reasoning) and [Chat Completions contract](https://dev.meta.ai/docs/protocols/chat-completions), checked 3 Nov: reasoning consumes output allowance; max_completion_tokens is supported, max_tokens is its deprecated alias; top-level reasoning_effort supports low. None is not supported for Muse Spark. This supports the proposed bounded trial; it does not diagnose the unrecorded usage of the four failed calls.
- [Java URLConnection](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/net/URLConnection.html#setReadTimeout(int)): read timeout waits for data availability, not a whole-question wall-clock deadline. The required absolute deadline follows from the project's 60-second contract.
- [Android Settings.Panel](https://developer.android.com/reference/android/provider/Settings.Panel): internet panel added at API 29; guard it for the declared API-28 minimum.

No model answer, phone flash, cloud proof, or completed M6 integration is certified by this review.
