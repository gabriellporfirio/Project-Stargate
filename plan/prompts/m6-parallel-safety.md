# Running M6 in advance: why it can't disturb the current work

Owner rule (2 Nov): anything started in advance must not depend on, or disturb, the work running now.

## What is running now (the "Now" track)
Updated 3 Nov 2026. Re-check this table before starting the Ahead Muses; the owner's Now flag, not this table, is what protects running work.
| Who | Where | What |
|---|---|---|
| Install-plan Muse | `/workspaces/m5` (branch `m5-install-plan`, at `0f3ef23`), `/workspaces/m5-tools` | M5 fix 5l (spec v2.2, offline) after GPT approves it, then a live run only on the owner's "go" |
| Key-fix Muse | `/workspaces/m4b` (branch `m4c-byok`, at `f7e080d`), `/workspaces/m4b-tools` | M4c fix 5m (review fixes, new cloud APK in `out-byok3`) after GPT approves it |
| Builder Muse | `/workspaces/m4a` (branch `m4a-build`, at `5a9c7e6`), then a new `/workspaces/m4c-live` | The M4c live-proof build after 5m, under the Now flag |
| Owner on the Mac | the Mac, plus the codespace transfer server on port 8765 when downloading | Mac proofs (M4c live proof next) |
| Read-only reviewers | `/workspaces/review-*`, `/workspaces/reviews` | Reviews only; they never build |

## What would start in advance (the "Ahead" track)
| Who | Where | What |
|---|---|---|
| Platform Muse (new, terminal 6) | `/workspaces/m6` (branch `m6-platform`), `/workspaces/m6-tools` | M6 Part 1, the platform |
| Phone Muse (new, terminal 5) | `/workspaces/m6-phone` (branch `m6-phone`), `/workspaces/m6-phone-tools` | M6 phone side Part A: Link, Files behind it, signing, home screen |

## Why they are independent
- **Fixed start.** Both start from the fixed commit `5a9c7e6`, not a branch tip. A later fix on `m4a-build` (if the Mac test fails) doesn't move them.
- **No merges.** Neither merges M5, M4c or each other in this part. M5's work is not inside them, and nothing they do changes M5.
- **Separate folders.** Each has its own worktree, branch and tools folder. Every other worktree and tools folder is read-only to them. Nothing touches the frozen build outputs the Mac test is downloading.
- **No shared ports or devices.** They never use the transfer port 8765 or 8080 in the codespace, and tests use any free port. They never run an emulator or adb in the codespace.
- **Shared resources are bounded, and the Now track has priority.** Separate folders don't share files, but the Muses still share one machine's CPU, memory, disk and the build lock, so "no interference" holds only through these rules, not unconditionally:
  - **Limits from M4:** at most one Android build at a time across all Muses, with at most 2 GB of heap (2 Gradle workers if Gradle is ever used). Builds and full test suites run under `nice -n 10`.
  - **Disk:** a Muse takes the build lock **first**, then measures free space. It estimates the build's full peak: scratch and unpacked copies, the image, payload copies and the gzip. It goes ahead only if free space is at least that peak plus M4's 5 GB reserve, and it records the measured peak afterwards. (The earlier flat "8 GB" estimate is withdrawn.)
  - **Quiet windows (a handshake):** every heavy step an Ahead Muse runs goes through its helper `ahead-heavy.sh`. Heavy means any Android/Gradle build including standalone APKs, image builds, compression, full test suites, and any single test that starts an Android build tool (aapt2, d8, javac, zipalign, apksigner, keytool, `build_apps.sh`, the image builder), because those can trip `build_apps.sh`'s process guard during another build. The helper:
    1. refuses to start while `/workspaces/.now-track-busy` exists;
    2. takes the build lock;
    3. writes a marker `/workspaces/.ahead-heavy-<name>` with its PID and the word `pending`, **before** starting anything;
    4. checks the flag **again** and backs out (deleting the marker) if it appeared;
    5. starts the step **once**, in its own process group, confirms the group exists, and only then records the group's ID in the marker atomically (temporary file, then rename). If it can't confirm the group, the marker says `unknown` and stays;
    6. waits until every process in that group has ended, and only then removes the marker.

    A step already running finishes, because nothing is killed mid-write. If the helper is interrupted, or can't confirm that the whole group has finished, it leaves the marker in place and reports it. The owner sets the flag first, then waits until no marker is left before starting the Now task. Because the marker is written before the second check, a Muse that was waiting for the lock can't slip in after the owner's check. The owner's wait loop never deletes a marker by itself. A marker whose helper has stopped, or whose group ID is `pending`, `unknown` or unreadable, blocks CLEAR until the owner checks by hand that its job has finished. The helper's tests keep the joint case of a dead helper with a live child.
  - **Output paths:** before any suite or build, each Ahead Muse checks that inherited scripts write only under its own worktree or tools folder.
  - **Planning repo:** the owner fetches it once before starting both Muses. The Muses read the pinned commit and never fetch, so no two processes write to that shared repo at once.
- **No live calls.** The Ahead track makes no network or Meta calls.
- **The builder isn't used.** It stays free for Mac-test fixes. That's why the platform gets a new Muse instead of the builder.

## What gets joined later (and when)
1. After the Mac test passes, and after M5 and the M4c fixup finish, their branches are merged into the M6 branches in a reviewed step. Any later fix on `m4a-build` is merged then too.
2. Platform Part 2 wires in M5's install plan and Link. Phone Part B adds the Assistant behind Link (a new Assistant handoff).
3. Known overlap to resolve at that merge:
   - Phone A changes the M4 build (Link in every build, Files without a socket).
   - The platform's Build step must then use the merged build code, and the M4 Mac steps change from "Files listens on 8080" to "Link listens on 8080".

## Owner steps this adds
- Once, before starting both Ahead Muses: `git -C /workspaces/Project-Stargate fetch origin`
- **Before** a Now-track live run, BYOK build or urgent fix, run these two commands. The second one waits until both Ahead Muses have finished any heavy step in progress. It never deletes anything itself. If it prints BLOCKED, follow its instruction: confirm from the Muse's record that the job really has ended (a process search is only a hint), then delete that one marker by hand; if completion can't be confirmed, keep the marker:
  ```
  touch /workspaces/.now-track-busy
  while ls /workspaces/.ahead-heavy-* >/dev/null 2>&1; do for f in /workspaces/.ahead-heavy-*; do p=$(sed -n 1p "$f"); g=$(sed -n 2p "$f"); ps -p "$p" >/dev/null 2>&1 || echo "BLOCKED: $f is from a stopped helper (group: $g). If the group is a number, check its job has ended with: ps -g $g   If it says pending or unknown, this is only a hint (it misses steps such as the Python image builder, debugfs and zipalign): ps -ef | grep -v grep | grep -e aapt2 -e d8 -e javac -e gzip -e unittest   An empty result does NOT prove the job ended. Delete the file yourself (rm $f) only when the Muse's own record of the job (the command it launched and when it started) shows that job has finished; if you can't tell, leave the file and ask Claude."; done; echo "Waiting for the Ahead Muses to finish their current step"; sleep 30; done; echo "CLEAR: start the Now task"
  ```
- Start the Now task only after `CLEAR` prints.
- **After** it finishes: `rm /workspaces/.now-track-busy`, and the Ahead Muses resume on their next 5-minute check.

## What these partial stages don't prove
Platform Part 1 and phone Part A are partial stages. Approving them doesn't complete M6 §7's combined Files + Assistant Mac proof. Runtime claims are marked pending until the owner runs the Mac steps: which of our apps listen, and the positive and negative binding results.
