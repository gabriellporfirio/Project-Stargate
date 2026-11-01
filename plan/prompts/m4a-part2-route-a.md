# M4a Part 2: Route A image builds (builder Muse)

The Mac spike passed both paths, so M4 builds **Route A**: StarGate system images with the apps (and, for the Assistant build, the model) baked in. Pinned to:
- **Spec:** `plan/milestones/M4-image-build.md` on main after PR #32. That PR adds the `-sysdir` launch rule and the Route A decision.
- **Part 1:** `b72dc1f` on `m4a-build`, reviewed with no must-fix.
- **Spike:** `c3c3739f017a0c24623b481e569193f3c3e28570` on `m4-spike`.
- **Assistant:** `6bb6681` on `m4b-assistant`, reviewed and fixed.

## Setup (the builder terminal)
```
cd /workspaces/m4a
git status --short
git log -1 --oneline
muse --approval-mode on-request --approval-judge on
```
`git log` should show b72dc1f and `git status` should be empty.

## Paste this into the builder Muse
```
StarGate M4a, Part 2: Route A image builds. You are the BUILDER Muse in /workspaces/m4a on branch m4a-build at b72dc1f. Spec: git -C /workspaces/Project-Stargate fetch origin main, then read origin/main:plan/milestones/M4-image-build.md and origin/main:plan/master-plan.md (don't change that folder's checkout). First confirm that master-plan section 7 has the row "M4 takes Route A (image)" and that spec section 6 has the -sysdir launch rule. If either is missing, stop: PR #32 isn't merged yet. Read the whole spec again, especially sections 2, 3, 4b, 5, 5a, 6, 9, 10 and 11. The spec wins over this prompt where they differ.

Rules: the same as Part 1. Work only in /workspaces/m4a. /workspaces/m4-tools stays READ-ONLY, and your tools and outputs go in /workspaces/m4a-tools and /workspaces/m4a-downloads. No downloads or installs without ONE "INSTALL APPROVAL REQUIRED" block and my OK. /usr/local/bin/python3 with PYTHONPATH=/workspaces/m4a. Never push, keys never printed, never --yolo, no sudo or apt. No live Meta or Baseten calls: Part 1 used M4a's allowance. Keep a list of commands run outside the sandbox.
Build slot: before any Android build, image unpack or repack, take the shared lock with `flock /workspaces/.android-build.lock <command>`, or hold it with `exec 9>/workspaces/.android-build.lock; flock 9` for a sequence, and release it after. At most 2 workers and 2 GB heap. The second Muse uses the same lock.
Disk: before the FIRST large unpack or repack (including any test or validation run in Step 3), record free space and estimate your peak (two unpacked plus two repacked images, the 1.1 GB model and any copies). Stop if free space is under that peak plus 5 GB. Carry the spec's Mac free-space check into the Step 5 Mac steps.

Step 1: bring in the other branches (one commit each, merge commits, nothing rewritten).
a. git merge c3c3739f017a0c24623b481e569193f3c3e28570, with "M4a: merge M4 spike c3c3739 (Route A proven on the Mac)" in the message.
b. git merge m4b-assistant at 6bb6681, or at the M4b fixup commit if my paste note names one (check that the branch tip equals that SHA; stop if it's different). Note in your report: this brings in the old demo/assistant.apk blob (about 24.7 MB) from commit 31512ba in history. Don't rewrite history, just report it, and the owner decides before any push.
After each merge, run the full suite. All tests must pass.

Step 2: the Part 1 review items.
- docs/m4-build.md: record the full `stargate plan ... --explain` command, including its output flag.
- manifest.py: a guard that refuses a finished build manifest whose route is not_yet.
- checks.py: read the Assistant package name from assistant-manifest.json, not a constant.
- Optional: assert exit 8 through run_contents_checks for each contents case. Make plan-v1.json byte-identical to M3's again, or note why not. Only formatting differences may be explained away: M3's schema must stay semantically unchanged.
Commit: "M4a part 2A: merges and Part 1 review items".

Step 3: Route A packaging.
1. Read the spike's spike/m4/path_a_repack.py and docs/m4-spike.md, and reuse its proven repack method on the same stock image (system-images;android-34;default;arm64-v8a, system.img 250ee9bb4e87b7beb5755a3b6984822bcf4335cd2d80701ac2e5ce9fb9da105d, from /workspaces/m4-tools, read-only).
2. `stargate build --plan P --out D` for an emulator_only plan now produces a repacked system image with: the launcher as a privileged/system app that is the home screen, with the build ID and the label from spec sections 1 and 2 in its config; the Files app when Files is selected; and, when the Assistant is selected, the Assistant APK plus EVERY file listed in assistant-manifest.json (today the .pte and tokenizer.model; the manifest defines the set, not this prompt) in the read-only folder it names (Route A path), opened in place, never copied out. Write the build ID into the image as a file the Mac steps can read back.
3. Size: the model is about 1.1 GB, so the image will grow. Grow the filesystem the way the spike's method allows. Record the image size against the partition limit (spec section 5). If the model can't be placed in the image, that's a recorded Route A failure for the Assistant (spec 4b), never a push after boot. Report it and continue with the Files-only build. From then on the result is PARTIAL (see Step 4).
4. The section 5 checks read the REAL image: list the packages and the model folder inside the repacked image and compare them with the selection and assistant-manifest.json. Wrong content fails with 8.
5. build-manifest.json (build-v1): route "A", every artifact with size and SHA-256, the assistant-manifest's own SHA-256, and the image size versus the partition limit.
6. Tests for each of the above, with small synthetic images where real ones are too big.
Commit: "M4a part 2B: Route A image packaging and image contents checks".

Step 4: the two demo builds.
- Files-only: make a fresh accepted plan with M3's code for a demo profile whose result is emulator_only with only Files selected. Name the profile.
- Files + Assistant: demo/plans/flagship-files-assistant.plan.json from M4b. Re-validate it first.
Build both into /workspaces/m4a-tools/out/build-files and /workspaces/m4a-tools/out/build-files-assistant. Each build that is attempted must either exit 0 with the section 5 checks passing, or fail with its documented exit code; never fake or hand-assemble an artifact.
- FULL result: both builds exit 0, with different manifests and launcher configs.
- PARTIAL result (the Assistant can't be placed in the image, per Step 3 and spec 4b): keep the Files-only build, record the Assistant build's failure and exit code, create NO Assistant image, manifest or Mac steps, and don't retry just to get two builds. The reduced-demo decision is mine (spec section 10).
Gzip each successful image for transfer and record both hashes (.img and .img.gz).
Commit: "M4a part 2C: both demo builds" (manifests and docs only, no images in git).

Step 5: the Mac steps (written, not run) in docs/m4-build.md, a section the owner can paste from. Use exactly the spike's working patterns:
- Every block pastes cleanly into zsh: one command per line, no angle brackets, no lines that wrap mid-command.
- Start with the environment block: export SG=~/stargate-spike, ANDROID_HOME=$SG/sdk, ANDROID_USER_HOME=~/.android, JAVA_HOME=$SG/jdk-17/Contents/Home and PATH, each on its own line. Reuse the spike's tools, with NO new installs.
- Transfer: from the codespace, `cd /workspaces/m4a-tools/out` then `/usr/local/bin/python3 -m http.server 8765 --bind 127.0.0.1`, and download through the private forwarded port (the file explorer download gave 9-byte files). Files go to ~/stargate-m4/. Check them with shasum -a 256. Safari may unpack .gz files, so give both hashes.
- Before creating anything: append the new AVDs (stargate-m4-files, stargate-m4-files-assistant) and ~/stargate-m4 to ~/stargate-cleanup-log.md with their undo commands.
- Create each AVD with avdmanager (stock system-images;android-34;default;arm64-v8a, -d pixel_7). For the Assistant AVD, set hw.ramSize=6144 and a data partition big enough for the spec, editing config.ini with paste-clean lines.
- Boot each with a sysdir of symlinks to the stock system-image files, with system.img pointing at that build's image, and `emulator -avd NAME -sysdir DIR -no-snapshot -wipe-data -no-metrics`. Never -system or -writable-system.
- Device guard before EVERY device command, not just each group (spec section 6). The guard reads ONE adb devices inventory, counts EVERY device row whatever its state (device, offline, unauthorized and so on), and allows the command only if there is exactly one row, it is exactly "$SERIAL" followed by a tab and "device", and adb -s "$SERIAL" emu avd name equals the intended build AVD. Anything else stops, including an extra row in any state. Put this function in the environment block (it passes a bash test with a fake adb; re-test it in zsh): sg_guard() { local inv rows avd; inv="$(adb devices 2>/dev/null | tr -d '\r')" || { echo "STOP: adb devices failed"; return 1; }; rows="$(printf '%s\n' "$inv" | sed '1d' | sed '/^\*/d' | sed '/^[[:space:]]*$/d')"; [ "$(printf '%s\n' "$rows" | sed '/^$/d' | wc -l | tr -d ' ')" = "1" ] || { echo "STOP: expected exactly one device row"; return 1; }; [ "$rows" = "$(printf '%s\tdevice' "$SERIAL")" ] || { echo "STOP: the only row must be $SERIAL in state device"; return 1; }; avd="$(adb -s "$SERIAL" emu avd name 2>/dev/null | head -1 | tr -d '\r')"; [ "$avd" = "$1" ] || { echo "STOP: AVD is '$avd', expected '$1'"; return 1; }; } Then write each adb line as: sg_guard stargate-m4-files && adb -s "$SERIAL" ... . Add a test that runs the guard against a fake adb for: one valid emulator (allow); that emulator plus a physical device marked unauthorized, or offline (deny); two emulators (deny); empty (deny); the emulator offline (deny); the wrong serial (deny); the wrong AVD name (deny); Windows line endings (allow).
- Boot record per spec section 6: sys.boot_completed, the build ID read back from the image, a home-screen screenshot, and every adb command run (with no install or push).
- Files: adb forward, upload and download a test file with matching hashes, no code and wrong code refused, and loopback-only listeners shown inside the emulator and on the Mac.
- Assistant (FULL result only): networking off, one question, and the model hashes the app shows. On a PARTIAL result, leave out the Assistant AVD and its steps.
- Shut down and run adb devices after each boot.
Commit: "M4a part 2D: Mac boot steps".

Then STOP. Save /tmp/m4a-part2-report.md with: FULL or PARTIAL at the top (if PARTIAL, why, and that the reduced-demo decision is waiting on me); each merge commit, the Part 1 items fixed (file:line), the Route A method and image sizes versus the limit, each build attempted (exit code, manifest path, image and .gz hashes for successful ones), whether the Assistant fit in the image, test count, scan results, the outside-sandbox command list, every commit SHA, and the history blob note.
```
Paste Muse's report into the project thread. A reviewer check follows, then the Mac run.
