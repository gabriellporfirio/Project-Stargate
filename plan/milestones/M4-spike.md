# M4 spike: can we build and boot a StarGate image at all?

Status: v2, 31 Oct 2026, which folds in [ChatGPT's review](../../reviews/2026-10-31-chatgpt-m4-parallel-spike.md) (three must-fix, one should-fix). It runs **alongside M2**, so we know by Sunday 1 Nov whether the core of the demo (two selection-dependent images booting in the emulator) is possible, and which path it takes. It's a test, not the M4 build. The full M4 spec follows from what it finds. It doesn't prove the Files or Assistant apps work, or anything about real phones.

## Why now
M4 is the core of the demo ([scoring plan](../scoring-plan.md)) and the riskiest milestone. Three things are still unknown, and each could change the plan:
- **Q7:** which emulator system image to use.
- **Q8:** whether that image can be unpacked, changed and repacked in the Linux codespace.
- **Which tools have to be installed**, in the codespace and on the Mac, to build the apps and boot the result.

Finding a blocker on Monday would leave no time to switch paths.

## Where things run (Q11, answered 31 Oct)
- **Codespace (Linux):** downloading and inspecting the image, any repacking, and building the minimal launcher. Muse does this work.
- **The owner's Mac** (MacBook Pro, Apple M5, 16 GB RAM, owner-stated): the Android Emulator only. That's arm64, so the image must be an **arm64** emulator image. The emulator needs hardware virtualization, which the codespace doesn't have.
- The Mac gets nothing installed until an **INSTALL APPROVAL REQUIRED** block (master plan section 1, rule 3) has been shown and approved. The owner runs the Mac commands themselves, from steps Muse writes into `docs/m4-spike.md`.

## Isolation from M2
A git worktree separates source files only. It doesn't separate installed tools, caches or machine resources, so the spike also keeps those apart.
- **Code:** a second Muse works in its own worktree on a named branch, `m4-spike`, created from the accepted M0 checkpoint `1673b97fb97d2612f42fa28c6fe07caa2a937bb3` (`git worktree add -b m4-spike ../m4-spike 1673b97fb97d2612f42fa28c6fe07caa2a937bb3`). The spike doesn't need M1 or M2 code. Its files go only under `spike/m4/` and `docs/m4-spike.md`. No changes to the `stargate` package, its schema or its CLI. Integration comes later, in M4.
- **Tools and caches:** everything the spike downloads or installs lives under `/workspaces/m4-tools/` (for example `ANDROID_HOME`, `ANDROID_USER_HOME`, `GRADLE_USER_HOME` and any JDK), and large files under `/workspaces/m4-downloads/`. These are set **only in the spike's own shell** (for example with `export` in a script it sources), never in `~/.bashrc`, global git or pip config, or anything M2 uses. Existing system tools may be used read-only.
- **No system-wide installs** (`apt`, `sudo`, global `pip`). If one turns out to be required, the spike stops and reports it, because it would affect M2.
- **Resources:** builds use at most 2 workers and 2 GB of heap (for example Gradle `--max-workers=2` and `-Xmx2g`), so M2 keeps running.
- **Hand-off:** one commit on `m4-spike`, plus a manifest in `docs/m4-spike.md` listing every artifact with its path, size and SHA-256.

## Questions the spike answers (recorded in `docs/m4-spike.md`)
1. **Image (Q7):** which official arm64 emulator system image (Android version and variant), its exact source URL, size and SHA-256, and why it was picked. Whether the variant allows `adb root` is checked, not assumed.
2. **Image layout:** what the package contains (for example a separate `system.img`, or a `super` image holding several partitions), each partition's filesystem format, and whether the emulator verifies them at boot.
3. **Repacking (Q8):** can a small, harmless marker be added to the system partition and repacked in the codespace? The marker is a text file holding the selection name and a random value generated for this run. If tools need installing, they go in the approval list below.
4. **Launcher toolchain:** what it takes to build a minimal launcher app in the codespace: a StarGate home screen showing "StarGate" and the selected services. The lightest route is preferred (for example the JDK plus Android SDK build tools used directly, without Gradle). Each tool is listed with its version, source and size.
5. **Mac setup:** the exact Mac install (tool, version, source, size, where it goes, how to undo) and the transfer steps, together in one approval block.

Out of the spike (they come in M4 itself): the Files and Assistant apps, any Llama model download, and the two-build demo.

## Approvals (two, asked once each)
- **Codespace tool list:** before downloading any tool, Muse shows one INSTALL APPROVAL REQUIRED block for everything questions 3 and 4 need. It names every download source, which may include sources beyond Google and Android if they're needed (for example Maven Central for build dependencies, or a JDK publisher such as Eclipse Temurin). Nothing outside that list is fetched. Once approved, Muse **may build** the minimal launcher. Without approval, Path B is reported as **not tested**.
- **Mac block:** the emulator install, plus the transfer of the spike's artifacts to the Mac.

## The two paths
- **Path A, image:** the codespace repacks the emulator image with the marker (and, if time allows, the launcher) built in, and the Mac boots **that** image. This is the plan's first choice.
- **Path B, configuration bundle:** the stock image boots, and StarGate's launcher is installed on top after boot and set as the home app. It must be labelled **"configuration bundle, not an image"** everywhere, including the video.

**Time:** at most 4 hours of Muse work in total. Path A gets at most 2.5 hours, so at least 1.5 hours are kept for Path B.

## Proof rules
**Path A** counts only if it's clear the repacked artifact itself made the difference, not a temporary change. Android's `-writable-system` option works on a temporary copy, so it's not allowed here.
- Record the SHA-256 of the stock package, the stock system image and the output image, plus the marker's selection and random value.
- Boot the output from a **fresh, dedicated AVD** used for nothing else (for example `stargate-spike-a`), with **snapshots off and data wiped** (for example `-no-snapshot -wipe-data`), and record the exact launch command.
- Nothing is installed or changed after boot.
- Record `sys.boot_completed` = `1`, and read the marker back from the running system, matching the recorded random value.

**Path B** records its stock image hash, the launcher APK's hash, every post-boot command, and a screenshot of the StarGate home screen. It stays clearly separate from Path A.

**ADB safety:** before every `adb` command, the device list must show only the emulator, and every command names it explicitly (`adb -s emulator-5554 …`, with the serial checked against the AVD's name). If a physical device is ever listed, stop. No real phones, no USB, no `fastboot`.

**Transfer:** the owner downloads artifacts from the codespace through the browser file explorer (nothing to install), then checks each one on the Mac with `shasum -a 256` (built into macOS) against the manifest. A mismatch means stop.

## Limits
- **Disk:** before downloading, record the free space in the codespace and on the Mac. Downloads count against **10 GB in total**, dependencies included. Unpacked and repacked copies take space on top of that, so Muse estimates the peak (archive, unpacked image, repack copy, outputs) and stops if free space is less than that peak plus 5 GB.
- **Network:** only the sources in the approved list, plus official Android documentation. No Meta calls.
- The usual Muse rules hold: no push, no `--disable-sandbox` or `--yolo`, keys never printed, and a list of every command run outside the sandbox.

## Results
Each path is reported as one of: **passed**, **failed** (with the error), **blocked** (waiting for approval, or out of disk, time or memory), or **not tested**. Blocked and not tested aren't technical failures.

## Done when
- [ ] `docs/m4-spike.md` answers questions 1–5, with sources, sizes, hashes and the artifact manifest.
- [ ] The owner has booted the stock arm64 image on the Mac (owner-observed), **or** the spike reports exactly why not.
- [ ] Path A meets the proof rules, **or** Path B shows the StarGate home screen with its records, **or** the spike reports each path's result as above.
- [ ] Every install was approved first and is logged. One commit on `m4-spike`, not pushed.

## What happens next
Claude writes the full M4 spec for the chosen path, GPT reviews it, and M4 builds on Monday. The owner picks the path, with Claude's and ChatGPT's view. If neither path boots by Sunday night, the owner decides between more time on M4 and the Tuesday fallback (record what works, clearly labelled).
