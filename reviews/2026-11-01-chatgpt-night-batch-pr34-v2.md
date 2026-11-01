# PR #34 night batch re-review

Reviewed `d06eaee07bd4897473b25dcd91bc61a699c155c1`, M4 v2.3, M5/M6 v2 and the two attached Muse prompts.

**Verdict: request changes for three remaining specification items. M4's revised contract and Part 3 prompt are approved.** Fixup 4 and M4c retain their earlier scoped approvals; no new implementation evidence was supplied.

**Resolved:** canonical source/request budget; profile hash binding; flash-before-unlock ordering; closed partitions; limited-proposal labels; replay equality and token/call limits; Assistant-only composition; stale-output invalidation; the specified browser protections; explicit after-boot payload validation and separation of build readiness from Mac completion.

**Must fix 1 — finish M5's unknown-prerequisite contract (§3, lines 61–79).** `I-UNKNOWN` stops an unknown-lock plan after `check_oem_unlocking`, but the table permits `stop_for_check` only after `check_is_logical`. Specify one legal terminal representation for each unknown case and test unknown lock, unknown dynamic partitions and both together. Separately, locked=true with OEM support/permission unknown can still pass check → warning → reboot → unlock → flash: the table promotes unlock to success and `I-UNLOCK` only requires an availability warning. Require unresolved unlocking prerequisites to end unconfirmed without unlock/flash, or define an explicit conditional continuation that cannot be marked accepted. A listed check is not its observed answer; preserve the already-unlocked exception.

**Must fix 2 — distinguish source facts from project policy (M5 line 53).** Requiring an exact sentence from these two Android pages to justify *every* rule is unsatisfiable for `I-FORMAT`'s provider `finish_reason`, the schema and the project's system-only scope. Mark policy/schema rules as such, with local policy references; require fetched anchor quotes for Android facts. Keep exact source checks and relevant step citations. Do not invent or attach unrelated Android quotes to internal rules. Carry this correction into M5 prompt Step 2.

**Must fix 3 — scope the signing check (M6 §2b).** “Every app in the image” includes stock Android packages. Limit certificate equality to the included project packages: launcher, Link, Files and Assistant. [AOSP uses several signing keys](https://source.android.com/docs/core/ota/sign_builds); do not re-sign stock APKs to satisfy this check. Test a project-app mismatch fails while differing stock certificates are allowed.

**Should fix:** make authentication bootstrap exceptions explicit (opening a token link currently changes state despite “GET never changes anything”); use full origins, including schemes, rather than comparing Origin to raw Host values. Put Link code/start/stop controls in a base screen available in Assistant-only builds, and revoke sessions on code renewal/stop. Specify streamed file transfer over Binder: [its shared transaction buffer is 1 MB](https://developer.android.com/reference/android/os/TransactionTooLargeException), below the 50 MB Files limit. Correct M4 §4d's “free space”: 305,967,104 B was total capacity; reported free space was 901,120 B.

Companions: [Part 3 v2](2026-11-01-chatgpt-m4a-part3-v2.md), [M5 prompt v2](2026-11-01-chatgpt-m5-build-prompt-v2.md). Specification review only; no product execution.
