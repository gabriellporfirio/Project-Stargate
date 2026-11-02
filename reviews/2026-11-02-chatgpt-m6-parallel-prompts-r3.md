# PR #36: M6 handover re-review

Reviewed `dcec74f139ab3a42f893bc03ef031eb9383f290e` on 2 November 2026. Checked the three changed prompts against the previous review; the M6 spec, mockup guidance and earlier resolved requirements are unchanged.

**Verdict: request changes — one remaining failure-path issue.**

The normal handover is now sound: all heavy stages are covered, including standalone APK/Gradle builds, compression and full suites. Publishing the marker before the second flag check closes the queued-worker race, and the owner waits for active work to finish. The earlier reuse, runtime-proof and scope findings remain resolved.

**Must fix — a dead wrapper PID does not prove its job has finished** (`plan/prompts/m6-parallel-safety.md:49–54`; platform prompt line 25; phone prompt line 23).

The owner loop deletes a marker whenever `ps -p "$p"` fails, then prints `CLEAR`. A wrapper can exit or be killed while its child compiler, compression process or test process continues. Both prompts also require unconditional marker deletion on exit/interrupt without requiring the child to have finished. Either path can announce a quiet window while heavy work is still running.

**Verified:** I ran the exact owner loop, changing only its directory to a temporary scratch directory, against a synthetic exited wrapper with a live child. It exited 0, deleted the marker and printed `CLEAR: start the Now task` while the child was still alive. The test child was then stopped and reaped; no project workload was run.

Small correction:
- Remove automatic stale-marker deletion based only on the wrapper PID. An uncertain/dead wrapper must block the handover and require explicit confirmation that its work has finished.
- Remove the marker only after the launched job and its children have finished. On interruption or uncertain cleanup, preserve the marker and report the blockage; do not kill a real build mid-write.
- Test the **owner waiter together with the helper**, including an interrupted/exited wrapper whose child remains active. It must not print `CLEAR` until completion is established. Retain the existing active-job and queued-worker tests.

A manual confirmation for this exceptional case is sufficient; no additional scheduler is needed.

**Should fix:** none. Approval of these prompts still covers partial M6 stages only; the combined Files + Assistant Mac proof remains pending.

Validation was limited to document comparison and the isolated owner-loop probe. No product build, product suite, page request or Meta call was run.
