# ChatGPT re-review: M1 fixup prompt v3

Reviewed PR #25 at `82d53f162fc3c8ac17b7d43b829a77a7dec8bf5c` on 31 October 2026. **Verdict: request changes — one small interruption-handling fix remains.**

Both previous blockers are resolved: an unset Baseten key is correctly not applicable, and changed code now fails the comparison before committing. Item 4's evidence status is also corrected. The nine fixes, one fixup commit and PR #23 approval policy remain accepted.

**Must fix — reserve the single doctor attempt before launching it (script B, lines 99 and 107).** The repeat guard checks `doctor.rc`, which is created only after the command returns. If the script is interrupted during the call, that file never appears, so restarting B launches another call. Keeping the directory across a restart does not close this gap.

I reproduced this by terminating script B during a local stub doctor invocation: the result file was absent, a second B exited 0, and the stub recorded **two** invocations.

Use a separate persistent started marker, created atomically immediately before launching doctor, after the preflight checks. For example, reserve the attempt with `mkdir "$E/doctor.started" || fail "..."`, and reject an existing started marker on entry as well as an existing result. Leave the marker in place after failure or interruption; an incomplete attempt means stop and report, not retry. Keep `doctor.rc` for the outcome and script C's success check.

I tested that marker change in the disposable harness: the ordinary path still passed; after interruption the second B failed before invocation, leaving the call count at **one**. This is a suggested repair, not an edit to Claude's prompt.

**Checks completed against v3:** normal path without Baseten passes; changed code is rejected; repeating a completed doctor run is rejected; a planted dummy key in evidence is rejected. The remaining failure is specifically interruption before the result file is written.

**Top three priorities:** record the attempt before launch → retain the passing code-identity gate → retain optional-key handling. The latter two are already resolved; no additional scope is requested.

Validation used temporary Git repositories, synthetic command stubs and dummy keys, with only the base SHA and temporary paths adapted. Fixtures were removed. No unpublished product code, real credentials, real inference calls or installs were involved.
