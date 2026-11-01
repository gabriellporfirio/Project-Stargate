# M4a Part 1: corrections to the prompt (from GPT's review)

The prompt in `m4a-part1-build-core.md` stays exactly as it was sent. These corrections come from [GPT's review of it](../../reviews/2026-11-01-chatgpt-m4a-part1-prompt.md).

## Now: a short note for the running builder Muse
Paste this into the builder Muse right away. Muse takes it in after its current step, so it reaches Part 1C (the one live call) in time:
```
Two corrections to my Part 1 prompt. The spec wins as before.
1. Step 2 was wrong: the plan's handoff has NO per-file hashes (spec section 5a). Bind the model ID, revision, file names and sizes to the handoff. Require a SHA-256 for every file in the Assistant manifest. A binding mismatch or a missing hash gives exit 9. Then the contents check compares each real model file's hash with the manifest, and different content gives exit 8. Don't change M3's plan schema. Record the Assistant manifest's own SHA-256 in build-manifest.json. If you already built it this way, say so and leave it.
2. Step 11 was wrong: the command is `stargate plan ... --explain` with the inputs M3 section 6 supports, not `stargate --explain`. Before the live run, prove that the exact command you'll run uses /workspaces/m4a's code and /usr/local/bin/python3 (for example, run it through `/usr/local/bin/python3 -m stargate` with PYTHONPATH=/workspaces/m4a, and print stargate.__file__ in the same way). Check docs/m4-build.md first: if a live --explain or doctor run is already recorded, don't run it again. M4a gets one --explain run (with its one allowed retry) and one doctor run in all of M4.
Also: keep the route "not yet" value as internal draft state only (no exit 0 and no finished build may carry it), and if the AOSP page date isn't on file, mark the citation date as PENDING in docs/inference-rules.md and in your report rather than as done.
```

## After Part 1: the reviewer Muse checks these on top of its normal review
- **Hash binding:** model ID, revision, names and sizes are bound to the handoff, with exit 9 for a mismatch. Hashes come only from the Assistant manifest, with exit 9 for a missing hash. A same-name, same-size file with changed content fails the contents check with exit 8. M3's schema is unchanged. The manifest's own hash is in `build-manifest.json`. Tested on a real M3-generated plan.
- **Live run:** it used `stargate plan ... --explain`, the run provably used the M4a worktree code, and there's at most one `--explain` run and one doctor run.
- **Draft route:** the "not yet" route value can't reach exit 0 or a finished build.
- **AOSP date:** shown as pending if it wasn't on file.
- **Build slot:** before Part 2, both Muses share one lock file (for example `/workspaces/.android-build.lock`, taken with `flock`) instead of a `ps` snapshot. This goes into the Part 2 prompt.
