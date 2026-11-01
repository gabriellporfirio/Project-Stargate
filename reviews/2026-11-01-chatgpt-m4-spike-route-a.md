# ChatGPT review: M4 Route A evidence and Part 2 prompt

Reviewed PR #32 at `87e9cff6b5e6eea85aa9a6369d118b8f44d738e7` on 1 November 2026. This updates the initial review after the spike commit and evidence copy were added.

**Verdict: the missing commit/report finding is resolved. Three corrections remain before accepting Path A as passed and sending the new Part 2 prompt.**

The pinned spike SHA, full image/APK hashes, symlink layout and post-boot command list now provide a useful record. I also inspected the Path B screenshot, which shows the stated launcher. Missing archive/ancillary hashes are honestly labelled. The scoped `-sysdir` workaround is consistent with [Android's documented system-directory option](https://developer.android.com/studio/run/emulator-commandline).

**Must fix 1 — complete the Path A boot evidence** (`plan/evidence/m4-spike-mac-results.md:61–75`). The successful marker run has no captured `sys.boot_completed=1`; the loop could also exit after ten minutes. The earlier value of 1 belongs to a different launch without the marker. The spike's proof rules require boot completion and marker read-back for the same repacked-image run. Recover that observation from existing records if available; otherwise perform a bounded owner-run confirmation of the same hashed image, recording both values and treating timeout as failure. Until then, label boot completion unverified rather than Path A fully passed.

**Must fix 2 — carry the partial-result branch through the prompt** (`plan/prompts/m4a-part2-route-a.md:41,50–67`). Step 3 allows an Assistant image failure and continuing with Files-only; Step 4 then unconditionally requires both builds to exit 0. Make the subsequent artifacts, Mac instructions and report conditional: if Assistant packaging fails, retain the Files-only output, report partial under M4 §10, and leave the reduced-demo decision with the owner. Do not invent a successful Assistant artifact or keep retrying merely to satisfy “both.”

**Must fix 3 — preserve the device guard** (prompt line 60). “Before every group” weakens M4 §6's check before each device command. Require the emulator-only inventory check before each action, use the explicit serial, and verify the AVD name matches the intended dedicated build AVD. Stop for an unexpected device/AVD.

**Should fix, non-blocking prompt clarifications:**
- Line 35: only formatting differences may be explained away; M3's schema must remain semantically unchanged.
- Line 40: package the entire approved manifest file set, rather than treating `.pte` and `tokenizer.model` as an independent payload definition.
- Line 24: perform the shared disk/peak-space check before the first large unpack/repack, including any Step 3 validation, and carry forward the spec's Mac free-space check.

The shared lock, no-new-live-calls rule, manifest binding and final artifact/boot checks otherwise remain aligned. Part 1 remains approved.

Evidence/specification/prompt review only. I did not inspect the unpushed product commits or run builds, emulator commands or live inference calls.
