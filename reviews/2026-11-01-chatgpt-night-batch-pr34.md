# Night batch item 1: PR #34, M5 and M6 v1

Reviewed `9dcc8c2f568e50152b69e6a6ff10929442170867` on 1 November 2026.

**Verdict: request changes.** The cable-first scope, separate Assistant transport, model choice and owner-authorized after-boot model delivery are accepted directions. The following specification gaps remain.

**Must fix — M5 acceptance is too weak (lines 47–58).** A locked-phone draft can order check-OEM → flash → unlock, yet pass the listed ordering rules. Require a closed partition allowlist and explicit mode/unlock state transitions, with flashing permitted only after established prerequisites. Unknown/conflicting critical facts must stop the actionable sequence or produce a conditional, unconfirmed plan; a `check_is_logical` step without a result cannot authorize a later unconditional flash. Preserve the already-unlocked case even when new unlocking is unsupported. Bind the supplied profile's hash to the M3 plan, not just its phone name. Require nonempty, rule-linked citations. A generic two-page routing proposal must not be advertised as a validated handset installation procedure: image compatibility, signing and other M7 prerequisites remain unresolved. [Android's fastbootd reference](https://source.android.com/docs/core/architecture/bootloader/fastbootd) explicitly requires an unlocked device for flashing.

**Must fix — the second source leaves the allowlist (M5 lines 16–20).** `/docs/setup/build/running` currently redirects to [`/docs/setup/test/running`](https://source.android.com/docs/setup/test/running). M2 rechecks redirect targets, so the proposed exact-path allowlist rejects it. Pin the canonical page and retain the two-request budget; test the requested/final URL policy.

**Must fix — M6 composition and stale-output handling (lines 17–33, 49–54).** M4 supports Assistant-only builds without Files, but M6 puts the sole Link server inside Files. Define a base transport component or another explicit selection-aware arrangement; an unselected Files service must remain absent. Also bind every displayed report, M5 plan, build and replay to the current profile/selection and their hashes. Re-run M3 after research changes its inputs, invalidate dependent outputs, and block Build for stale or refused plans. Merely rendering a real file is insufficient.

**Must fix — browser request boundaries (M6 sections 1–2).** Specify browser authentication/access-code handling, state-changing POSTs, origin/CSRF protection appropriate to that authentication, host/CORS restrictions, escaped model/source text, bounded chat requests and serialized generation. Test foreign-origin requests and injection. Loopback and a private forwarded port do not replace these checks; see [OWASP's CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

**Must fix — replay equality (M5 lines 65, 72, 90).** Live and replay outputs have different `provenance`. Define equality of the decision payload with explicit run-metadata exceptions; retain the replay label.

**Should fix:** Reconsider 2048 completion tokens given the earlier truncation evidence. Specify shared signing-certificate verification and owner-run positive/negative bound-service tests; permission assertions must distinguish local and cloud variants. “Spark Open already on camera” is premature: M4c live proof is pending.

Companion reviews cover [fixup 4](2026-11-01-chatgpt-m4b-fixup4-report.md), [M4c](2026-11-01-chatgpt-m4c-part1-report.md), [M4a](2026-11-01-chatgpt-m4a-part2-and-part3.md), and the [M5 prompt](2026-11-01-chatgpt-m5-build-prompt.md). Documents/reports reviewed; no product execution.
