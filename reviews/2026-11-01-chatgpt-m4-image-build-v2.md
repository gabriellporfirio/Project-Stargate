# ChatGPT re-review: M4 image build specification v2

Reviewed PR #29 at `4a81994f248f1d2fe974905c3cb792cdcc2e3a60` on 1 November 2026. **Verdict: request one focused correction.**

The previous review's five areas are addressed: complete Assistant payload and locations, conditional services and actual artifact checks, separate worktrees and integration ownership, Files endpoint checks, and explicit complete/partial/blocked outcomes. The reasons comparison and Mac cleanup-log clarifications are also resolved.

**Must fix — name the source of expected model hashes (§4a, §5, §11).** [M4 §5](https://github.com/gabriellporfirio/Project-Stargate/blob/4a81994f248f1d2fe974905c3cb792cdcc2e3a60/plan/milestones/M4-image-build.md#L76) requires each model file's name, bytes and SHA-256 to equal the handoff and build manifest. But the accepted [M3 catalog and handoff contract](https://github.com/gabriellporfirio/Project-Stargate/blob/4a81994f248f1d2fe974905c3cb792cdcc2e3a60/plan/milestones/M3-strategy-fit.md#L116) carries file names and bytes, without per-file SHA-256. M4 still requires M3 schema validation and says new entries follow M3's catalog rules; it does not define a hash-field extension. A plan conforming to that contract therefore lacks a value required by M4's check. This leaves Muse to invent the interface or weaken the check.

Choose one explicit contract:

- **Smallest change:** preserve M3's schema. Bind the approved `assistant-manifest.json` to the handoff's exact model identity, source/revision, format/runtime and file set. Compare names and sizes with the handoff, and actual payload hashes with the approved manifest's pinned hashes. The generated build manifest must repeat those expected hashes; it cannot be the only source of them.
- Alternatively, deliberately extend the catalog, plan schema, serializer and validator with per-file hashes; assign ownership and define how existing plans are handled.

Add one offline integration test using an M3-generated plan: the approved payload passes, while changed content with the **same file name and size** fails. This proves the comparison has an independent expected hash.

No other merge blockers found in this revision. The approved spike and bounded Assistant investigation can continue.

**Verification limit:** this is a specification review. GitHub still returns “No commit found” for the cited product checkpoint `e701acd82939a7cd9d8eef89813cd3427e4b5ef7`; I could not inspect its schema implementation. No installs, builds, emulator runs or inference calls were performed.
