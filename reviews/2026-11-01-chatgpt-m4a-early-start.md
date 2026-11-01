# ChatGPT review: M4a early start (M4 spec v2.2)

Reviewed PR #31 at `cb3024f006990965968e841579a52a24ead5f77a` on 1 November 2026.

**Verdict: approved for the owner's merge. No must-fix findings.**

The sequencing change is consistent with the approved M4 contract:

- Part 1 contains shared work that can be implemented and tested before a route is chosen: plan validation, Assistant-manifest binding, the build schema, APK/model-folder inspection, section 7 corrections, and the launcher and Files apps.
- Part 2 still requires the spike's recorded Mac result. Route packaging, Route A image checks, the two demo builds and the Mac proof remain behind that decision.
- Moving the recorded spike merge to the first Part 2 commit is coherent with the spike's isolated source paths. M4a remains the sole integrator, and the full tests, artifact checks and demo builds still run on the combined commit.
- File ownership, approved manifest handoff, install approvals, read-only shared tools, one Android build at a time, and the shared resource/network limits are unchanged.
- Master plan §7 records the same split.

Part 1 passing does not select a route or establish that an image boots. The existing route decision, artifact checks, owner-run Mac evidence and complete/partial/blocked criteria still determine the M4 result.

After the owner merges this PR, Claude can issue the bounded Part 1 prompt to the builder Muse while the Mac spike result is pending. No additional scope is needed.

Specification review only. I checked the diff against the full M4 spec, spike spec and prior M4 approval. No installs, product tests, builds, emulator commands or live inference calls were performed.
