# Running M6 in advance: why it can't disturb the current work

Owner rule (2 Nov): anything started in advance must not depend on, or disturb, the work running now.

## What is running now (the "Now" track)
| Who | Where | What |
|---|---|---|
| Second Muse | `/workspaces/m5` (branch `m5-install-plan`), `/workspaces/m5-tools` | M5 fetch diagnosis and fix, then a live rerun after the owner's "go", then the M4c BYOK fixup in `/workspaces/m4b` (branch `m4c-byok`) |
| Owner on the Mac | the Mac, plus the codespace transfer server on port 8765 serving `/workspaces/m4a-tools/out` | The Files + Assistant boot test (M4 Part 3C) |
| Builder Muse | `/workspaces/m4a` (branch `m4a-build`, at `5a9c7e6`) | Idle, **kept free** for any fix the Mac test needs |

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
- **Shared resources are guarded.**
  - Android builds take the shared build lock and hold it only while building.
  - Each build first checks for at least 8 GB free and stops if not (the codespace had 15 GB free on 2 Nov; one image build uses about 2.5 GB).
  - The second Muse makes no Android builds now.
- **No live calls.** The Ahead track makes no network or Meta calls.
- **The builder isn't used.** It stays free for Mac-test fixes. That's why the platform gets a new Muse instead of the builder.

## What gets joined later (and when)
1. After the Mac test passes, and after M5 and the M4c fixup finish, their branches are merged into the M6 branches in a reviewed step. Any later fix on `m4a-build` is merged then too.
2. Platform Part 2 wires in M5's install plan and Link. Phone Part B adds the Assistant behind Link (a new Assistant handoff).
3. Known overlap to resolve at that merge:
   - Phone A changes the M4 build (Link in every build, Files without a socket).
   - The platform's Build step must then use the merged build code, and the M4 Mac steps change from "Files listens on 8080" to "Link listens on 8080".
