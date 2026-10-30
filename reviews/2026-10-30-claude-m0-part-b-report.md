# M0 Part B: review of Muse's report

30 Oct 2026 · Reviewer: Claude · Plan commit used by Muse: `b498e7037e1e064fd6db8ff73687ecc5a81e449b` · Product checkpoint commit: `b2144293a929518ac9d547523f72bd9c6616729e` (in the codespace, not pushed)

This review checks Muse's final report against the Part B done-when list in [M0-clean-reset.md](../plan/milestones/M0-clean-reset.md). It's based on the report Muse printed in the codespace. Nothing here was rerun by Claude. The owner's own 5-minute check (below) is what confirms it.

## Done-when list

| Item | Result | Evidence |
|---|---|---|
| B1 approved; codespace exists with a $0 spending limit and a 30-minute idle timeout | Codespace exists. Limit and timeout: **to confirm by the owner** | Owner's account settings |
| `INSTALL-LOG.md` lists every codespace install and nothing else | Proven | Only download: setuptools 84.2.1 from PyPI into pip's isolated build environment, identified from pip's cache. No system packages |
| `stargate doctor` exits 0 with `Meta inference: ok`, the endpoint and the model | Proven after a fix: at 256 tokens it failed on the owner's rerun. At 1024, 3 consecutive live runs were `ok` (reasoning used 161–233 tokens). Fixup commit `1673b97` | `POST https://api.meta.ai/v1/chat/completions`, model requested and returned `muse-spark-1.3`, 1 attempt, 20 s timeout, 1 retry, `max_completion_tokens` 256 |
| Exits non-zero with `missing-credential` when the variable is unset | Proven | Exit 2, 0 attempts, no request sent |
| `python -m unittest -v` passes with a count above zero | Proven | 39 offline tests pass (after the fixup) |
| Checkpoint commit in the codespace, nothing pushed | Proven | `b214429` plus fixup `1673b97`, clean tree |

## Points

1. **Should fix: the spec's "keep the sandbox on" can't be met in Codespaces.** Muse's sandbox needs unprivileged user namespaces, which Codespaces turns off. Every command ran outside the sandbox, each with the owner's approval. The plan now records this as a known fact. Later milestone prompts should say "approvals on; sandbox where available" rather than requiring it.
2. **Should fix: the product's model choice is a decision.** `muse-spark-1.3` was chosen from the live model list as Meta's recommended Spark model. It is a reasoning model, so token caps must leave room for its thinking. 64 gave an empty answer. 256 passed once, but the owner's rerun returned `bad-response` (cut off by the cap with no answer), so the doctor wasn't reliably green. Fixed: the cap is now 1024, the doctor reports token usage, and 3 consecutive live runs passed. Tests went from 36 to 39. Recorded in plan section 7.
3. **Optional: doctor code size.** `stargate/doctor.py` is about 420 lines for four checks. That's acceptable for M0. The M1 prompt should ask Muse to put shared parts (the Meta client, redaction) in their own modules, not grow doctor further.
4. **Optional: the key-leak check command in the approval message was malformed** (the `--` was placed before `--exclude-dir`). It searched more files than intended, including `.venv` and `.git`, and found nothing, so the result still holds.

## Still open

- Q10: is the product repo private, and when does the first push happen? The commit exists only in the codespace until it's pushed.
- Q11: the emulator host for M4.
- Q3: Baseten is not configured, which is expected.

## Owner's 5-minute check (codespace terminal, product repo)

```
.venv/bin/stargate doctor
env -u MODEL_API_KEY .venv/bin/stargate doctor; echo "exit $?"
.venv/bin/python -m unittest 2>&1 | tail -3
git log --oneline -1 && git status --short
```
