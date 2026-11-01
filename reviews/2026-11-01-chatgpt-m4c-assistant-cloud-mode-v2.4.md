# ChatGPT re-review: M4c Assistant cloud mode v2.4

Reviewed PR #30 at `4707d0a008b6a66d5f71e3c8db2f44de0657c42f` on 1 November 2026.

**Verdict: approved for the owner's merge. No outstanding must-fix findings.**

The remaining budget-policy finding is resolved:

- The default reservation uses the corrected **32,768-token estimate** for the 16,384-byte request-body cap.
- Section 6 explicitly distinguishes the $5 Baseten/$2 Meta ledger allowance from actual provider charges. It acknowledges charges above the estimate, including billed requests with a timeout or missing `usage`.
- The one-request-overshoot and account-protection promises are removed. The five-attempt cap, input/output limits, pre-dispatch reservations and stop on an observed overrun remain.
- The phone-share summary, completion checklist and master plan §7 now reflect the estimated policy, with the owner's after-run billing readings recorded alongside the ledger.

Read the ledger limits as pre-dispatch admission checks: if later usage exceeds a reservation, record the full cost and stop that provider as §6 requires. An overrun must never be hidden by capping the recorded value.

All previously closed findings remain closed: APK variants and artifact checks, provider-specific requests and credential routing, key storage and backup checks, history isolation, retry rules and shared attempt accounting.

Merging approves the optional Baseten-key exception and the explicitly estimated budget for this bounded demo. M4c still starts after the local Assistant works, stays within its four-hour time-box and does not delay the core demo.

This approval covers the specification, not proof that Muse's implementation passes it. Implementation tests and owner-run emulator evidence remain required. No installs, product tests, builds, emulator commands or live inference calls were performed in this review.
