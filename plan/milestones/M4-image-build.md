# M4: Build StarGate OS for a selection and boot it in the emulator (spec)

Status: v2.3, 1 Nov 2026. v2.3 adds section 4d, after-boot model delivery for Route A (owner's decision, 1 Nov 22:57, master plan section 7), with matching edits to sections 3, 5, 6, 8, 9 and 10, following [GPT's review of the Part 3 handoff](../../reviews/2026-11-01-chatgpt-m4a-part2-and-part3.md). v2.2, 1 Nov 2026. v2.2 lets M4a start its route-independent Part 1 before the Mac result (section 11). v2.1, 1 Nov 2026. v2 folded in [ChatGPT's review of v1](../../reviews/2026-11-01-chatgpt-m4-image-build.md) (five must-fix, one should-fix). v2.1 fixes the one finding in the [re-review](../../reviews/2026-11-01-chatgpt-m4-image-build-v2.md): where the expected model hashes come from (section 5a). It's written **before** the spike's Mac results, so it covers both routes. The Mac result picks one (section 2), and only that route's parts are built. Builds on M3 (final commit `e701acd82939a7cd9d8eef89813cd3427e4b5ef7`, reviewed) and the M4 spike (`m4-spike` branch, commit to be recorded after the Mac run).

## Goal
`stargate build` takes an accepted M3 plan and produces a StarGate build for **exactly** the selected services. Two selections give two different builds. Each one boots in the Android Emulator on the owner's Mac, shows a StarGate home screen listing only its services, and the services work:
- **Files:** the owner can upload a file from the Mac and download it again.
- **Assistant:** a small on-device model answers a question, with no network.

This is the core of the demo (scoring plan, video sections 5 and 6). It doesn't touch real phones.

## 1. Input: only an accepted plan
`stargate build --plan <plan.json> --out <dir>`
1. Validate the **whole** file against `plan-v1` (M3's validator). Exit 6 if it's invalid.
2. Check that `handoff.selection_result` equals the top-level selection result, `handoff.build_allowed` equals the top-level `build_allowed`, and `handoff.reasons` equals `fit.reasons` exactly (same items, same order). Exit 6 if any of them differ.
3. Build only if `build_allowed` is `emulator_only`. A `refused` plan (or `none`) stops with exit 7 **before any build step**, and prints the refusal reasons from the handoff.
4. If the Assistant is selected and the handoff's model is missing, `null` or unresolved, stop with exit 9 **before any build step**. The message says a concrete catalog entry and a fresh M3 plan are needed. The build never picks or swaps in a model on its own.
5. The build reads only the `handoff` block from then on: services, chosen model and unresolved checks.

An `unconfirmed` plan may build, but every output and the home screen carry the label "**emulator experiment: fit not confirmed**".

## 2. Route: picked by the spike's Mac result
| Spike result on the Mac | Route M4 builds |
|---|---|
| Path A passed: it boots, and the marker reads back from the running system | **Route A, image**: the apps and the model are baked into the emulator system image |
| Path A failed, blocked or not tested, and Path B passed | **Route B, configuration bundle**: stock image, and the apps and model are installed after boot |
| Neither path passed | Stop M4. The owner decides between more time and the Tuesday fallback (master plan) |

Path A that is **blocked or not tested** (not only failed) also leads to Route B, and the record says which it was. Route B is a full M4 route, not a partial result, as long as it's labelled. The route is recorded in master plan section 7 with the spike evidence. **Route B is always labelled "configuration bundle, not an image"**: in the build manifest, on the home screen, in the README and in the video.

## 3. What gets built
Up to three small Android apps, built in the codespace with the spike's toolchain (JDK plus Android SDK build tools; Gradle only if needed and approved). **Each module is included only when its service is selected**, so an Assistant-only plan gets no Files app, and a Files-only plan gets no Assistant app or model.
- **StarGate launcher** (home app, always included): shows "StarGate", the selected services, the build ID, and the label from section 1 or 2 when one applies. It shows nothing for services that weren't selected.
- **Files module:** a small file server inside the app's own storage (section 3a).
- **Assistant module:** runs the chosen model on the device with no network permission (section 4).

**Route A** places the apps and the model files in the system image **before boot**, repacks it with the spike's proven method, and records every hash. Nothing is installed or pushed after boot, **with one recorded exception: the Assistant's model files when they don't fit the image (section 4d)**. No APK is ever installed after boot on Route A. **Route B** installs the same APKs after boot with `adb -s <serial> install`, pushes the model files (section 4b), sets the launcher as home, and records every command.

Uploads to Files and caches the apps create while running are normal use, not installs, on both routes.

### 3a. Files: the security boundary
- **Inside the emulator:** the server listens on `127.0.0.1` only, never on all addresses.
- **On the Mac:** the owner reaches it with `adb -s <serial> forward tcp:<port> tcp:<port>`. The ADB server must not be started with `-a` (which listens on all addresses), and no other forward or reverse is set up.
- **Access code:** a random code is generated on first start and shown on screen. A request with **no** code or a **wrong** code is refused.
- **Paths:** every file name stays inside the app's own upload folder. Names with `..`, absolute paths, encoded slashes or links pointing outside are refused.
- **Size:** one upload is at most **50 MB**, and the folder holds at most **200 MB**. Anything larger is refused before it's written, and a refused upload leaves no partial file.
- There's no LAN exposure in M4, so nothing on the owner's network can reach it.

## 4. Assistant: runtime, model and payload
### 4a. Decided first (step 0, the second Muse)
The model must come from the handoff. M3's catalog currently has only SmolLM2 entries, and **for the demo we want a Meta model** (scoring plan: depth of Meta tooling, and the open-weight bonus if Q15 allows). So M4b starts with a short, bounded decision step that Muse documents in `docs/m4-assistant.md` and **stops for the owner's OK**. For the chosen pair it **pins the complete payload**:
1. **Runtime:** name, exact version, source, licence, and whether a prebuilt Android library exists (no NDK build if avoidable). Candidates include **ExecuTorch** (Meta's on-device runtime) and **llama.cpp**.
2. **Model files:** the exact file set the runtime needs, for example the model file in the runtime's format (such as ExecuTorch's `.pte` or llama.cpp's `.gguf`), the tokenizer, and any config or support files. Each with name, bytes, SHA-256 and source revision.
3. **Conversion:** whether a ready-made file in that format exists. If the model must be converted, the tool, its version and where conversion runs are named, and they go in the install list. A ready-made file is preferred.
4. **Android needs:** minimum Android version, CPU type (arm64), and RAM needed using `docs/fit-budgets.md`'s method.
5. **Model options compared:** Muse Glimmer (Q15: size, licence, formats, whether a runtime above can load it), a small Meta Llama (exact repo, revision, file bytes and licence; whether the repo is gated and needs the owner to accept a licence), and the M3 SmolLM2 entries as the fallback.
6. A recommendation. Then new catalog entries go through the M3 catalog rules (sourced or estimated, per-entry provenance), M3's plan is re-run, and the build uses the model the **new plan's handoff** names. A model is never swapped in outside the plan.

Values are sourced or `unknown`. If a needed value stays `unknown`, the pair isn't picked.

### 4b. Where the model lives, and how the app reads it
The model is too large to ship inside the APK, so the files are delivered separately and the app opens them by path.
- **Route A:** the files are placed in the system image before boot, in a read-only folder Muse names in the build (for example under `/product/`). The Assistant app opens them **from that folder directly**, with no extracted copy. If the app process can't read them (for example Android's file-access rules block it), that's a recorded Route A failure for the Assistant, not a reason to push files after boot. The only exception is section 4d, which the owner chose because the model doesn't fit the product partition.
- **Route B:** the files are pushed after boot into the app's own external files folder (`/sdcard/Android/data/<package>/files/model/`), which the app can read without extra permissions. Every push command and its target path are recorded.
- **Hash chain:** each file's SHA-256 is recorded at four points: in the build manifest, after transfer to the Mac (`shasum -a 256`), inside the built artifact (image or pushed file), and **by the app itself** when it loads the file (shown on screen or written to its log). All four must match.
- **AVD space:** each AVD's data and system sizes are set and recorded. The space needed is the model files plus any extracted copy plus **1 GB** headroom, and it's checked before boot.

### 4d. Route A exception: apps in the image, model added after boot
Part 2 measured the model (1,138,135,470 bytes) against the product partition's free space (305,967,104 bytes): it doesn't fit. The owner chose (1 Nov 22:57, master plan section 7) to keep the Assistant **app** in the image and to copy the **model files only** into the app's own folder after first boot, as in the Mac proofs.
- **Label:** every output, the build manifest, the README and the video say "**apps in image; model added after boot**". It is never called a pure image build.
- **What may be copied after boot:** only the model files listed in the approved Assistant manifest, into `/sdcard/Android/data/<package>/files/model/`. Nothing else. No APK is installed after boot.
- **The payload is checked, not just the manifest.** The build reads the actual model files from an immutable snapshot (a folder the build copies them into under the build lock, then hashes) and compares them with `assistant-manifest.json` and with M3's handoff (section 5a). The snapshot's path, and each file's name, bytes and SHA-256, go in `build-manifest.json` under `model_delivery: "after_boot"`, and that snapshot is what the owner downloads.
- **Exit codes:** a binding error (model ID, revision, file names or sizes differ from the handoff, or a hash is missing) stops with **9**. A missing payload file, or one with the right size but a different hash, fails with **8**.
- **The image holds no model file.** The section 5 check reads the real image and fails with 8 if any model file is found in it.
- **Mac steps:** the app is launched once and stopped so it creates its own folder (never `mkdir` from the shell); then each model file is copied with `adb -s <serial> push`, after checking it with `shasum` on the Mac, and hashed again on the device. The four-point hash chain in 4b still applies. Every push is listed in the boot record as the recorded exception.
- **Result:** after the build passes, the result is "**build ready, Mac proof pending**". It becomes complete only after the section 6 boot record on the Mac (section 10).

### 4c. Limits
Model download at most **2 GB**. The model must fit the AVD's memory with room for Android (the AVD gets 4 GB RAM unless the fit numbers say otherwise). No model, runtime or conversion tool is downloaded until the owner approves the INSTALL APPROVAL REQUIRED block for it.

## 5. Build manifest and checks
Every build writes `build-manifest.json` (**`build-v1`**): the plan's SHA-256, the selection, the route, the build ID, each artifact (path, size, SHA-256), each app (package name, version, SHA-256), the model files (name, bytes, SHA-256, target path on the device) if any, `model_delivery` (`in_image`, `after_boot` under section 4d, or `none`) with the payload snapshot's path when it's `after_boot`, the runtime version, and the unresolved checks from the handoff.

**Checks before a build is reported as done (all read the actual artifact, not just the manifest):**
- **Apps match the selection exactly.** The check lists the real package names inside the image (Route A) or inside each APK to be installed (Route B, read from the APK itself), and compares them with the selection. An unselected app, or a selected one that's missing, fails.
- **Model files match exactly.** The check lists every file in the model folder of the image (Route A) or of the Route B bundle, and the assets inside every APK. A model file in a build without the Assistant fails. In a build with the Assistant, the files must match the approved Assistant manifest as section 5a describes; wrong bytes fail. Under section 4d the image must hold **no** model file, and the after-boot payload snapshot is checked file by file instead (missing or wrong bytes fail with 8).
- The two demo builds have different manifests and different home screens.
- Route A: the image's size against its partition limit is checked and recorded. This resolves the "image size" check M3 left unresolved, for the emulator only.

### 5a. Where the expected model hashes come from
M3's plan and catalog name the model, its revision, and each file's name and size, but **not** per-file SHA-256 values. M3's schema stays as it is. The expected hashes come from the **approved Assistant manifest** (`assistant-manifest.json`, section 11), which M4b writes after downloading the files. There are two separate approvals: the owner approves the install list **before** anything is downloaded, and approves the completed manifest (with its hashes) **after** hashing and before any build uses it. It's committed, and its own SHA-256 is recorded in `build-manifest.json`.

Before any build step, `stargate build` binds the manifest to the plan, and stops with exit 9 if any of these differ:
1. The manifest's model ID and source revision equal the handoff's.
2. The manifest's file set equals the handoff's: the same file names, and the same size for each file.
3. Every file in the set has a SHA-256 in the manifest.

Then the section 5 checks compare the hash of every model file in the artifact with the manifest. A file with the right name and size but different content fails with 8.

## 6. Boot proof on the Mac (owner-run steps, written by Muse)
 (owner-run steps, written by Muse)
Carried over from the spike:
- **Transfer:** the owner downloads each artifact from the codespace through the browser and checks it with `shasum -a 256` against the manifest. A mismatch means stop.
- **Launch:** each build gets a **fresh, dedicated AVD** (for example `stargate-m4-files` and `stargate-m4-files-assistant`), launched with `-no-snapshot -wipe-data` and without `-writable-system`. The **exact launch command**, including the image path, is recorded, so the record shows which image booted. A repacked image is booted with `-sysdir` pointing at a folder that holds it alongside the stock image's other files, never with `-system`: on the owner's Mac (emulator 37.2.13.0), `-system` silently booted the stock image instead (spike, 1 Nov). The build ID read-back is what proves which image ran.

Each boot record has:
- `sys.boot_completed` = `1`;
- the build ID read back from the running system, matching the manifest;
- a screenshot of the home screen;
- **every** `adb` command run after boot. For Route A this list has no `install` or `push`, which proves the apps and model came from the image. Under section 4d the only allowed `push` lines are the model files, each with its on-device SHA-256, and they're marked as the recorded exception;
- Files (when selected): upload a test file from the Mac and download it again, with matching SHA-256 on both sides. A request with no code and one with a wrong code are both refused. The listeners are shown to be loopback-only: inside the emulator with `adb -s <serial> shell ss -ltn` (or `netstat`), and on the Mac with `lsof -nP -iTCP:<port> -sTCP:LISTEN`, both showing `127.0.0.1`;
- Assistant (when selected): the SHA-256 the app reports for the model files, matching the manifest, and one question answered with the emulator's networking turned off for the test, plus the answer's time and the model ID.

**ADB safety** (from the spike): before every `adb` command, the device list must show only the emulator, and every command names its serial. If a physical device is listed, stop. No real phones, USB or `fastboot`.

**Mac hygiene:** every new tool, AVD or file goes on the cleanup list **before** it's installed, with its undo command. There are two copies:
- **On the Mac:** `~/stargate-cleanup-log.md`. Muse's Mac steps tell the owner to add the row there first. This is the copy the final cleanup uses.
- **Planning copy:** `/mnt/project-files/stargate/mac/mac-install-log.md`, kept in step by Claude. The Mac can't read it.

Everything stays in the user's home folder (tools under `~/stargate-spike/`, M4 files under `~/stargate-m4/`).

## 7. Carried over from M3's reviews
- **The explanation cap.** `muse-spark-1.3` spends tokens on reasoning, and both M3 live explanations were cut short at 2048. M4 raises `--explain`'s `max_completion_tokens` to **4096**, keeping one retry and the "cut short" label.
- `handoff.reasons` must equal `fit.reasons` for **every** result, not only for refused ones (the M3 validator, and the build gate in section 1).
- A field listed in a catalog entry's `estimates` can't also be a sourced field.
- Any `finish_reason` other than `stop` counts as incomplete.
- Record the AOSP page date with the quoted sentence in `docs/inference-rules.md`.

## 8. Exit codes for `stargate build`
6: invalid or inconsistent plan. 7: the plan doesn't allow a build. 8: the build or a section 5 check failed. 9: the Assistant is selected but its model is unresolved, or the Assistant manifest doesn't match the plan (section 5a), including a binding error in a section 4d payload. 8 also covers a missing or wrong-content model file in a section 4d payload. 0: built, and the section 5 checks passed. **Exit 0 means only that the artifacts are right.** Whether M4 is complete is decided by section 10, after the boot proof on the Mac.

## 9. Tests (offline, in the codespace)
- Plan gate: invalid, inconsistent (including `handoff.reasons` different from `fit.reasons`) and refused plans stop with 6 or 7, and an unresolved Assistant model stops with 9, all before any build step (a stub build function is never called).
- Selection: Files-only, Assistant-only and Files + Assistant plans each produce exactly their apps. An Assistant-only build has no Files app.
- Contents check, each failing with 8: a Files-only build that contains the Assistant app; one with a model file hidden in an APK's assets or in the model folder; a Files + Assistant build missing either app; a build whose model file has the right name and size but different content.
- Manifest binding (section 5a), using a **real plan generated by M3's code** with a small test model entry: the correct payload passes; a manifest with a different model ID, revision, file name or file size stops with 9; a manifest missing a file's hash stops with 9.
- Section 4d: a correct after-boot payload passes; a payload file with the same size but a different hash fails with 8; a missing payload file fails with 8; a payload whose names or sizes differ from the handoff stops with 9; an image that still contains a model file fails with 8; a Files-only build that carries a model payload fails with 8.
- Manifest: valid and invalid `build-v1` examples, including `model_delivery`. Hashes match the files.
- Launcher: the services list is generated from the handoff only.
- Files handler tests (on the host, same code): no code and wrong code refused; `..`, absolute and encoded paths refused; an upload over 50 MB, and one that would pass 200 MB in total, refused with no partial file left; the server's listening socket is `127.0.0.1` (checked on the running test server, not only in the settings).
- Section 7 items each have a test.
- The full suite runs with sockets blocked, except the loopback test server above.

## 10. Results: complete, partial or blocked
M4's result is one of:
- **Build ready, Mac proof pending:** a build passed section 5 in the codespace but has no Mac boot record yet. This is never reported as complete.
- **Complete:** both demo builds pass section 5, boot with the section 6 records, Files transfers with matching hashes, and the Assistant answers with networking off. A section 4d build counts, labelled "apps in image; model added after boot".
- **Partial:** everything works except the Assistant (it's missing, doesn't load, or doesn't answer), **or** only one of the two demo builds has a boot record. The record names what's missing. The owner then decides on the reduced demo (for example drop the Assistant from the video, or show it labelled "not ready"), and that decision is recorded in master plan section 7. A "not ready" Assistant never counts as complete.
- **Blocked:** neither spike path passed, or a needed approval, disk space or time ran out. The record says which.

**If no on-device model works by Monday night**, the Assistant module isn't faked: M4 is reported as partial and the owner decides as above.

## Done when (complete)
- [ ] The route is recorded in master plan section 7 with the spike's Mac evidence.
- [ ] `docs/m4-assistant.md` pins the runtime and the complete model payload (section 4a), and the owner approved it.
- [ ] `stargate build` builds Files-only and Files + Assistant from two accepted plans, and both pass the section 5 checks (exit 0). A refused plan gives exit 7 with nothing built.
- [ ] Both builds boot on the Mac with the section 6 records (owner-observed).
- [ ] Files transfers a file both ways with matching hashes, refuses no and wrong codes, and listens on loopback only. The Assistant answers with networking off, and its reported model hashes match.
- [ ] All tests pass offline on the combined commit, `stargate doctor` still passes, and the key scan is clean.
- [ ] Every install was approved first and is logged (codespace and Mac). One checkpoint commit per part, nothing pushed without the owner's OK, and the reviewer Muse checks each commit, including the combined one.

If any line can't be ticked, M4 is reported as partial or blocked under section 10, not done.

## 11. How the work is split (to run in parallel)
**Two workers, each in its own worktree, both from the M3 commit `e701acd82939a7cd9d8eef89813cd3427e4b5ef7`:**

| | M4a (builder Muse) | M4b (second Muse) |
|---|---|---|
| Worktree and branch | `/workspaces/m4a`, branch `m4a-build` | `/workspaces/m4b`, branch `m4b-assistant` |
| Starts | **Part 1** now: the route-independent work (section 1 plan gate, section 5a binding, `build-v1`, the section 5 checks on APKs and model folders, section 7 items, the launcher and Files apps). **Part 2** when the route is known: route packaging (image or bundle), the spike merge, the Route A image checks, both demo builds and the Mac steps | now (step 0 doesn't depend on the route) |
| Owns these files | `stargate/build/` and the `build` CLI command, the launcher and Files apps, `build-v1`, the section 5 checks, the section 7 items, `docs/m4-build.md` | the Assistant app, `docs/m4-assistant.md`, `docs/m4-sources.md`, the new catalog entries in `catalog/models.json` |
| Doesn't touch | the Assistant app, the catalog | the build code, the launcher, Files, section 7 items |
| Tool folders it may write | `/workspaces/m4a-tools/`, `/workspaces/m4a-downloads/` | `/workspaces/m4b-tools/`, `/workspaces/m4b-downloads/` |

- **The spike:** M4a's first **Part 2** commit brings in the recorded spike commit on purpose (`git merge <spike commit>`, with the commit named in the message). The spike's tools in `/workspaces/m4-tools/` are **read-only** for both workers. If a worker needs more tools, they go in its own tool folder through its own approval.
- **What M4b hands over:** `assistant-manifest.json`, with the model ID and source revision exactly as the new plan's handoff names them, the Assistant APK (path, package name, version, SHA-256), the runtime version, each model file (name, bytes, SHA-256), the minimum Android version, the RAM need, and the target path for each route (section 4b). M4b computes the hashes from the downloaded files, and the owner approves the completed manifest before any build uses it (section 5a). M4a only reads it (section 5a).
- **Joining up:** M4a is the only integrator. It merges `m4b-assistant` into `m4a-build` with a merge commit, then runs the full test suite, the section 5 checks and both demo builds **on that combined commit**. The reviewer Muse checks the combined commit.
- **Shared limits in the codespace:**
  - At most **one** Android or Gradle build runs at a time across both workers, with at most 2 workers and 2 GB of heap.
  - Before downloading, each worker records free space and estimates its peak, including both demo images (Route A), unpacked and repacked copies, model files and any extracted or converted copy. It stops if free space is less than the combined peak of both workers plus 5 GB.
  - Downloads stay within **10 GB in total across both workers**, model included.
- **Shared limits on the Mac:** the owner records free space before the transfer. Two AVDs plus both images plus the model must leave at least 5 GB free, or the first AVD is deleted before the second is created.
- **Live calls:** M4a makes the one live `--explain` run and the one `stargate doctor` run. M4b makes no Meta or Baseten calls.

## Out of scope
Real phones (M7), the real-phone build plan (M5), the full app (M6), the VPN module, Vault and Home, and any LAN exposure of Files.

## Network use allowed in M4
- Downloads only from an approved INSTALL APPROVAL REQUIRED list (toolchain, runtime library, model, any conversion tool). The model is at most 2 GB, and the total stays within 10 GB across both workers.
- Official documentation and model pages for the section 4 decision: at most 20 fetches, each logged in `docs/m4-sources.md`.
- One live `--explain` run to confirm the new cap, and one `stargate doctor` run, both by M4a.
- Nothing else. The launcher and Assistant don't request Android's network permission. Files needs it to listen on loopback, and it makes no outgoing connections (tested).
