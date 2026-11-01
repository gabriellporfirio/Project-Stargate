# ChatGPT review: exact M4a Part 1 Muse prompt

Reviewed PR #31 at `25a872af7c00e047b0e5bd7592490990a68b809c` on 1 November 2026, including `plan/prompts/m4a-part1-build-core.md`, pinned M4 v2.2 and M3 §6.

**Verdict: the Part 1 / Part 2 split remains approved. The added execution prompt needs two corrections before accepting the Part 1 result.**

**Split check — passes.** The gates, manifest binding, schema, APK/model-directory inspection, M3 corrections and launcher/Files apps can be developed without choosing Route A or B. The prompt explicitly stops before spike integration, packaging, final demo builds and Mac proof. Route-dependent values must remain parameters or fixtures until Part 2.

**Must fix 1 — hash binding (line 29).** The prompt says file hashes must match the plan's handoff. M4 §5a explicitly says that handoff has **no per-file SHA-256 values**. Bind model ID, revision, file names and sizes to the handoff; require hashes in the owner-approved Assistant manifest. Compare actual payload hashes with that manifest in the contents check (exit 8), while missing manifest hashes or binding mismatches give exit 9. Keep M3's schema unchanged and record the Assistant manifest's own hash in the build manifest. Check the implementation with the specified real M3-generated plan and same-name/same-size changed-content test.

**Must fix 2 — live-check invocation (line 44).** The documented command is `stargate plan ... --explain`, not `stargate --explain`. Include the supported fixture/service/research arguments and verify that the actual CLI runs the M4a worktree code with the intended interpreter; a separate import check alone is not evidence about a later bare command. Preserve the allowance of one explanation run (including its permitted retry) and one doctor run. Check the existing run record before doing anything again.

**Should fix, non-blocking execution clarifications:**
- Line 23: a `ps` check is only a snapshot. Both workers need an agreed exclusive build slot, such as a shared lock they both honor, to enforce the existing one-build-at-a-time rule.
- Line 30: keep “not yet” as internal draft state; no successful build artifact or exit 0 may use it.
- Line 32: “date not recorded” is an honest temporary marker, but the required AOSP citation date must remain explicitly pending, not reported as completed.

The prompt's “spec wins” rule may mean Muse already followed the correct behavior. Inspect the resulting code/report before assuming defects. Preserve this exact sent prompt as evidence and put corrections in the short follow-up, as Claude proposed.

Specification/prompt review only. I did not run Muse, product tests, builds or live calls.
