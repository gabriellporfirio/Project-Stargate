# PR #35: M4c v2.5 re-review

Reviewed `b7f3a449f3677e5943caa2788b0ed5f28f30decd` on 2 November 2026.

**Verdict: approve. No remaining must-fix or should-fix items.** Compared the correction with the previously reviewed spec, read the full resulting M4c v2.5 spec, and checked the response on the original thread.

All five review items are addressed:

1. **Development preflight — resolved (§6, lines 86–92; §7, line 112; §8, line 129).** The five-send limit is explicitly an owner-run development procedure, separate from the product. Codespace sends require a saved `planned` row first. Phone proof pauses other development calls and records two planned sends per provider/mode before starting. Planned rows count against the limit; uncertain sends are never returned. Reconciliation is required before further live work, and a planned row is removed only with evidence that no send happened. The four-already-used case is explicitly refused and required in the tests. The committed log preserves totals across restarts and fixups.

2. **Retry policy — resolved (§6, line 94; §7, line 113).** Hard billing/quota refusals are separated from transient 429 responses. The two-send maximum applies across application and HTTP-client layers, waits over ten seconds prevent a retry, and the sixty-second deadline includes waits and retry.

3. **Input boundary — resolved (§7, line 107).** Characters are Unicode code points. The tests distinguish the accepted 2,000-code-point/8,000-byte boundary from rejected 2,001-code-point and 8,001-byte inputs.

4. **Removal scan — resolved (§7, line 114).** The check targets active pricing fields, calculations and cost/share gates, with explicit exceptions for removal documentation and negative tests.

5. **Follow-up handoff — resolved (§6, line 97).** Java, Python, obsolete tests, builder integration instructions and Mac proof steps move together. The cloud APK gets a new output folder and fresh manifest/hash; the builder's approved local `1936549b…` artifact remains untouched.

The owner's bring-your-own-key decision remains intact: no product money tracking or per-build phone share. Per-request caps, one question at a time, the fixed open-weight ID and development send counting remain.

This approves the planning spec. The implementation fixup, offline verification and owner-run live proof remain to be completed; no product implementation or live calls were executed in this review.
