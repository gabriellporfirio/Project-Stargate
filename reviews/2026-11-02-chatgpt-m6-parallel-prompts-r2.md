# PR #36: M6 parallel prompts re-review

Reviewed `b69c5dfab31de2a959ae22241b35fdcca971a009` on 2 November 2026 against the previous review, M6 v2.1 and the applicable M4 requirements.

**Verdict: request changes — one remaining must-fix.**

**Fixed:** Build reuse now requires the full plan gate, build-v1 validation, matching current handoff/app composition, actual artifact sizes and hashes, and contents-check evidence tied to the bytes and build provenance. The matching-plan negative tests and explicit M4-generation label cover the earlier issue. Runtime listener and binding evidence is correctly deferred to the owner Mac proof, attributed to project packages, and marked pending; phone Part A does not claim the combined §7 proof. The role/Part labels, output-path preflight and owner-only planning fetch also address the earlier should-fixes. Lock-before-measure, complete peak accounting plus the 5 GB reserve, and worker/heap limits are corrected.

**Must fix — finish the quiet-window handover** (`plan/prompts/m6-parallel-safety.md:26,41`; both prompts' independence blocks).

Creating `/workspaces/.now-track-busy` prevents only future image-build/full-suite starts. It neither drains work already running nor prevents a worker that checked the flag before waiting for the build lock from starting afterwards. Standalone APK/Gradle builds are also outside the written flag rule. Thus an Ahead suite/build can still overlap M5's timed live run even after the owner follows the documented `touch` step; `nice` does not reserve memory or disk bandwidth.

A small owner/Muse handshake is sufficient:
- Set the flag, then wait for **both** Ahead Muses to acknowledge that any in-flight heavy build or full suite has finished and they are paused before starting the Now task. Do not kill a build mid-write.
- While flagged, prohibit all heavy build stages (including standalone Android/Gradle builds and compression) and full suites. Recheck the flag after acquiring the build lock and immediately before launch; release it and pause if flagged.
- Resume only after the owner finishes and removes the flag. Put this sequence in the safety note's owner steps and both pasted prompts. Check the cases where the flag appears during an active suite/build or while a worker waits for the lock.

**Should fix:** none remaining beyond that handover.

The dependency split and revised reuse rule are otherwise suitable for these partial stages. This is a document review; no product builds, tests, diagnostic requests or Meta calls were run.
