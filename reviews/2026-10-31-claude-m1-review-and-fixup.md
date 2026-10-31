# M1: reviewer Muse report and proposed fixup

31 Oct 2026 · v2, which folds in [ChatGPT's review](2026-10-31-chatgpt-m1-fixup-prompt.md) (three must-fix, two should-fix). Written before the builder Muse makes any change.
Commit reviewed: `6baa6bcc639c9b9c781549a9692c8fef355665fb` (one commit on `1673b97…`, in the codespace only, not pushed). Evidence level: **Muse-reported** (the reviewer Muse read and ran the code; neither Claude nor ChatGPT has seen it).

Note: the reviewer worked in the builder's folder instead of a separate worktree, because the `<SHA>` placeholder in its prompt was left unfilled. It only read and ran commands.

## Reviewer verdict (summary)
- The reviewer marked done-when items 1–6 and 8 as passing and item 7 (live doctor) as partial. **Our status (v2):** the gaps below undercut several of those passes, so items 1, 2, 3, 5, 6 and 7 are **not yet proven** until the fixup evidence supports them. Items 4 (bare scan exits 3) and 8 (install log, one commit, not pushed) stand as Muse-reported, with item 8's "no installs" line still to be written. Everything stays labelled Muse-reported.
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

## Questions for ChatGPT (answered)
1. Are all nine worth fixing before M2, or should any wait?
2. Is anything missing from the fixup prompt below, or does any item go beyond the M1 spec?
3. Is one fixup commit right, or should the builder split it?

ChatGPT's answers: fix all nine before M2, since they're all within the M1 spec; one focused fixup commit; keep the optional refactor skipped.

## Changes in v2 (from ChatGPT's review)
1. **Checks now gate the commit.** A single gate block stops at the first failure: tests exit 0 with a count above zero, all four profiles validate, the bare scan exits 3, the doctor run exited 0, and both keys are absent from the working tree, the staged content and the doctor output. An unset key fails the gate instead of being skipped. Only `ALL GATES PASSED` allows the commit.
2. **Honest status and sources.** The summary above now marks the affected items not yet proven. In fix 9, a probe with no official source isn't kept as a measured fact: its fact becomes `unknown` with reason `deferred`, and the gap is written down.
3. **Tests at the real refusal boundary.** Fix 6 now patches the names where the code actually looks them up (plus the standard library as a backstop), checks that forbidden commands reach the transport zero times, runs the CLI in-process, and includes a test showing the guard catches a call.
4. **Doctor evidence is tied to the tested code.** The doctor runs once, after the fixes are staged, and records the base SHA and a hash of the staged diff together with stdout, stderr and the exit status. The report compares that hash with the committed diff.
5. **Smaller points.** Redaction has negative controls (byte counts stay integers), the "no installs" line is required, and the step references are corrected.

## Fixup prompt v2 (for the builder Muse)

You are finishing M1 in this product repo. The reviewer checked commit `6baa6bcc639c9b9c781549a9692c8fef355665fb` and reported nine gaps. Until they're fixed and proven, M1 done-when items 1, 2, 3, 5, 6 and 7 count as **not yet proven**. Fix the gaps in **one fixup commit** on top of that commit. Keep changes to what each fix needs: no unrelated cleanup, and skip the optional `doctor.py` refactor.

## Start check
Run `git rev-parse HEAD && git status --short`. HEAD must be `6baa6bcc639c9b9c781549a9692c8fef355665fb` with a clean tree. If not, stop and report what you see.

## Rules (unchanged from M1)
- No installs of any kind (pip, apt, npm, curl-to-shell). No `git push`. Never use `--disable-sandbox` or `--yolo`.
- Never print, log or write `MODEL_API_KEY` or `BASETEN_API_KEY`.
- Network: **one** `stargate doctor` run (fix 10) is the only product call. Reading Android docs or AOSP source online is allowed for fix 9. Nothing else.
- Keep a list of every command you ran outside the sandbox, and include it in the report.

## Fixes
1. **Evidence command allowlist** (`stargate/profile.py` around line 178): the validator rejects any `evidence.command` that isn't exactly on the probe allowlist. Add an invalid schema example and a test.
2. **Inference rule IDs** (`profile.py` around line 300): the validator rejects an `inference.rule_id` that isn't listed in `docs/inference-rules.md` (or the code's single source of those IDs). Add an invalid example and a test.
3. **Redaction** (`stargate/probe.py` around lines 76 and 131), one shared change:
   - Catch phone-number-like values (for example `+44 7700 900123`, `07700900123`) and `serial`/`serialno` followed by a value (for example `serialno ABC123XYZ`, `ro.serialno=...`).
   - Test each on values, evidence excerpts **and** error messages.
   - **Negative controls:** a test proves that legitimate numbers are untouched. For example, `resources.ram_total` and `resources.data_free` byte counts stay typed integers, and `/proc/meminfo` lines aren't redacted.
4. **60-second total-scan cap** (`stargate/scan.py` around line 398): a test with a fake clock (no real sleeping) proves the scan stops at 60 s and the remaining facts become `unknown` with `timeout`.
5. **1 MiB decompressed config cap** (`scan.py` around line 337): a test with a small compressed input that decompresses past 1 MiB proves it becomes `unknown` with `output_too_large`, without decompressing everything into memory. In `docs/probes.md`, explain in one or two sentences how this cap and the 64 KiB per-command cap interact.
6. **Refusal boundary** (replaces the tests at `tests/test_probe.py` around line 129 and `tests/test_scan.py` around line 188, which mock `subprocess` even though the code never uses it):
   - First, list how each module in `stargate/` imports anything that can start a process (for example `import subprocess` vs `from subprocess import run`, `os`, `asyncio`, `pty`). Python mocks must patch the name **where the code looks it up**, not only the standard library. Patch those actual lookup sites, plus the standard-library functions as a backstop. Each patch raises instead of running.
   - **Transport test:** for every forbidden command and every metacharacter case, use a recording fake transport and assert it received **zero** calls (refused before the transport).
   - **No-process test:** run the CLI entry point **in-process** (not as a child process) for `stargate scan` without `--sim`, assert exit 3 and the "not enabled" message, and assert no patched function was called.
   - **Guard self-test:** a test that deliberately calls one of the patched functions and shows the guard catches it, so we know the guards work and nothing launches.
7. **Error redaction test** (`test_probe.py` around line 113): `test_values_evidence_errors_redacted` must produce an error message containing a serial-like value and a phone-like value, and assert both are redacted.
8. **Conflicting evidence** (`test_scan.py` around line 165): a direct test that a `conflicting` fact keeps both candidates, each with its own evidence, through the scan and in the `--json` output.
9. **Probe sources** (`docs/probes.md` around line 39): five probes cite only conventional names. For each, find official Android documentation or AOSP source and link the exact file. **If no official source is found, don't invent one.** Say so in `docs/probes.md`, and make the fact that probe feeds `unknown` with reason `deferred` in every fixture and in the code, instead of `measured`. List which probes this affected in the report.
10. **Live doctor evidence:** do this **after** fixes 1–9 and 11 are done and `.venv/bin/python -m unittest` passes, and **once only**:
    - Run `git add -A`, then record the base SHA (`git rev-parse HEAD`) and the tested diff identity (`git diff --cached | sha256sum`).
    - Run `.venv/bin/stargate doctor > /tmp/doctor.out 2> /tmp/doctor.err; echo $? > /tmp/doctor.rc`.
    - Write `docs/m1-live-check.md` with the date (UTC), the base SHA, the diff hash, the exit status, and stdout and stderr from that same run. Don't rerun just to capture output.
11. **Install log (required):** add the line `M1: no installs` to `INSTALL-LOG.md`. In the commit message, note that the optional `doctor.py` refactor was skipped.

## Gates (all must pass before committing)
Run this block exactly as written. It stops at the first failure and prints which gate failed. **If any gate fails, do not commit.** Fix the cause if it's within these fixes, otherwise stop and report.

```
set -u
fail() { echo "GATE FAILED: $1"; exit 1; }
( set -o pipefail; .venv/bin/python -m unittest 2>&1 | tee /tmp/tests.out ); rc=$?; [ $rc -eq 0 ] || fail "tests exit $rc"
n=$(grep -Eo '^Ran [0-9]+' /tmp/tests.out | grep -Eo '[0-9]+'); [ "${n:-0}" -gt 0 ] || fail "test count ${n:-0}"; echo "tests ok: $n"
for p in budget flagship old32 locked; do .venv/bin/stargate scan --sim $p --json > /tmp/$p.json || fail "$p scan exit $?"; .venv/bin/python -m stargate.profile validate /tmp/$p.json || fail "$p validate exit $?"; echo "$p ok"; done
.venv/bin/stargate scan; rc=$?; [ $rc -eq 3 ] || fail "bare scan exit $rc (expected 3)"; echo "bare scan ok (3)"
[ "$(cat /tmp/doctor.rc)" = "0" ] || fail "doctor exit $(cat /tmp/doctor.rc)"; echo "doctor ok"
git add -A
for k in MODEL_API_KEY BASETEN_API_KEY; do v="${!k:-}"; [ -n "$v" ] || fail "$k unset, key scan can't run"; grep -rlF --exclude-dir=.venv --exclude-dir=.git -e "$v" . ; rc=$?; [ $rc -eq 1 ] || fail "$k working-tree scan exit $rc (0 = FOUND, 2 = error)"; git grep --cached -lF -e "$v"; rc=$?; [ $rc -eq 1 ] || fail "$k staged scan exit $rc"; grep -lF -e "$v" /tmp/doctor.out /tmp/doctor.err; rc=$?; [ $rc -eq 1 ] || fail "$k doctor-output scan exit $rc"; echo "$k scan clean"; done
echo "ALL GATES PASSED"
```

If a key is unset in this codespace, the gate fails on purpose: report it rather than skipping the check.

Only after `ALL GATES PASSED`: make **one** commit (message starting `M1 fixup:`), don't push, then run `git rev-parse HEAD && git status --short`.

## Report
- The full new commit SHA and a clean `git status`.
- The base SHA and diff hash from `docs/m1-live-check.md`, and the output of `git diff 6baa6bcc639c9b9c781549a9692c8fef355665fb HEAD -- . ':!docs/m1-live-check.md' | sha256sum`. It should equal the recorded hash, which shows the doctor ran against exactly the committed code. If it doesn't, say what changed after the doctor run.
- For each of fixes 1 to 11: done, or not done and why, with file and line.
- The full gate output.
- The probes moved to `unknown` / `deferred` in fix 9, if any.
- The doctor result (ok or not, model, attempts).
- Every command run outside the sandbox.

Everything you report is labelled **Muse-reported**. Nobody else has seen the code.
