# M1: reviewer Muse report and proposed fixup

31 Oct 2026 · v3, which folds in [ChatGPT's review](2026-10-31-chatgpt-m1-fixup-prompt.md) and [its re-review](2026-10-31-chatgpt-m1-fixup-prompt-v2.md). Written before the builder Muse makes any change.
Commit reviewed: `6baa6bcc639c9b9c781549a9692c8fef355665fb` (one commit on `1673b97…`, in the codespace only, not pushed). Evidence level: **Muse-reported** (the reviewer Muse read and ran the code; neither Claude nor ChatGPT has seen it).

Note: the reviewer worked in the builder's folder instead of a separate worktree, because the `<SHA>` placeholder in its prompt was left unfilled. It only read and ran commands.

## Reviewer verdict (summary)
- The reviewer marked done-when items 1–6 and 8 as passing and item 7 (live doctor) as partial. **Our status (v3):** the gaps below undercut several of those passes, so items 1, 2, 3, 5, 6 and 7 are **not yet proven** until the fixup evidence supports them. Item 4 is split: the bare scan exiting 3 stands as Muse-reported, but "no process is started" is **pending** until the replacement test passes, because the current test was ineffective. Item 8 (install log, one commit, not pushed) stand as Muse-reported, with item 8's "no installs" line still to be written. Everything stays labelled Muse-reported.
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

## Changes in v3 (from ChatGPT's re-review)
1. **Baseten key is optional.** The Meta key is required. The Baseten key is scanned only when it's configured, and otherwise recorded as "not applicable".
2. **Doctor evidence now gates the commit.** The gates are three scripts. A runs the offline checks. B runs the single doctor call only after A passes, refuses to run a second time, checks that all code is staged and nothing is untracked, and records a hash of the tested code. C refuses to pass if the staged code's hash differs from the tested one (excluding the evidence file), so any change after the doctor run blocks the commit. Muse must then stop and report rather than use a second live call.
3. **Item 4 split** as above.

I ran the three scripts in a throwaway Git repo with stub commands and dummy keys. The normal path passed. Running B twice failed, a code change after B made C fail, a planted dummy key made C fail, Baseten unset was recorded as not applicable, and the committed diff's hash matched the tested hash.

## Fixup prompt v3 (for the builder Muse)

You are finishing M1 in this product repo. The reviewer checked commit `6baa6bcc639c9b9c781549a9692c8fef355665fb` and reported nine gaps. Until they're fixed and proven, M1 done-when items 1, 2, 3, 5, 6 and 7, and the "no process started" half of item 4, count as **not yet proven**. Fix the gaps in **one fixup commit** on top of that commit. Keep changes to what each fix needs: no unrelated cleanup, and skip the optional `doctor.py` refactor.

## Start check
Run `git rev-parse HEAD && git status --short`. HEAD must be `6baa6bcc639c9b9c781549a9692c8fef355665fb` with a clean tree. If not, stop and report what you see.

## Rules (unchanged from M1)
- No installs of any kind (pip, apt, npm, curl-to-shell). No `git push`. Never use `--disable-sandbox` or `--yolo`.
- Never print, log or write `MODEL_API_KEY` or `BASETEN_API_KEY`.
- Network: **one** `stargate doctor` run (script B) is the only product call. Reading Android docs or AOSP source online is allowed for fix 9. Nothing else.
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
10. **Live doctor evidence:** covered by the three scripts in the next section. The doctor runs **once only**, after every offline check has passed, against code that is fully staged.
11. **Install log (required):** add the line `M1: no installs` to `INSTALL-LOG.md`. In the commit message, note that the optional `doctor.py` refactor was skipped.

## Gates (all must pass before committing)
Save each block below as a file outside the repo, exactly as written, and run it with `bash <file>`. Each script stops at the first failure and prints `GATE FAILED: <reason>`. **If any gate fails, do not commit.** Fix the cause if it's within these fixes, otherwise stop and report. Evidence is kept in `.git/m1-fixup/`, which survives a codespace restart and is never committed.

**Order:** finish fixes 1–9 and 11, run script A until it passes, run script B **once**, then run script C. If you change any code after script B has run, script C will fail. Don't rerun the doctor: stop and report, because the one allowed live call has been used.

**Script A: offline checks** (`/tmp/m1-gate-a.sh`; run as often as needed, it makes no network calls)
```
set -u
fail() { echo "GATE FAILED: $1"; exit 1; }
( set -o pipefail; .venv/bin/python -m unittest 2>&1 | tee /tmp/m1-tests.out ); rc=$?; [ $rc -eq 0 ] || fail "tests exit $rc"
n=$(grep -Eo '^Ran [0-9]+' /tmp/m1-tests.out | grep -Eo '[0-9]+'); [ "${n:-0}" -gt 0 ] || fail "test count ${n:-0}"; echo "tests ok: $n"
for p in budget flagship old32 locked; do .venv/bin/stargate scan --sim $p --json > /tmp/m1-$p.json || fail "$p scan failed"; .venv/bin/python -m stargate.profile validate /tmp/m1-$p.json || fail "$p validate failed"; echo "$p ok"; done
.venv/bin/stargate scan; rc=$?; [ $rc -eq 3 ] || fail "bare scan exit $rc (expected 3)"; echo "bare scan ok (3)"
echo "OFFLINE GATES PASSED"
```

**Script B: the single doctor run** (`/tmp/m1-gate-b.sh`; run once, right after script A passes)
```
set -u
fail() { echo "GATE FAILED: $1"; exit 1; }
BASE=6baa6bcc639c9b9c781549a9692c8fef355665fb
E=.git/m1-fixup; mkdir -p "$E"
[ -e "$E/doctor.rc" ] && fail "the one allowed doctor run has already been used; stop and report"
[ -n "${MODEL_API_KEY:-}" ] || fail "MODEL_API_KEY unset; the doctor can't run"
[ "$(git rev-parse HEAD)" = "$BASE" ] || fail "HEAD is not the M1 commit"
git add -A
git diff --quiet || fail "working tree differs from staged code"
[ -z "$(git ls-files --others --exclude-standard)" ] || fail "untracked files present"
git diff --cached "$BASE" -- . ':(exclude)docs/m1-live-check.md' | sha256sum | cut -d' ' -f1 > "$E/tested.sha"
date -u +%Y-%m-%dT%H:%M:%SZ > "$E/doctor.time"
.venv/bin/stargate doctor > "$E/doctor.out" 2> "$E/doctor.err"; echo $? > "$E/doctor.rc"
echo "doctor exit $(cat "$E/doctor.rc"); tested code hash $(cat "$E/tested.sha")"
```
Then write `docs/m1-live-check.md` with the time, the base SHA, the tested code hash, the exit status, and the contents of `doctor.out` and `doctor.err` from `.git/m1-fixup/`. Don't change anything else.

**Script C: final checks** (`/tmp/m1-gate-c.sh`; run after writing `docs/m1-live-check.md`)
```
set -u
fail() { echo "GATE FAILED: $1"; exit 1; }
BASE=6baa6bcc639c9b9c781549a9692c8fef355665fb
E=.git/m1-fixup
[ -e "$E/doctor.rc" ] || fail "doctor has not run"
[ "$(cat "$E/doctor.rc")" = "0" ] || fail "doctor exit $(cat "$E/doctor.rc")"
[ "$(git rev-parse HEAD)" = "$BASE" ] || fail "HEAD is not the M1 commit"
git add -A
now=$(git diff --cached "$BASE" -- . ':(exclude)docs/m1-live-check.md' | sha256sum | cut -d' ' -f1)
[ "$now" = "$(cat "$E/tested.sha")" ] || fail "code changed after the doctor run; the saved result no longer applies. Stop and report"
git diff --cached --name-only "$BASE" | grep -qx 'docs/m1-live-check.md' || fail "docs/m1-live-check.md missing"
for k in MODEL_API_KEY BASETEN_API_KEY; do
  v="${!k:-}"
  if [ -z "$v" ]; then [ "$k" = MODEL_API_KEY ] && fail "MODEL_API_KEY unset"; echo "$k scan: not applicable (not configured)"; continue; fi
  grep -rlF --exclude-dir=.venv --exclude-dir=.git -e "$v" . ; rc=$?; [ $rc -eq 1 ] || fail "$k working-tree scan exit $rc (0 = FOUND, 2 = error)"
  git grep --cached -lF -e "$v"; rc=$?; [ $rc -eq 1 ] || fail "$k staged scan exit $rc"
  grep -lF -e "$v" "$E/doctor.out" "$E/doctor.err"; rc=$?; [ $rc -eq 1 ] || fail "$k doctor-output scan exit $rc"
  echo "$k scan clean"
done
echo "ALL GATES PASSED"
```

Only after `ALL GATES PASSED`: make **one** commit (message starting `M1 fixup:`), don't push, then run `git rev-parse HEAD && git status --short`.

## Report
- The full new commit SHA and a clean `git status`.
- The tested code hash from `docs/m1-live-check.md`, and the output of `git diff 6baa6bcc639c9b9c781549a9692c8fef355665fb HEAD -- . ':(exclude)docs/m1-live-check.md' | sha256sum`. They must be equal.
- For each of fixes 1 to 11: done, or not done and why, with file and line.
- The full gate output.
- The probes moved to `unknown` / `deferred` in fix 9, if any.
- The doctor result (ok or not, model, attempts).
- Every command run outside the sandbox.

Everything you report is labelled **Muse-reported**. Nobody else has seen the code.
