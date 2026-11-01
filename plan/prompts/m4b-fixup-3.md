# M4b fixup 3: what the Mac proof found (second Muse)

On 1 Nov the owner ran the Assistant on the Mac emulator (stock API 34 AVD, 6 GB RAM, Wi-Fi off). The model loaded and answered offline, but it hit three problems:

1. **Model folder permissions.** The Mac steps made `files/model` with `adb shell mkdir` before the app had ever run. The folder ended up owned by `shell` with mode `drwxrws---`, so the app (uid 10141) couldn't see it, and the app said "model files not found". The APK isn't debuggable, so `run-as` failed. Deleting the app's folder while Android was using it caused FUSE "Software caused connection abort" and "Input/output error" until a reboot. The workaround was emulator root: push into `/data/media/0/Android/data/com.stargate.assistant/files/model` and `chown` it to the app's uid and gid.
2. **Answers ran on.** The literal end-of-turn token "<|eot_id|>" showed up on screen, which proves generation doesn't stop at it. Asked "What's the current battery level", the model invented "24%", then a charging dialogue, then "Task 1: Sample Data…". This looks like a missing chat template or stop token, plus no length cap.
3. **System crash on first boot.** On the first boot after `-wipe-data`, system_server crashed once (LockSettingsService gatekeeper NullPointerException) and Android restarted. That's the stock image, not our app. It means the steps must wait for boot again after installing.

Proof screenshot: [m4b-proof.png](../evidence/m4b-proof.png). It shows both on-screen hashes matching, the answer with "<|eot_id|>", prompt_tokens 12, and about 56 tokens a second.

## Paste into the second Muse (in `/workspaces/m4b`)
```
StarGate M4b fixup 3: fixes from the owner's Mac proof. Same rules as before: you own the Assistant app, its docs, the catalog entry and assistant-manifest.json; /workspaces/m4-tools is read-only; NO network; no Meta or Baseten calls; never push; keys never printed; /usr/local/bin/python3. Before any Android build, take the shared lock: flock /workspaces/.android-build.lock <command> (at most 2 workers, 2 GB heap). Start by checking that git log -1 shows 6bb6681 on m4b-assistant.

What happened on the Mac (stock android-34 arm64 AVD, Wi-Fi off): (a) docs section 10 had the owner run "adb shell mkdir -p .../files/model" before the app's first launch, so the folder was owned by shell with mode drwxrws--- and the app showed "ERROR: model files not found". The APK isn't debuggable, so run-as wasn't available. (b) Once the files were readable, the question "What's the current battery level" produced an invented "24%" and then rambled on into made-up tasks without stopping. A second question ("3-item packing list for a rainy day hike") gave three items, then "5. 3 Items for a hotel room?" and the literal text "<|eot_id|>" on screen: the end-of-turn token is being printed as text instead of stopping generation. (c) system_server crashed once on the first boot after -wipe-data (gatekeeper NullPointerException, stock image), so Android restarted mid-steps.

Fix:
1. Model folder. On launch the app creates its own model folder (getExternalFilesDir(null) plus "model", mkdirs) before it checks for files, so the folder is always owned by the app. The error screen says WHICH check failed for each path: folder missing, file missing, not readable, or wrong size. Show the expected file names. Never show hashes as passed when they weren't checked.
2. Prompt format. Check how the app calls the ExecuTorch Llama runner today. Use the Llama 3.2 Instruct chat format exactly as the model card or ExecuTorch docs on disk give it (system, user and assistant headers, with the end-of-turn token), and stop generating at the end-of-turn and end-of-text tokens. Quote the file you took the format and token IDs from. If it isn't on disk, say so and mark it "unknown, needs checking", and don't guess.
3. Behaviour. Add a short fixed system message: you are an offline assistant on this phone; you cannot see the phone's sensors, battery, files, time or the internet; say so plainly when asked about them; keep answers short. Cap new tokens at 256 (one setting). Use the model card's recommended sampling defaults if they're on disk, otherwise keep the current values and note that.
4. Docs section 10 (Route B quick test), zsh-paste-clean, one command per line, adb -s "$SERIAL" throughout:
   - After install: launch the app once with am start -W -n com.stargate.assistant/.MainActivity, then am force-stop, so the app creates its own folder. Only then adb push the two files into files/model/. Never mkdir it from the shell, and never rm the app's folder while it's running.
   - Re-wait for sys.boot_completed after install (the stock image can restart once on first boot).
   - Launch with am start -n, not monkey.
   - Add an "If the app still says not found" fallback for the EMULATOR ONLY: adb root, push into /data/media/0/Android/data/com.stargate.assistant/files/model/, chown to the uid and gid of the files folder (read them with stat -c %u and %g), restorecon -R, then adb unroot. Mark it as emulator-only and never for a real phone.
   - Proof: screencap to m4b-proof.png, settings get global wifi_on shows 0, emu kill, then adb devices.
5. Screen (owner direction: no StarGate branding in the product, clean UI). The proof screenshot showed "prompt_tokens":12 for a one-line question (which also suggests no chat template) and a raw JSON stats dump under the answer. Rename the visible app title and label to "Assistant" (keep the package name com.stargate.assistant for now). Replace the JSON dump with one short line, for example "Offline · 26 tokens · 0.7 s", with the full stats behind a "Details" toggle. Keep the model ID and the two hashes visible but small.
6. Tests: folder creation and the per-check error messages; the exact prompt string for one sample question (golden test); stopping at the end-of-turn token (with a fake runner); the token cap; the stats line. Keep the existing tests passing.

Rebuild the APK (contents change). Run the full offline suite and the two key scans. Make ONE commit on m4b-assistant ("M4b fixup 3: app-owned model folder, Llama chat format and stop tokens, Mac steps from the proof run, cleaner screen") and save /tmp/m4b-fixup3-report.md with: each item fixed / not fixed with file:line; the source file for the chat format and token IDs; the new APK bytes and SHA-256; the test count; the scan results; and the commit SHA.
```
Paste Muse's report into the project thread.

## Knock-on for M4a Part 2
The Part 2 prompt merges `m4b-assistant` at `6bb6681` and stops if the tip is different. If fixup 3 lands first, add this line when pasting Part 2: "Step 1b: merge m4b-assistant at NEW_SHA (the M4b fixup 3 commit) instead of 6bb6681. It's 6bb6681 plus one reviewed-by-owner fix commit." Replace NEW_SHA with the commit from the fixup 3 report.
