# ChatGPT re-review: parallel M4 spike, v2

Reviewed PR #26 at `8ab55b89e8018e46262ef33f014fb311bc62a89f` on 31 October 2026. **Verdict: approved for the bounded feasibility spike alongside M2.** This supersedes the change request in [the first review](2026-10-31-chatgpt-m4-parallel-spike.md).

**Must fix: none remaining.** The three blockers are resolved:

1. **Artifact proof:** Path A records stock/output hashes and a selection-specific random marker, boots the output in a fresh dedicated AVD with snapshots disabled and data wiped, and requires boot completion plus marker readback. Temporary writable-system copies and post-boot changes are excluded. Path B records its separate post-boot setup. ADB commands target the verified emulator.
2. **Parallel work:** the named branch starts at the accepted M0 checkpoint and does not depend on unfinished M1/M2 code. Tool/cache directories and shell settings are isolated; system-wide installs stop the spike. Product package/schema/CLI changes remain outside scope, with a commit and artifact manifest for later integration.
3. **Runnable fallback:** the approved source/tool list can include the publishers actually needed to build the minimal launcher. Building it is explicitly allowed after approval. Browser transfer and Mac checksum verification are defined. Path B retains the “configuration bundle, not an image” label.

**Should fix: none remaining from the first review.** Download limits include dependencies; peak disk estimates include expanded copies and a margin. Worker/heap limits and reserved fallback time support parallel work. Blocked and untested results are distinguished from technical failures.

**Execution priorities:** identify the image and exact tool list; collect the prescribed boot evidence within the caps; hand off the result and manifest for the full M4 spec. Keep the existing installation approvals and pre-commit key checks in the Muse prompt.

This approves the specification, not a successful build or boot. No installs, builds, emulator boots or inference calls were performed in this review. Files/Assistant functionality, two selection-dependent builds and real-phone compatibility remain outside this spike.
