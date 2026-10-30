# M0 Part B: review of Muse's report

30 Oct 2026 · Reviewer: Claude · v3, which folds in [ChatGPT's review](2026-10-30-chatgpt-m0-part-b-results.md) and [its re-review](2026-10-30-chatgpt-m0-part-b-results-v2.md).
Plan commit used by Muse: `b498e7037e1e064fd6db8ff73687ecc5a81e449b`.
Product checkpoint: `b214429…` plus fixup `1673b97…`. Full final SHA (from the owner): `1673b97fb97d2612f42fa28c6fe07caa2a937bb3`. Both commits are in the codespace only and not pushed, so neither Claude nor ChatGPT can inspect the code. The product repo's `main` still holds only the two seed files (`59176961…`).

## Evidence labels
- **Muse-reported:** Muse ran it and printed the result. Nobody else has seen the output directly.
- **Owner-observed:** the owner ran it (or watched it run) and saw the output.
- **Independently checked:** Claude or ChatGPT actually inspected the code **and** reran the check successfully. Nothing is in this category yet. Pushing the code only makes it **available** for review. A label moves up only after the matching check has passed.

Settings (spending limit, idle timeout) and install evidence are tracked separately from the check results.

## Done-when list

| Item | Status | Evidence |
|---|---|---|
| B1 approved; codespace exists with a $0 spending limit and a 30-minute idle timeout | Codespace exists (owner-observed). Limit and timeout: **pending owner confirmation** | Owner's GitHub settings |
| `INSTALL-LOG.md` lists every codespace install and nothing else | Muse-reported | One download, setuptools 84.2.1 from PyPI, into pip's isolated build environment. Muse identified it from pip's cache. **Limit:** the cache shows what pip fetched in this session, not a full history of the machine, and the devcontainer image's own contents are taken as given |
| `stargate doctor` exits 0 with `Meta inference: ok`, the endpoint and the model | Muse-reported, at the fixup commit | At 256 tokens a later rerun failed with `bad-response` (cut off by the cap, no answer). At 1024 tokens there were 3 consecutive `ok` runs: `POST https://api.meta.ai/v1/chat/completions`, `muse-spark-1.3` requested and returned, 1 attempt each, 20 s timeout, 1 retry, reasoning 161–233 tokens. This supports **this check**, not reliability for every Meta call |
| Exits non-zero with `missing-credential` when the variable is unset | Muse-reported | Exit 2, 0 attempts, no request sent |
| `python -m unittest -v` passes with a count above zero | Muse-reported, at the fixup commit | 39 offline tests pass. The earlier 36 was before the fixup |
| Checkpoint commit in the codespace, nothing pushed | Muse-reported | `b214429` plus fixup `1673b97fb97d2612f42fa28c6fe07caa2a937bb3`, clean tree. |

**Verdict:** M0 Part B is **Muse-reported complete**. Each row moves to "owner-observed" when the owner runs the matching line of the check below and sees it pass. A row only becomes "independently checked" once the code is pushed (Q10) **and** a reviewer has inspected it and rerun that check successfully.

**Tracked separately:** the $0 spending limit and the 30-minute idle timeout (owner confirmation pending), and install evidence (Muse-reported, with the limits noted in the table).

## Points

1. **Must fix (done in this PR): the sandbox exception.**
   - **What happened:** every command Muse tried inside its sandbox failed with `bwrap: No permissions to create a new namespace … kernel does not allow non-privileged user namespaces`. That was observed in this codespace on 30 Oct. It's not proven for every codespace, and the Muse version in the codespace wasn't recorded (unknown).
   - **Settings in force:** `muse --approval-mode on-request --approval-judge on`. **Note:** with the judge on, Muse's automatic judge can approve some requests by itself, so "the owner approved every command" is **not** established.
   - **What the owner approved (30 Oct, in the project thread):** read-only checks could retry outside the sandbox. Anything that writes, installs or touches the network beyond the Meta call needed the owner's explicit OK, and the M0 batch (steps 0–8) was approved as a whole.
   - **What's at stake:** the codespace holds the `MODEL_API_KEY` secret, Muse's sign-in, and GitHub access to the private plan repo. Being disposable doesn't make up for losing command isolation.
   - **What Muse's [permissions docs](https://dev.meta.ai/docs/muse-code/permissions) say (read 30 Oct):** `--approval-mode on-request` (the default) only stops for dangerous or external-execution patterns, and safe commands pass silently. `--approval-mode untrusted` stops for **every shell command without a matching allow rule**. `--approval-judge off` sends every review decision to the person instead of the automatic judge. File reads, and file writes inside the workspace, never prompt in any mode. The docs say Muse **refuses** shell commands when it can't confirm the sandbox, and they don't describe the per-command "retry outside the sandbox" path Muse actually used here. So that path is **undocumented**, and how it behaves with the judge off is unverified.
   - **For M1 onwards (proposal):** run `muse --approval-mode untrusted --approval-judge off`, with no allow rules added. Even so, "every command prompts" isn't guaranteed: file edits inside the workspace don't prompt, and the outside-sandbox path is undocumented. So **before M1 work starts**, the owner records `muse --version` and does one harmless test: ask Muse to run `echo approval-test` and confirm that a prompt appears and the command waits for them. If no prompt appears, M1 stops and the exception is reconsidered (for example a different environment). Each milestone's network use stays bounded in its spec. M0's spec and prompt keep their original wording as historical records. The exception is logged in the master plan's section 7.
2. **Should fix: the product's model choice is a decision.** `muse-spark-1.3` was picked from the live model list. It's a reasoning model, and its thinking varies run to run, so token caps need headroom (now 1024). Recorded in section 7. Model discovery shows which IDs were **listed**, not that each one works for every task.
3. **Should fix: rerun the key-leak scan correctly.** The scan I gave in the approval message put `--` in the wrong place, so `--exclude-dir` was read as paths. That can produce errors, and "found nothing" can't be told apart from an error. The corrected scan is in the owner check below. grep's exit code 1 means no matches, 0 means a match was found, and 2 means an error.
4. **Optional: doctor code size.** `doctor.py` is about 475 lines. Splitting out the Meta client and redaction is optional in M1.

## Still open
- **Q10:** answered in part. The product repo is **public** and its seed is already pushed. Pushing the M0 code needs a separate OK from the owner, and anything pushed is visible to everyone.
- **Q11:** the emulator host for M4.
- **Q3:** Baseten isn't configured, which is expected.

## Owner check (codespace terminal, product repo)
Each line prints its exit code, so a failure can't hide.
```
.venv/bin/stargate doctor; echo "doctor exit $?"
env -u MODEL_API_KEY .venv/bin/stargate doctor; echo "no-key exit $? (expect 2)"
.venv/bin/python -m unittest; echo "tests exit $?"
if [ -n "${MODEL_API_KEY:-}" ]; then grep -rlF --exclude-dir=.venv --exclude-dir=.git -e "$MODEL_API_KEY" . ; echo "key-scan exit $? (1 = no matches, 0 = FOUND, 2 = error)"; else echo "key-scan SKIPPED: MODEL_API_KEY is unset or empty"; fi
git rev-parse HEAD && git status --short; echo "status exit $?"
```
