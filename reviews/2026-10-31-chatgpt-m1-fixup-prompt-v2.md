# ChatGPT re-review: M1 fixup prompt v2

Reviewed PR #25 at `9917c2b08a131289611b2d6e486675166a004859` on 31 October 2026. **Verdict: request changes — two gate defects remain.**

The revision addresses the actual refusal boundary, redaction controls, unsupported probe semantics and most evidence labelling. Passing checks now gate the commit. The nine fixes and one focused fixup commit remain appropriate; PR #23's approval policy stays unchanged.

1. **Must fix — don't require an optional Baseten key (gate line 85 and line 89).** The loop fails whenever either key is unset. My previous review requested scanning both keys **when present**. M1 requires Meta for its doctor check; Baseten is not an M1 dependency. In an isolated run with a synthetic Meta key and no Baseten key, the gate stopped with `GATE FAILED: BASETEN_API_KEY unset, key scan can't run`. Require the Meta key; scan Baseten if configured, otherwise record `not configured / not applicable`. Don't require provisioning a Baseten secret to complete M1.

2. **Must fix — enforce the doctor/code match before committing (fix 10, Gates and Report).** The block checks only the saved doctor exit code. The diff comparison happens after the commit and merely asks for an explanation if it differs. I changed the staged code after the synthetic successful doctor snapshot; the complete gate still exited 0 and printed `ALL GATES PASSED`. This can happen after the prompt's permitted “fix the cause” step following a failed gate. Run the offline checks before the one live doctor call, ensure the working tree matches the staged code at that call, and compare the tested identity with the final candidate **before** allowing a commit, using the same evidence-file exclusion. Any subsequent code change must invalidate that success. If the single live run is already used, stop and report; don't silently rerun or accept stale evidence.

3. **Should fix — split item 4's evidence status.** It requires both exit 3 and no process started. Keep the observed exit code Muse-reported, but mark the process-isolation evidence pending until the replacement test passes; the summary currently leaves the whole item passing despite the reported ineffective test.

**Top three priorities:** optional-key handling → doctor evidence tied to the committed code → precise item-4 status.

**Validation:** exercised the quoted gate block in a disposable Git repository, with temporary paths redirected, synthetic passing CLI/test stubs and dummy keys. Both cases above reproduced; the fixtures were removed. No product code was inspected, no product tests or real inference calls were run, and nothing was installed.
