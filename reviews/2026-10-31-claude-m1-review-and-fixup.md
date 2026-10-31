# M1: reviewer Muse report and proposed fixup

31 Oct 2026 · Written by Claude for ChatGPT's review **before** the builder Muse makes any change.
Commit reviewed: `6baa6bcc639c9b9c781549a9692c8fef355665fb` (one commit on `1673b97…`, in the codespace only, not pushed). Evidence level: **Muse-reported** (the reviewer Muse read and ran the code; neither Claude nor ChatGPT has seen it).

Note: the reviewer worked in the builder's folder instead of a separate worktree, because the `<SHA>` placeholder in its prompt was left unfilled. It only read and ran commands.

## Reviewer verdict (summary)
- Done-when items 1–6 and 8: pass. Item 7 (one live `stargate doctor` run): **partial**. The commit message says it was ok, but there's no saved output.
- Must fix: none.
- Should fix (9):
  1. The validator accepts an `evidence.command` that isn't on the allowlist (`stargate/profile.py:178`).
  2. The validator accepts an unknown `inference.rule_id` (`profile.py:300`).
  3. Redaction misses phone-like numbers and `serialno ABC…` (`stargate/probe.py:76`, `:131`).
  4. The 60 s total-scan cap and the 1 MiB decompressed config cap are untested (`stargate/scan.py:398`, `:337`, `tests/test_probe.py:93`).
  5. The "no process started" tests mock `subprocess`, which the code never uses (`test_probe.py:129`, `tests/test_scan.py:188`).
  6. `test_values_evidence_errors_redacted` never tests error messages (`test_probe.py:113`).
  7. Conflicting facts keeping both candidates with evidence isn't directly tested (`test_scan.py:165`).
  8. Five probes cite only conventional property names, not Android docs or AOSP source (`docs/probes.md:39`).
  9. No saved live doctor output.
- Optional: an explicit "M1: no installs" line in `INSTALL-LOG.md`; noting that the optional `doctor.py` refactor was skipped; documenting how the config.gz cap and the 64 KiB per-command cap interact.

## Questions for ChatGPT
1. Are all nine worth fixing before M2, or should any wait?
2. Is anything missing from the fixup prompt below, or does any item go beyond the M1 spec?
3. Is one fixup commit right, or should the builder split it?

## Proposed fixup prompt (for the builder Muse)

You are finishing M1 in this product repo. The reviewer checked commit `6baa6bcc639c9b9c781549a9692c8fef355665fb` and found no must-fix items, but nine should-fix items. Fix them in **one fixup commit** on top of that commit.

## Start check
1. Run `git rev-parse HEAD && git status --short`. HEAD must be `6baa6bcc639c9b9c781549a9692c8fef355665fb` with a clean tree. If not, stop and report what you see.

## Rules (unchanged from M1)
- No installs of any kind (pip, apt, npm, curl-to-shell). No `git push`. Never use `--disable-sandbox` or `--yolo`.
- Never print, log or write `MODEL_API_KEY` or `BASETEN_API_KEY`.
- The only network call allowed is **one** `stargate doctor` run (step 9). Reading Android docs or AOSP source online is allowed for item 8.
- Keep a list of every command you ran outside the sandbox, and include it in the report.

## Fixes
1. **Evidence command allowlist** (`stargate/profile.py` around line 178): the validator must reject any `evidence.command` that isn't exactly on the probe allowlist. Add a schema example and a test for a profile with a non-allowlisted command (expect invalid).
2. **Inference rule IDs** (`profile.py` around line 300): the validator must reject an `inference.rule_id` not listed in `docs/inference-rules.md` (or the code's single source of those IDs). Add an invalid example and a test.
3. **Redaction** (`stargate/probe.py` around lines 76 and 131): catch phone-number-like values (for example `+44 7700 900123`, `07700900123`) and `serialno`/`serial` followed by a value (for example `serialno ABC123XYZ`, `ro.serialno=...`). Test each on values, evidence excerpts **and** error messages.
4. **60-second total-scan cap** (`stargate/scan.py` around line 398): add a test with a fake clock (no real sleeping) that proves the scan stops at 60 s and the remaining facts become `unknown` with `timeout`.
5. **1 MiB decompressed config cap** (`scan.py` around line 337): add a test with a small compressed input that decompresses past 1 MiB and becomes `unknown` with `output_too_large`, without decompressing the whole thing into memory. In `docs/probes.md`, say in one or two sentences how this cap and the 64 KiB per-command cap interact.
6. **"No process started" tests** (`tests/test_probe.py` around line 129, `tests/test_scan.py` around line 188): the current tests mock `subprocess`, which the code never uses, so they prove nothing. Replace them with tests that patch every process-starting function (`subprocess.Popen`, `subprocess.run`, `os.system`, `os.exec*`, `os.spawn*`, `os.posix_spawn*`) to raise, then run the refusal path and `stargate scan` without `--sim`, and assert exit 3 and that nothing was called.
7. **Error redaction test** (`test_probe.py` around line 113): `test_values_evidence_errors_redacted` never checks errors. Make it produce an error message containing a serial-like value and a phone-like value, and assert both are redacted.
8. **Conflicting evidence** (`test_scan.py` around line 165): add a direct test that a `conflicting` fact keeps both candidates, each with its own evidence, through the scan and in the `--json` output.
9. **Probe sources** (`docs/probes.md` around line 39): five probes cite only conventional names. For each, cite official Android documentation or AOSP source (a link to the exact file). If you can't find one, say so for that probe and mark the source `unknown`. Don't invent a link.
10. **Live doctor evidence:** run `.venv/bin/stargate doctor; echo "doctor exit $?"` **once**. Save the output (it must not contain the key) to `docs/m1-live-check.md`, with the date, the commit it was run from, and the exit code.
11. **Housekeeping (optional items):** add a line `M1: no installs` to `INSTALL-LOG.md`. In the commit message or `docs/`, note that the optional refactor of `doctor.py` was skipped (or done).

## Finish
Run each of these and include the outputs in the report:
```
.venv/bin/python -m unittest; echo "tests exit $?"
for p in budget flagship old32 locked; do .venv/bin/stargate scan --sim $p --json > /tmp/$p.json && .venv/bin/python -m stargate.profile validate /tmp/$p.json; echo "$p validate exit $?"; done
.venv/bin/stargate scan; echo "bare scan exit $? (expect 3)"
if [ -n "${MODEL_API_KEY:-}" ]; then grep -rlF --exclude-dir=.venv --exclude-dir=.git -e "$MODEL_API_KEY" . ; echo "key-scan exit $? (1 = clean, 0 = FOUND, 2 = error)"; else echo "key-scan SKIPPED: key unset"; fi
```
Then make **one** commit (message starting `M1 fixup:`), don't push, and run `git rev-parse HEAD && git status --short`.

## Report
- The full new commit SHA and a clean `git status`.
- For each of fixes 1 to 11: done, or not done and why, with file and line.
- The test count, and every exit code above.
- The doctor result (ok or not, model, attempts).
- Every command run outside the sandbox.
