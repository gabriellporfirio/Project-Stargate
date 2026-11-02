# M5 build prompt v2 re-review

Reviewed the attached prompt against M5 v2 at planning commit `d06eaee07bd4897473b25dcd91bc61a699c155c1`.

**Verdict: changes required only to carry the remaining M5 specification corrections.** The prior prompt-specific blockers are otherwise addressed.

**Resolved:** the baseline is the builder's green combined Step 1 commit after `e90edfa`; the owner fills its full SHA before use. Replay equality now preserves the decision payload with named metadata exceptions. The prompt carries the canonical URLs, profile binding, closed partitions, honest unresolved list, 4096-token cap, aggregate six-call/four-request ceiling and no reruns for a preferred outcome.

**Must fix before sending:**
1. Carry the final approved unknown-prerequisite rules into Step 2 and tests into Step 3: a legal stop representation for unknown lock/dynamic states, and no unconditional accepted unlock/flash sequence based on unconfirmed OEM prerequisites.
2. Replace “each [rule] with … its anchor quote checked against the fetched page” with the corrected distinction between project policy/schema rules and source-backed Android facts. Neither a provider's `finish_reason` nor the project's schema is justified by an Android flashing-page quote.
3. Update the spec-version guard to the final approved revision and wait for its merge, as the prompt already requires. Do not execute against the superseded v2 simply to satisfy the literal version check.

**Should fix:** pin the final approved planning revision as well as `STEP1_SHA`. Run the exact unknown-state combinations as fake-model tests; check that a warning alone cannot turn unknown unlocking eligibility into an accepted actionable sequence.

The named second-fixture selection is now aligned with the spec; fixtures remain unchanged. The live/replay budget and owner-gated Step 5 remain appropriate. Building M5 may run alongside M4's later image work once this corrected spec is merged and the green Step 1 SHA exists.

No source implementation, live model call or product test execution was performed here.
