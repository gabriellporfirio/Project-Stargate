# ChatGPT re-review: M4c Assistant cloud mode v2

Reviewed PR #30 at `82f3a809729e027240da036e56720a28893f1cb3` on 1 November 2026. **Verdict: request two focused corrections.**

The APK variants and permission checks, pinned provider requests, separate credential slots, redirect refusal, error handling, local-history isolation and four-hour time-box address the previous review. Q16 and the optional Baseten-key policy are now clear. Two parts of the original verification and budget findings remain.

1. **Must fix — complete the shared budget gate (§6–7).** The spec promises five attempts across Codespace probes, emulator demos and reruns, but only names a local counter plus a Markdown record. Separate hosts or the required fresh/wiped AVD can otherwise start with separate allowances. Define a durable authoritative ledger outside wiped app data, or fixed non-overlapping host allocations with an explicit handoff. Reserve and persist each attempt before dispatch, including retries/timeouts; restarting must not restore allowance.

   The dollar caps also need a pre-dispatch rule. Recording cost from response `usage` happens after spending and does not enforce $5/$2. Pin pricing for allowed model IDs, reserve a conservative maximum request cost against the smaller of remaining credit and milestone allowance, and refuse unpriced IDs or exhausted budgets. Keep the reservation when a timeout or missing usage leaves cost unknown. Add offline tests for restart/host handoff, retry counting, budget exhaustion before transport and missing usage. Keep this a small validation mechanism.

2. **Must fix — finish the credential verification (§5/7/8).** The no-plaintext-fallback rule is present, but the requested Keystore/encryption-failure test is absent from both test lists. Inject that failure and verify no plaintext credential is persisted and no cloud request is sent. Also replace the bare `adb -s <serial> shell bmgr` acceptance step: [Android documents that no arguments prints the command list](https://developer.android.com/tools/bmgr), not an app's backup eligibility. Specify a per-package check and expected result for the chosen AVD, and inspect the packaged exclusions for both cloud backup and device transfer. Save/restart/delete tests remain useful.

**Optional clarification:** if a 429 asks for a wait longer than the allowed ten seconds, show “try later” rather than retrying earlier than the provider requested.

**Top three:** durable attempt accounting; cost reservation before dispatch; meaningful credential-failure/backup proof. The approved M4 work can continue, and the new time-box correctly protects the core demo.

Specification review only. No installs, product tests, builds, emulator commands or live inference calls were performed.
