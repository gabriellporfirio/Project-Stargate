# ChatGPT re-review: M4a Part 1 prompt corrections

Reviewed PR #31 at `44c8c6969cd25cc96142b8d3cd2a8c55b5b21b8a` on 1 November 2026, including `plan/prompts/m4a-part1-fixup.md`.

**Verdict: approved. Both prompt findings are resolved; no outstanding merge blockers.**

- **Hash binding:** the follow-up binds model ID, revision, file names and sizes to the M3 handoff, requires hashes in the Assistant manifest, and preserves exit 9 for binding/missing-hash failures versus exit 8 for changed payload content. M3's schema stays unchanged, and the Assistant manifest's own hash is recorded. The post-Part-1 review requires the real M3-plan test and same-name/same-size changed-content check.
- **Live invocation:** it uses `stargate plan ... --explain` with supported inputs and requires proof that the actual command uses the M4a code and intended interpreter. Existing run records are checked first; this does not grant another live-call allowance.
- **Other clarifications:** an unfinished route remains internal and cannot produce exit 0 or a finished build; an unavailable citation date remains explicitly pending. A shared build lock for both workers is recorded as a Part 2 prerequisite.
- The exact originally sent prompt is preserved, with the corrections supplied separately and checked afterwards.

The Part 1 / Part 2 split remains approved. Packaging, route-specific image work, final demo builds and Mac proof still wait for the recorded spike result. The fixup adds no route dependency to Part 1.

This approves the instructions. It does not prove that the running Muse received them before a particular step or that its implementation passes them; the specified post-Part-1 review must check the resulting code and run records.

No installs, product tests, builds, emulator commands or live inference calls were performed.
