# PR #36: M6 parallel prompts review

Reviewed `68633b54649d8f4766a071b61a264e7de4cb180d` on 2 November 2026. Read the parallel-safety note first, then both prompts, the mockup README, M6 v2.1 and the applicable M4 requirements.

**Verdict: request changes.** The dependency split is sound: fixed-base worktrees, no current-branch merges, M5 placeholders, Files-only phone proof and a deferred Assistant handoff avoid a hard dependency on unfinished M5/BYOK work. The browser, streaming, signing-scope and branding instructions broadly match M6 v2.1. The mockup README correctly makes the spec authoritative. Shared-host non-interference and build reuse are not yet established.

**Must fix:**

1. **Reuse needs more than the plan hash** (`m6-part1-platform.md:41`; M4 §5/5a, M6 §1a). The same plan can refer to a missing/corrupt artifact, an obsolete Assistant handoff, or an old M4 image without Link after integration. Run the full plan gate on reuse; validate the build manifest and current handoff/component expectations; verify actual image, compressed-transfer artifact and model-payload sizes/hashes; require evidence of successful applicable contents checks tied to those bytes. Match build provenance/component generation too. Add negative tests for an unchanged plan with changed bytes, a stale handoff and an incompatible app set. An M4 image can serve Part 1 only while explicitly identified as that generation.

2. **Bound shared resources and give current work priority** (`m6-parallel-safety.md:23–26`; both prompts' independence blocks). Separate worktrees do not isolate CPU, RAM or disk. The second Muse later builds BYOK, and the builder may need a Mac fix. Acquire the shared lock before measuring free space; check the remaining peak, including scratch, payload copies and gzip, plus M4's 5 GB reserve. Validate the stated 2.5 GB estimate against that complete peak before treating 8 GB as sufficient. Retain M4's build-worker/heap limits. Define scheduling so Ahead heavy builds/suites pause during current live-run or urgent-fix windows, rather than promising no interference from the build lock alone.

3. **Manifests cannot prove the only listener** (`m6-phone-a-link-files.md:51,54–56`). Manifest checks prove declared permissions, not running sockets ([Android INTERNET reference](https://developer.android.com/reference/android/Manifest.permission#INTERNET)). Keep static checks and host behavior tests, but require process/package-attributed listener evidence and actual positive/negative binding results in the owner Mac proof. Mark these runtime results pending beforehand. Scope “only Link” to our project apps.

**Should fix:**
- Correct the platform introduction's stale “second Muse after M5” assignment and align the Part 2/Part 3 labels with the parallel-safety schedule.
- Verify inherited build/test scripts direct intermediates, cleanup and outputs to the owning worktree/tools folder before any suite/build can touch frozen outputs. Fetch the pinned planning revision once before launching both workers, then read it without concurrent shared-repo writes.

Approval of either partial stage must not imply completion of M6 §7's combined Files + Assistant proof. No product code or runtime tests were executed.
