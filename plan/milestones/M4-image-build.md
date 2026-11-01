# M4: Build StarGate OS for a selection and boot it in the emulator (spec)

Status: v1 draft, 1 Nov 2026, for review. It's written **before** the spike's Mac results, so it covers both routes. The Mac result picks one (section 2), and only that route's section is built. Builds on M3 (final commit `e701acd82939a7cd9d8eef89813cd3427e4b5ef7`, reviewed) and the M4 spike (`m4-spike` branch, commit to be recorded after the Mac run).

## Goal
`stargate build` takes an accepted M3 plan and produces a StarGate build for **exactly** the selected services. Two selections give two different builds. Each one boots in the Android Emulator on the owner's Mac, shows a StarGate home screen listing only its services, and the services work:
- **Files:** the owner can upload a file from the Mac and download it again.
- **Assistant:** a small on-device model answers a question, with no network.

This is the core of the demo (scoring plan, video sections 5 and 6). It doesn't touch real phones.

## 1. Input: only an accepted plan
`stargate build --plan <plan.json> --out <dir>`
1. Validate the **whole** file against `plan-v1` (M3's validator). Exit 6 if it's invalid.
2. Check that `handoff.selection_result`, `handoff.build_allowed` and `handoff.reasons` match the top level. Exit 6 if they don't.
3. Build only if `build_allowed` is `emulator_only`. A `refused` plan (or `none`) stops with exit 7 **before any build step**, and prints the refusal reasons from the handoff.
4. The build reads only the `handoff` block from then on: services, chosen model and unresolved checks.

An `unconfirmed` plan may build, but every output and the home screen carry the label "**emulator experiment: fit not confirmed**".

## 2. Route: picked by the spike's Mac result
| Spike result on the Mac | Route M4 builds |
|---|---|
| Path A boots, and the marker reads back from the running system | **Route A, image**: the apps are baked into the emulator system image |
| Path A fails (for example dm-verity or boot failure) and Path B works | **Route B, configuration bundle**: stock image, and the apps are installed after boot |
| Neither works | Stop M4. The owner decides between more time and the Tuesday fallback (master plan) |

The route is recorded in master plan section 7 with the spike evidence. **Route B is always labelled "configuration bundle, not an image"**: in the build manifest, on the home screen, in the README and in the video.

## 3. What gets built (both routes)
Three small Android apps, built in the codespace with the spike's toolchain (JDK plus Android SDK build tools; Gradle only if needed and approved):
- **StarGate launcher** (home app): shows "StarGate", the selected services, the build ID, and the label from section 1 or 2 when one applies. It shows nothing for services that weren't selected.
- **Files module:** a small file server inside the app's own storage. It listens on the **emulator's loopback only**, and the Mac reaches it with `adb -s <serial> forward tcp:<port> tcp:<port>`. A random access code is generated on first start and shown on screen. Every request without it is refused. There's no LAN exposure in M4, so nothing on the owner's network can reach it.
- **Assistant module:** runs the chosen model on the device with no network permission (section 4). It's only included when the Assistant is selected.

**Route A** places the apps in the system image (for example as system apps), repacks it with the spike's proven method, and records every hash. **Route B** installs the same APKs after boot with `adb -s <serial> install`, sets the launcher as home, and records every command.

## 4. Assistant: runtime and model (decided first, as step 0)
The model must come from the handoff. M3's catalog currently has only SmolLM2 entries, and **for the demo we want a Meta model** (scoring plan: depth of Meta tooling, and the open-weight bonus if Q15 allows). So M4 starts with a short, bounded decision step that Muse documents in `docs/m4-assistant.md` and **stops for the owner's OK**:
1. **Runtime options** on arm64 Android, each with version, source, licence, download size, and whether a prebuilt Android library exists (no NDK build if avoidable): for example **ExecuTorch** (Meta's on-device runtime) and **llama.cpp**. Values are sourced or `unknown`.
2. **Model options:** Muse Glimmer (Q15: size, licence, formats, whether a runtime above can load it), a small Meta Llama (exact repo, revision, file bytes and licence; note whether the repo is gated and needs the owner to accept a licence), and the M3 SmolLM2 entries as the fallback.
3. A recommendation. Then new catalog entries go through the M3 catalog rules (sourced or estimated, per-entry provenance), M3's plan is re-run, and the build uses the model the **new plan's handoff** names. A model is never swapped in outside the plan.

**Limits:** model download at most **2 GB**. The model must fit the AVD's memory with room for Android (the AVD gets 4 GB RAM unless the fit numbers say otherwise). No model is downloaded until the owner approves the INSTALL APPROVAL REQUIRED block for it.

**If no on-device model works by Monday night**, the Assistant module isn't faked. The owner decides between dropping the Assistant from the video and showing it as "not ready". Either way it's labelled.

## 5. Build manifest and checks
Every build writes `build-manifest.json` (**`build-v1`**): the plan's SHA-256, the selection, the route, the build ID, each artifact (path, size, SHA-256), each app (package name, version, SHA-256), the model files (name, bytes, SHA-256) if any, and the unresolved checks from the handoff.

**Checks before a build is reported as done:**
- **Contents match the selection exactly.** A Files-only build contains no Assistant app and no model files. A Files + Assistant build contains both. The check reads the actual artifact (the image contents for Route A, the APK list for Route B), not just the manifest.
- The two demo builds have different manifests and different home screens.
- Route A: the image's size against its partition limit is checked and recorded. This resolves the "image size" check M3 left unresolved, for the emulator only.

## 6. Boot proof on the Mac (owner-run steps, written by Muse)
For each build, a **fresh, dedicated AVD** (for example `stargate-m4-files` and `stargate-m4-files-assistant`), launched with `-no-snapshot -wipe-data` and without `-writable-system`. The record has:
- `sys.boot_completed` = `1`;
- the build ID read back from the running system, matching the manifest;
- a screenshot of the home screen;
- Files: upload a test file from the Mac and download it again, with matching SHA-256 on both sides. A request without the access code is refused;
- Assistant: one question answered with the emulator's networking turned off for the test, plus the answer's time and the model ID.

**ADB safety** (from the spike): before every `adb` command, the device list must show only the emulator, and every command names its serial. If a physical device is listed, stop. No real phones, USB or `fastboot`.

**Mac hygiene:** every new tool, AVD or file goes on the cleanup list (`/mnt/project-files/stargate/mac/mac-install-log.md`) **before** it's installed, with its undo command. Everything stays in the user's home folder.

## 7. Carried over from M3's reviews
- **The explanation cap.** `muse-spark-1.3` spends tokens on reasoning, and both M3 live explanations were cut short at 2048. M4 raises `--explain`'s `max_completion_tokens` to **4096**, keeping one retry and the "cut short" label.
- `handoff.reasons` must equal `fit.reasons` for **every** result, not only for refused ones.
- A field listed in a catalog entry's `estimates` can't also be a sourced field.
- Any `finish_reason` other than `stop` counts as incomplete.
- Record the AOSP page date with the quoted sentence in `docs/inference-rules.md`.

## 8. Exit codes for `stargate build`
6: invalid or inconsistent plan. 7: the plan doesn't allow a build. 8: the build or a section 5 check failed. 0: built and checked. Boot proof (section 6) is recorded separately, because it runs on the Mac.

## 9. Tests (offline, in the codespace)
- Plan gate: invalid, inconsistent and refused plans stop with 6 or 7 before any build step (a stub build function is never called).
- Contents check: a Files-only build that wrongly contains the Assistant app or a model file fails with 8, and so does a Files + Assistant build that's missing one.
- Manifest: valid and invalid `build-v1` examples. Hashes match the files.
- Launcher: the services list is generated from the handoff only.
- Files: requests without the access code are refused, and the server binds to loopback only (tested on the host with the same code, or with a unit test of the bind address).
- Section 7 items each have a test.
- The full suite runs with sockets blocked.

## Done when
- [ ] The route is recorded in master plan section 7 with the spike's Mac evidence.
- [ ] `docs/m4-assistant.md` records the runtime and model decision, and the owner approved it (or the owner's decision under section 4).
- [ ] `stargate build` builds Files-only and Files + Assistant from two accepted plans, and both pass the section 5 checks (exit 0). A refused plan gives exit 7 with nothing built.
- [ ] Both builds boot on the Mac with the section 6 records (owner-observed).
- [ ] Files transfers a file both ways with matching hashes. The Assistant answers with networking off, or its status is labelled as in section 4.
- [ ] All tests pass offline, `stargate doctor` still passes, and the key scan is clean.
- [ ] Every install was approved first and is logged (codespace and Mac). One checkpoint commit per part, nothing pushed without the owner's OK, and the reviewer Muse checks each commit.

## How the work is split (to run in parallel)
- **M4a (builder Muse):** plan gate, route build, launcher, Files, manifest and checks, section 7 items. It starts as soon as the route is known.
- **M4b (second Muse):** the Assistant decision step (section 4), then the Assistant module. It can start the decision step **before** the Mac result, because it doesn't depend on the route.
- They meet at the Files + Assistant build.

## Out of scope
Real phones (M7), the real-phone build plan (M5), the full app (M6), the VPN module, Vault and Home, and any LAN exposure of Files.

## Network use allowed in M4
- Downloads only from an approved INSTALL APPROVAL REQUIRED list (toolchain, runtime library, model). The model is at most 2 GB, and the total stays within 10 GB as in the spike.
- Official documentation and model pages for the section 4 decision: at most 20 fetches, each logged in `docs/m4-sources.md`.
- One live `--explain` run to confirm the new cap, and one `stargate doctor` run.
- Nothing else. The launcher and Assistant don't request Android's network permission. Files needs it to listen on loopback, and it makes no outgoing connections (tested).
