# M4 spike: can we build and boot a StarGate image at all?

Status: v1, 31 Oct 2026, for review. It runs **alongside M2**, so we know by Sunday 1 Nov whether the core of the demo (two selection-dependent images booting in the emulator) is possible, and which path it takes. It's a test, not the M4 build. The full M4 spec follows from what it finds.

## Why now
M4 is the core of the demo ([scoring plan](../scoring-plan.md)) and the riskiest milestone. Three things are still unknown, and each could change the plan:
- **Q7:** which emulator system image to use.
- **Q8:** whether that image can be unpacked, changed and repacked in the Linux codespace.
- **Which tools have to be installed**, in the codespace and on the Mac, to build the apps and boot the result.

Finding a blocker on Monday would leave no time to switch paths.

## Where things run (Q11, answered 31 Oct)
- **Codespace (Linux):** downloading and inspecting the image, any repacking, building the apps. Muse does this work.
- **The owner's Mac** (MacBook Pro, Apple M5, 16 GB RAM, owner-stated): the Android Emulator only. That's arm64, so the image must be an **arm64** emulator image. The emulator needs hardware virtualization, which the codespace doesn't have.
- The Mac gets nothing installed until an **INSTALL APPROVAL REQUIRED** block (master plan section 1, rule 3) has been shown and approved. The owner runs the Mac commands themselves, from steps Muse writes into `docs/m4-spike.md`.

## Questions the spike answers (recorded in `docs/m4-spike.md`)
1. **Image (Q7):** which official arm64 emulator system image (Android version and variant), where it comes from (an official Google source, with the exact URL and SHA-256), and its size. Muse picks it and states why. Whether the chosen variant allows `adb root` is checked, not assumed.
2. **Image layout:** what the downloaded package contains (for example a separate `system.img`, or a `super` image holding several partitions), the filesystem format of each partition, and whether the emulator verifies them at boot.
3. **Repacking (Q8):** can a small, harmless change (one added text file under the system partition) be repacked in the codespace with tools that are already there, or with tools that need installing? If they need installing, list each one (name, version, source, size) and **stop for the owner's approval** before installing.
4. **App toolchain:** what it takes to build a minimal launcher app (a StarGate home screen showing "StarGate" and the list of chosen services) in the codespace: JDK, Android SDK packages, and so on, each with its source and size. It's listed only. Nothing is installed without the owner's approval of the full list.
5. **Mac boot:** the exact Mac install (tool, version, source, size, how to undo), for one approval block.
6. **The boot test:** the owner boots (a) the stock image and (b) the result of the chosen path. Was (b) **different from stock in a way the selection controls**? For example, the StarGate home screen appears, or the test file is present.

Out of the spike (they come in M4 itself): the Files and Assistant apps, any Llama model download, and the two-build demo.

## The two paths, decided by question 3
- **Path A, image:** the codespace repacks the emulator image with StarGate added, and the Mac boots that image. This is the plan's first choice.
- **Path B, configuration bundle:** the stock emulator image is booted, and StarGate is installed on top (for example with `adb install` plus setting it as the home app). The master plan already defines this fallback, and it must be labelled **"configuration bundle, not an image"** everywhere, including the video.

The spike reports which path works, how long each step took, and what broke. It doesn't decide alone: the owner picks the path for M4, with Claude's and ChatGPT's view.

## Limits
- **Time:** at most 4 hours of Muse work in total. If it's not done by then, it stops and reports what it found.
- **Downloads:** official Google and Android sources only, each logged with its URL, size and SHA-256 in `docs/m4-spike.md`. At most 10 GB in total across the codespace. Nothing is downloaded on the Mac except within the approved install.
- **Installs:** none without the owner's approval. Every approved install goes in `INSTALL-LOG.md`.
- **Network:** the image and tool downloads above, plus reading official Android documentation. No Meta calls.
- **No real phones, no USB, no `fastboot`.**
- **Separate from M2:** a second Muse runs the spike in its own git worktree (`git worktree add ../m4-spike <final M1 SHA>`), so it can't collide with the M2 builder. Its files go under `spike/m4/` and `docs/m4-spike.md`, in one commit on that worktree. Large downloads go outside the repo (for example `/workspaces/m4-downloads/`) and are never committed.
- The usual Muse rules hold: no push, no `--disable-sandbox` or `--yolo`, keys never printed, and a list of every command run outside the sandbox.

## Done when
- [ ] `docs/m4-spike.md` answers questions 1–5, with sources, sizes and hashes.
- [ ] The owner has booted the stock arm64 image on the Mac (owner-observed), **or** the spike reports exactly why that couldn't happen.
- [ ] Path A or Path B has produced one boot that differs from stock in a way StarGate controls, shown in a screenshot (owner-observed), **or** the spike reports where both paths failed.
- [ ] Every install was approved first and is logged. One spike commit, not pushed.

## What happens next
Claude writes the full M4 spec for the chosen path, GPT reviews it, and M4 builds on Monday. If neither path boots by Sunday night, the owner decides between more time on M4 and the Tuesday fallback (record what works, clearly labelled).
