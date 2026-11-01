# M4a Part 1: the route-independent build core (builder Muse)

Pinned to the M4 spec v2.2 at `cb3024f006990965968e841579a52a24ead5f77a` (PR #31: merge it first) and the reviewed M3 commit `e701acd82939a7cd9d8eef89813cd3427e4b5ef7`. Part 2 (spike merge, route packaging, demo builds and the Mac steps) waits for your Mac spike test.

## Setup (the builder terminal)
If the builder Muse is open, quit it first (`/quit` or Ctrl+C), then run:
```
cd /workspaces/Project-StarGate-Meta-Hackathon
git worktree add -b m4a-build ../m4a e701acd82939a7cd9d8eef89813cd3427e4b5ef7
cd /workspaces/m4a
muse --approval-mode on-request --approval-judge on
```

## Paste this into the builder Muse
```
StarGate M4a, Part 1: the route-independent build core. You are the BUILDER Muse in /workspaces/m4a on branch m4a-build, starting at e701acd82939a7cd9d8eef89813cd3427e4b5ef7. Spec: plan/milestones/M4-image-build.md at cb3024f006990965968e841579a52a24ead5f77a. Read it with git -C /workspaces/Project-Stargate fetch origin, then git -C /workspaces/Project-Stargate show cb3024f006990965968e841579a52a24ead5f77a:plan/milestones/M4-image-build.md, and don't change that folder's checkout. Read ALL of it, especially sections 1, 3, 3a, 5, 5a, 7, 8, 9 and 11. The spec wins over this prompt where they differ.

Rules:
- Work only in /workspaces/m4a. Never touch /workspaces/Project-StarGate-Meta-Hackathon (except git worktree commands), /workspaces/m4b, /workspaces/m4-spike or /workspaces/review-m4b.
- /workspaces/m4-tools is READ-ONLY: you may run its JDK and Android build tools, but never write there. Your own tools and outputs go in /workspaces/m4a-tools and /workspaces/m4a-downloads.
- No downloads or installs. If something is missing, show ONE "INSTALL APPROVAL REQUIRED" block and stop.
- Python: /usr/local/bin/python3 with PYTHONPATH=/workspaces/m4a. The python3 on the shared PATH is the main folder's .venv, so don't use it. First prove that `import stargate` loads from /workspaces/m4a.
- Android builds: at most 2 workers and 2 GB heap, and never while another Android or Gradle build is running (check with ps first; the second Muse may be building in /workspaces/m4b).
- Never push, keys never printed, logged or written, never --yolo, no sudo or apt. Keep a list of commands run outside the sandbox.
- You own only what section 11 gives M4a. Don't touch the Assistant app, assistant-manifest.json, the catalog or docs/m4-assistant.md (the second Muse owns those).

Part 1A: the build gate and checks (Python). Commit and continue.
1. `stargate build --plan <plan.json> --out <dir>` with the section 1 gate and section 8 exit codes: full plan-v1 validation (6); handoff vs top level, including handoff.reasons == fit.reasons exactly (6); build only when build_allowed is emulator_only, else 7 with the refusal reasons; an Assistant with no resolved model gives 9. All of these happen BEFORE any build step, proven by a stub build function that is never called. The "emulator experiment: fit not confirmed" label for unconfirmed plans.
2. Section 5a binding: read an assistant manifest (the format is in /workspaces/m4b/assistant-manifest.json; read it, never write it) and stop with 9 if the model ID, revision, file names, sizes or any file hash don't match the plan's handoff.
3. build-v1: the schema, a writer and a validator. Leave the route field to Part 2 (it accepts A or B, plus a "not yet" value that a real build refuses).
4. Section 5 contents checks that don't need an image: the real package names read from inside each APK (aapt2 from m4-tools), the model files in a model folder, and the assets in every APK. Exit 8 for an unselected app, a missing app, a model file where none belongs, or a model file with the right name and size but different content.
5. Section 7 items, each with a test: the --explain cap raised to 4096 with one retry and the "cut short" label; handoff.reasons == fit.reasons for every result in the M3 validator; a field in a catalog entry's estimates can't also be sourced; any finish_reason other than stop is incomplete; the AOSP page date recorded with its quoted sentence in docs/inference-rules.md (if the date isn't already on file, write "date not recorded" rather than fetch it).
6. The section 9 tests for all of the above, including the manifest-binding tests on a REAL plan made by M3's code with a small test model entry. Run the full suite with sockets blocked.
Commit: "M4a part 1A: build gate, manifest binding, build-v1, contents checks, M3 carry-overs".

Part 1B: the launcher and Files apps (Android).
7. The StarGate launcher (home app): shows "StarGate", the selected services from the handoff only, the build ID, and the label when one applies. It requests no permissions.
8. The Files app, following section 3a exactly: listens on 127.0.0.1 only; a random access code made on first start and shown on screen; refuses no code and wrong codes; path confinement (refuses .., absolute paths, encoded slashes and links that point outside); 50 MB per upload and 200 MB total, refused before writing, leaving no partial file; no outgoing connections. Its only permission is INTERNET (needed to listen on loopback).
9. Files handler tests run on the host against the SAME handler code: every rule above, including that the running test server's socket is bound to 127.0.0.1.
10. Build both APKs with the spike's toolchain (no Gradle). Keep the APKs out of git, under /workspaces/m4a-tools/out/. Record package name, version, bytes and SHA-256 in docs/m4-build.md, plus aapt2's permission list for each.
Commit: "M4a part 1B: launcher and Files apps".

Part 1C: one live check.
11. Run `stargate --explain` once, live, on one demo plan to confirm the 4096 cap, and record the finish_reason and token counts (never the key) in docs/m4-build.md. Then run `stargate doctor` once. These are M4a's only two live calls in all of M4: don't repeat them.
Commit: "M4a part 1C: live --explain and doctor check".

Then STOP. Don't start Part 2: it waits for the Mac result. Save /tmp/m4a-part1-report.md with: the proof that stargate loaded from /workspaces/m4a, what was built (file:line), the test count and result, both APKs (package, bytes, SHA-256, permissions), the live check results, the outside-sandbox command list, and every commit SHA.
```
Paste Muse's report into the project thread. After that, a reviewer Muse checks Part 1.
