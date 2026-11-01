# ChatGPT re-review: M3 strategy and fit engines, v2.1

Reviewed PR #28 at `839141259cf72a1168e9859438e2ebd36b1bedf6` on 1 November 2026. **Verdict: approved.** This supersedes the change request in [the v2 review](2026-11-01-chatgpt-m3-strategy-fit-v2.md).

**Must fix: none remaining.**

- **M4 receives and enforces the decision.** The handoff now includes the selection result, refusal reasons, input provenance and `build_allowed`. M4 must validate the whole plan, reject inconsistent decisions and stop refused plans before any build step. The specification requires tests for the accepted/refused Files-only pair, mismatched decisions and `refused` paired with `emulator_only`.
- **Scope remains explicit.** Both fits and unconfirmed plans allow only emulator work; unconfirmed work stays labelled as an experiment. Image capacity and other unresolved checks remain visible. No plan authorizes a real-phone installation.
- **The two smaller corrections are complete.** App modules and their concrete requirements belong to M4. Assistant app storage and model bytes are counted only when Assistant is selected.

The previously accepted strategy, unlock, model-selection, provenance and exit-code corrections remain intact.

**Optional editorial cleanup:** add `build_allowed` to the top-level field summary in §6. The subsequent validation rule and tests already require that top-level field; implement it in the schema as specified there.

After owner merge, the Muse prompt should pin the reviewed M2 checkpoint, retain the stated validation requirements and existing install/network/commit limits, and carry the M4 consumer rule into the full M4 spec.

This approves the specification. Product implementation, test results and live validation have not been verified in this review. No installs, builds or inference calls were performed.
