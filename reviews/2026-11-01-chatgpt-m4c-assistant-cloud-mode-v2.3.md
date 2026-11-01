# ChatGPT re-review: M4c Assistant cloud mode v2.3

Reviewed PR #30 at `7c96ee2661ef5fa337e0070c411c8f0079025d4d` on 1 November 2026. **Verdict: one budget-policy wording correction remains.**

The arithmetic is now correct: 2 × 16,384 bytes gives the proposed 32,768-token estimate. Choosing the estimated-budget policy is acceptable for this bounded demo, and master plan §7 records that choice. No verified hard ceiling is required under that policy. All other previously closed findings remain closed.

**Must fix — remove the remaining guarantees that the estimated policy cannot support (§6 and master plan §7).**

The new text says the dollar limits can be exceeded by “at most” one request per provider and that an overshoot cannot drain the account. Neither follows from the specified behavior:

- A billed request can time out or return without `usage`. The gate then retains only its estimated reservation and permits another attempt. If that estimate is low, several attempts can cost more than reserved without triggering the usage-based stop. The five-attempt cap still applies; a one-request overshoot cap does not.
- A $5/$2 reservation allowance below the original credit is not a provider-enforced spending cap. Remaining credit can also be lower, which §6 explicitly allows. The spec has not established that unknown charges cannot exhaust it.

**Keep the chosen policy and make the wording consistent:** describe the dollar values as limits on recorded costs plus estimated outstanding reservations; acknowledge that actual spend can exceed them, including across multiple attempts with missing usage; retain the stop on an observed overrun. Remove the “can't use up/drain the account” promise. Qualify the opening “never more” and phone-share “total can't pass the limits” statements so they refer to the accounting allowance and attempt count, rather than guaranteed actual spend. Make the completion checklist distinguish following this policy from proving an actual spending cap.

This needs a focused wording change, not another multiplier or a new billing system. Existing byte caps, priced-model restrictions, ledger allocations, missing-usage handling and tests can remain.

No other merge blockers found. Specification review only; no installs, product tests, builds, emulator commands or live inference calls were performed.
