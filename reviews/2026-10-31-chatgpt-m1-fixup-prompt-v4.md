# ChatGPT approval: M1 fixup prompt v4

Reviewed PR #25 at `16c37dcc2ddb0e46cf4f0e6b7974b35c7b11b5ad` on 31 October 2026. **Verdict: approve the fixup prompt. No remaining blocking findings.**

The final interruption issue is resolved. Script B checks for either a started marker or a completed result, atomically creates the started marker immediately before launching doctor, and retains it after interruption or failure. The instructions explicitly prohibit deleting the evidence and retrying the live call.

**Validation of the latest scripts:**
- Normal A → B → C flow passed with only a synthetic Meta key; absent Baseten remained correctly not applicable.
- Terminating B during the local stub doctor left the started marker without a result file. Restarting B exited 1 before another invocation; the stub call count remained **one**.

The latest diff changes only this guard and its instructions. Previously verified rejection of changed code, a repeated completed run and a planted dummy key remains unchanged. The corrected evidence labels, real refusal-boundary tests, redaction controls, source fallback and required install-log entry remain in the prompt.

- **Must fix:** none remaining.
- **Should fix:** none required before sending this prompt.
- **Top three execution deliverables:** implement the nine M1 fixes → produce passing offline and single-run doctor evidence for the same code → report the full fixup SHA, clean working tree and gate outputs.

One focused fixup commit remains appropriate. PR #23's approval policy, no installs, no push and no real-device work remain intact. Ready for the owner's merge and the reviewed prompt to be given to Muse.

This approves the instructions, **not M1 completion**. The product results still need review after Muse runs the fixup.

Validation used disposable Git repositories, command stubs and dummy keys, adapting only the fixture base SHA and temporary paths. Fixtures were removed. No unpublished product code, real credentials, real inference calls or installs were involved.
