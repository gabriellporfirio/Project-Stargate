# Night batch item 3: M4c part 1

Reviewed the supplied offline prompt/report for `027e77d8f92af194a16ce7dc273236525878d090` and `e90edfaf9354c1e1ea6c08e8256c176dcb964c29` against M4c v2.4.

**Verdict: approve the offline checkpoint and its local-variant integration. This is not approval of live cloud operation or M4c completion.**

The report covers the intended app-side scope: separate permission sets, provider-specific request fields and credentials, current-question-only cloud requests, Keystore storage, backup exclusions, offline tests and deferred builder integration. Null prices and no live calls are appropriate for this part. The Baseten test's Assistant-only exception follows the approved policy.

The builder should use the local APK at `1936549be6da213eb543be672a20fbf5f74c4f2a03de61939d4bbb1a1a95c187`, 24,777,688 bytes, with the matching manifest from `e90edfa`. The supplied permission read-back says no permissions; the reported cloud APK is a different hash and requests INTERNET.

**Should fix before the live handoff:**
- Say explicitly that filling in prices alone does not activate the existing cloud APK. Live proof requires the builder's reservation-before-build integration, a fresh build ID, the baked priced-model allowlist and reserved share, then the owner's go-ahead. Confirm that an APK made without a valid reservation/allowlist cannot send anything. This phone-side condition is not established merely by demonstrating the codespace's null-price gate.
- Clarify the report's “asked-wait capped at 10 s” wording. Spec §3 requires **no retry** when Retry-After exceeds 10 seconds, not retrying after a shortened wait. Include a fake 30-second Retry-After case.
- Confirm gate behavior through the real dispatch/network boundary, including concurrent reservations, restart persistence, oversized response/body and total deadline including retries. A list of function names or source-pattern checks is not runtime evidence.
- Keep the shared signing/APK artifacts tied to immutable hashes. The historical fixup-4 Mac proof does not cover this rebuilt local APK.
- When later enabling builder integration, narrow the NoBaseten import rule to permit the designated cloud-build gate; its blanket “no other module uses m4c” assertion must not force bypassing the ledger.
- Use ordinary questions for live provider proof; an “Answered by the app” device-fact response is not a Meta/Baseten inference result.

The 438 tests and scans remain Muse-reported. Real Android Keystore/backup checks, live provider results, billing reconciliation and builder integration are explicitly pending, not failed or waived.
