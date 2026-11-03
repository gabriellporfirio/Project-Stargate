# PR #36 round 4 review
Head reviewed: d63131c8f7ca94b848423e7b9f9c2375fefb0eb7. Verdict: REQUEST CHANGES.

The round-3 dead-helper cleanup finding is fixed: the owner loop no longer deletes markers automatically. The earlier reuse and runtime-proof corrections remain intact. The supplied read-only code review exposes these additional prompt issues.

**Must fix**
- Platform prompt:41: build launcher/Files for the current selection/build ID into the platform's own output/tools folders, then use the existing in-process builder with explicit inputs. Otherwise the reported default CLI inputs retain M4's baked launcher ID. Check launcher config against the resulting manifest.
- Phone prompt:51,54: explicitly remove Files' requested INTERNET permission. M4 permits it, so “none beyond M4's” contradicts “only Link/cloud Assistant.” Test zero requested permissions separately from the Files service's own signature-permission declaration.
- Platform:25 / phone:23: classify single tests invoking aapt2/d8/build tooling as heavy. The supplied review identifies interference with build_apps.sh's process guard; “small test” is not a safe exemption.

**Should fix / decisions**
- P1: approve fresh-only Part 1. Do not weaken reuse to accept old images lacking check/provenance evidence. Defer new shared manifest fields, or assign one owner explicitly.
- Safety:31–32,52 and G6:211: reject starting work before its marker. Mark first, recheck the flag, launch once, then atomically record the verified group identity. Unknown/malformed identities or failed process checks block cleanup. Keep the dead-child regression test.
- Guard the API-29 settings panel for minSdk 28. Label static listener/layout tests accurately and retain Mac runtime proof. Explicitly defer chat limits to Part B. Missing M2 replays show the honest placeholder; no invented input-hash binding.
- Update the Now-track table. Shared machine resources prevent an unconditional “no interference” claim.

**Optional:** worker limits can be conditional on Gradle being used.

Fixed-base worktrees, browser rules, streaming and the partial-stage split otherwise match M6 v2.1. This review approves neither a combined Files+Assistant runtime proof nor any live calls. The full batch review preserves every supplied version and the three requested decisions: [batch review](2026-11-03-chatgpt-night-batch.md).
