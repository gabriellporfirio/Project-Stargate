# Night batch item 5: M5 build prompt

Reviewed the supplied prompt against M5 v1 in PR #34 at `9dcc8c2f568e50152b69e6a6ff10929442170867`.

**Verdict: changes required before sending.** The owner-gated live runs, no-device execution rule, reusable M1–M4 code, recorded traces and no fabricated rejection are sound.

**Must fix 1 — use a coherent starting commit.** `95e2547` has the reported failing Assistant APK/manifest test, while the shared APK now belongs to `e90edfa`. M5 cannot promise the full suite stays green on that mismatched baseline. Start from the builder's reviewed, green combined commit after merging `e90edfa` (the Part 3 Step 1 checkpoint), pin its full SHA, and keep M5 in its separate worktree. M5 need not wait for Part 3's image work to finish. Do not weaken or skip the binding test.

**Must fix 2 — carry the corrected M5 spec into the prompt.** Wait for PR #34's revised approval/merge. Include the canonical Android source URL, bounded redirect policy, closed partitions, stateful ordering/unlock checks, unknown-fact handling, profile/plan hash binding and rule-linked citations from the PR review. Do not implement the current permissive rules merely because their IDs are listed. The output is an unexecuted, limited routing proposal, not proof that an emulator image is installable on a handset.

**Must fix 3 — define replay equality honestly.** A live result and a replay cannot be identical JSON when one says `provenance: live` and the other `replay`. Compare the deterministic decision payload and preserved input/trace hashes, with an explicit list of allowed provenance/run-metadata differences. Keep the replay label and guarantee zero network/process/device activity during replay.

**Should fix:**
- The prompt correctly checks the actual fixture instead of assuming old32 has known-false dynamic partitions. Make the spec's tests and done-when use the same chosen, named eligible second fixture; never alter a fixture to manufacture the demo.
- Pin and reject malformed, truncated or non-stop model responses before accepting a draft. Use the earlier 4096-token experience when choosing the revised cap; do not silently exceed whichever budget the merged spec approves.
- State an aggregate ceiling for the two owner-authorized runs: six Meta attempts and four page fetches at most under the current per-run limits, including retries, with replay using zero. Record usage and real rejections.
- `do_not_install` and incomplete/unknown results should be demonstrable outcomes, not retried until the desired screenshot appears.

This reviews the prompt only; M5 has not been implemented or executed here.
