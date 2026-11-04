# StarGate round 5 review

Reviewed 4 November 2026. PR #36 at 1ba318c02637b6d4eb4cdfcc35b11ba790d98fe2; both new commits reviewed separately: 6b0ebc445c4469de54c45b0384b16f7ef44dfd24 and 1ba318c02637b6d4eb4cdfcc35b11ba790d98fe2.

R5 line numbers below refer to the supplied `Pasted text(3).txt` (143 lines). Repository line numbers refer to the reviewed head. This is a planning/prompt review. Product source, new APKs and new Mac runs were not available; earlier product measurements and test counts remain attributed to the supplied reports. No product build, device operation, inference or diagnostic Android-page request was performed.

| Item | Verdict |
|---|---|
| 1. PR #36: M6 prompts and M5 v2.2 | APPROVE / GO to merge. |
| 2. Box 5l v2 | GO for the offline implementation after PR #36 is merged and PLAN_V22_SHA is filled. |
| 3. Fix 5m v3 | GO for the offline fix and cloud APK build, with the existing Now-track handover. |
| 4. M4c live-proof v2 | GO on the design; NO-GO to paste/run until the reviewed 5m tip and APK hash replace the placeholders. |
| 5. Grok round 4 | GO to edit the media package. Publication still depends on the actual proof and final files. |

## 1. PR #36 — APPROVE

**Must fix:** none remaining in this planning change.

Commit **6b0ebc4** addresses the three round-4 blockers:
- `m6-part1-platform.md:41,51`: fresh launcher/Files APKs for the current plan/build ID, explicit in-process image inputs, embedded config comparison, and frozen-output checks. Fresh-only Part 1 is safe; no missing provenance is invented to reuse M4.
- `m6-phone-a-link-files.md:51,54` and `M6-app.md` section 6: Files requests zero permissions; its signature permission declaration is checked separately.
- Platform `:25`, phone `:23`, safety `:29`: individual tests invoking Android tools are heavy work. Mark-before-launch, one launch, verified group identity and retained uncertain markers preserve the handover.

The API-29 fallback, static/runtime distinction, deferred chat tests and honest Research placeholder are aligned. Part 1/Phone A still start from the fixed M4 base, do not consume moving M5/BYOK tips, and keep separate outputs. Parallel work is acceptable under the stated resource and Now-track rules; it is not permission for simultaneous heavy jobs. Combined M6 runtime proof remains pending.

Commit **1ba318c** resolves the M5 design blockers: lossless sections, deduplication, canonical ranges, exact sent text/hash/version, single-range quotes, replay validation and one end-to-end deadline. The corrected history no longer claims the model never received the anchor sentences. Whole sections, 8192 tokens, low reasoning and 180 seconds are approved as a bounded trial, not a success guarantee.

**Should fix (non-blocking):**
1. `m6-parallel-safety.md:55`: label the tool-name grep as a diagnostic hint, never evidence sufficient to clear an unknown marker. It misses processes such as the Python image builder, debugfs and zipalign. Recover the recorded command/start-time and process identity; if job completion cannot be established, leave the marker. This clarifies the already binding rule at `:37`.
2. `M5-real-phone-plan.md:34`: replace “the fetched pages” with “the selected excerpts” to match section 1. At `:118`, remove the obsolete M4c “$5 recorded” budget. At `:136`, say “different cited results”; the named budget fixture can legitimately produce `do_not_install`, as `:144` already allows.

**Optional:** none needed for this round.

## 2. Box 5l v2 — GO offline

**Must fix:** none. R5:21–28 incorporates the earlier corrections, including owner-prefetched planning data, non-skipping fixtures, unchanged M2 outputs and the two historical corrections. The prompt matches M5 v2.2. Keep the actual merge SHA, clean product start and fresh owner go for any v3 live batch.

**Should fix:** R5:24,26–27: explicitly test replay of both newly recorded anchor/excerpt failures, reproducing the original exit **and reason** without network. Preserve 5j's 0/5/7/10 replay cases. An extraction failure has no successful excerpt: represent that failure and its version explicitly rather than requiring a fictitious excerpt or reducing its replay to a generic unsupported-version error. The recorded source body must remain available for successful excerpt reconstruction. This makes the required failure-trace behavior unambiguous; it does not add a new live-run requirement.

**Optional:** define ranges as half-open Unicode code-point offsets and include the gap markers in the exact sent-text hash and character cap. Keep the existing one-time entity decoding and apostrophe normalization.

Meta's current [Chat Completions parameters](https://dev.meta.ai/docs/protocols/chat-completions) support `max_completion_tokens` and top-level `reasoning_effort="low"`. Its [reasoning documentation](https://dev.meta.ai/docs/reasoning) confirms that reasoning consumes the output budget and that `none` is unsupported for Muse Spark. These documents support the request shape; they cannot establish that the next run will succeed.

## 3. Fix 5m v3 — GO offline

**Must fix:** none. R5:40–41 now requires the O2 single-send fix and an actual shared 60-second deadline in both implementations. R5:47–51 orders new cloud build, manifest binding, proof documentation and APK-backed release checks correctly. Frozen local/history artifacts, extracted-entry scans and dummy-key-only filming are preserved.

**Should fix:** R5:41: make the existing “no late answer / no overlap” requirement explicit in the tests too: a late callback cannot overwrite the timeout, and a second question cannot overlap a still-running first transport. Merely freeing the busy flag is insufficient. This is an acceptance detail for the behavior already required, not a reason to defer the fix.

**Optional:** O5 can remain deferred as written; it does not introduce another send. Report static password-field evidence separately from the later dummy-key Mac proof.

This approves the fix prompt, not the resulting APK. Review the actual 5m report and binding checks before using it in item 4.

## 4. M4c live-proof v2 — design GO; execution HOLD

**Must fix before execution:** R5:59,77,83: fill FILL_5M_TIP and FILL_5M_SHA only from the completed, reviewed 5m handoff. This is already an explicit prerequisite, not a new design defect.

The M4 base plus reviewed BYOK merge is appropriate for this standalone proof. The actual-pair conflict check, real consumed-input test, fresh launcher/Files inputs, measured fit, historical local-image revalidation and extracted APK scans address the earlier blockers. Keep the local-input test specific to the default/local path; the cloud path must bind to the cloud snapshot.

**Should fix:**
- R5:57,59,63,82,95: remove active references to “after 5c,” filled 5k pins, and out-byok2 being current. Describe these only as history. The active prerequisite is reviewed 5m/out-byok3; do not undo 5m's corrected proof doc.
- R5:78: if the target object is absent, fetch it by local path before `merge-tree`, then perform the exact-pair checks. Keep the stop on any additional conflict.
- R5:98: explicitly **Save** the dummy key before restarting, checking the last-four display and deleting it.

**Optional / decisions:** one question per provider with its one possible automatic retry is an adequate bounded proof attempt; it does not guarantee usable footage. Reserve both sends first, skip a provider with insufficient development allowance, reconcile uncertain sends conservatively, and retain the fresh owner Mac go. Hand entry into the masked app field with recording stopped, save/clear and clipboard cleanup is appropriate for this scoped proof; it is not a claim of universal screenshot/clipboard security.

## 5. Grok round 4 — GO to edit

**Must fix:** none in the correction prompt. R5:134–142 addresses emulator location, unproven UI screens, recording-specific answers/timings, product-claim attribution, conditional credits, narrower verification claims and genuine M5 outcomes.

**Should fix:** R5:138: allow the mixed proof states too (A passes/B fails, or B passes/A fails). Choose claims, shots, captions, diagram and credits consistently for the evidence actually obtained; a failed A does not require dropping a proven B.

**Optional:** R5:141 is a good pace instruction: speak naturally and give viewers reading time. A shorter honest cut is fine.

The round-4 output files have not been supplied, so this approves instructions to Grok, not an unseen final package or its updated counts. “Never narrate pending” means use the truthful fallback or omit the claim; it never licenses an unproved success claim.

## Version reconciliation

The [3 November review](2026-11-03-chatgpt-night-batch.md) remains the historical record; no earlier failure is erased.

| Earlier version | Round-5 disposition |
|---|---|
| M6 rounds 1–3 | Retain the prior reviews and resolved findings, including the reproduced unsafe marker cleanup. |
| M6 round 4 at d63131c | Its three blockers are now addressed by 6b0ebc4. |
| M5 v2.2 initial ±2-block draft, later whole-section draft, and 5l v1 | Preserve the omission/history findings. 1ba318c and 5l v2 replace the faulty contract; they do not retroactively validate the earlier runs. |
| 5m v1 and v2 | Remain NO-GO historically; v3 promotes O2/O4 to required fixes and corrects build/doc/release-check order. |
| M4c live-proof v1 and its 5c/5k repins | Retain the change log; v2 waits for the reviewed 5m artifact instead. |
| Grok rounds 1–3 | Earlier supplied outputs/instructions remain reviewed as previously recorded. Round 4 authorizes corrections; its eventual files still need checking. |
| M6 join / platform Part 2 / phone Part B | Parked, as requested. No new approval until the named prerequisite results and revised join prompt exist. |
