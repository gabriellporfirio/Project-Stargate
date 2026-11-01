# ChatGPT review: M4 spike Route A decision

Reviewed PR #32 at `10771ad059c8f7ff96c348ce9d7a3604af3f085f` on 1 November 2026.

**Verdict: the Route A decision is consistent with the reported Mac result; one evidence/handoff gap must be closed before this PR unblocks Part 2.**

The reported repacked-image boot and matching random marker support Route A under M4 §2. Keeping the separately tested Path B as a fallback is sensible. The marker test establishes the spike's image path; M4 still needs the real apps/model baked in and both final builds verified.

**Must fix — pin the spike commit and its evidence.** The new master-plan row still says the spike commit will be added later. M4 §11 requires M4a's first Part 2 commit to merge that exact recorded commit. The PR has only a narrative summary and abbreviated artifact hashes; the connected product repository still exposes only its seed, so I cannot inspect the underlying report.

Add the final spike commit SHA and link an accessible, pinned `docs/m4-spike.md` record. An evidence-only copy in this planning repository is sufficient. It should contain the already-required records:

- Full artifact SHA-256 values and sizes, including the stock package/system image, repacked image and Path B APK.
- The exact successful launch command and `-sysdir` directory layout/targets, showing which `system.img` was used, plus the fresh dedicated AVD, `-no-snapshot -wipe-data` and absence of `-writable-system`.
- Captured boot-complete and marker read-back, the post-boot command list showing no Path A install/push or image mutation, and the Path B install/home-screen evidence.

Use the existing Mac outputs. If a required observation was not captured, mark it missing rather than infer it from “passed.” Until the commit/report is pinned, Part 1 can continue but Part 2's spike merge remains pending.

**Launch change — accepted for this setup.** [Android's command-line documentation](https://developer.android.com/studio/run/emulator-commandline) supports `-sysdir` for selecting the system directory and also documents `-system`. Keeping the working `-sysdir` method is reasonable; treat the failed `-system` attempt as an observation on this Mac/emulator configuration, without claiming a universal emulator behavior.

No other blockers found. This is a review of the decision and available records, not independent verification of the owner's Mac run. No installs, builds, emulator commands or live inference calls were performed.
