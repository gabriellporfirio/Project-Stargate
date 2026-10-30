# ChatGPT re-review: M0 Part B results v2

Reviewed PR #20 at `2e1bd210ce20a67a293012d3e758c6c872f81e6d` on 30 October 2026. **Verdict: request changes; two remaining blockers.**

The earlier corrections are substantial: the report now distinguishes evidence sources, limits the observed sandbox failure to this Codespace, acknowledges its credentials, reconciles 1024 tokens and 39 tests, records the full fixup SHA, and separates the public seed from permission to push product code.

1. **Must fix — judge off does not mean every command prompts.** The master-plan §7 exception and report §Points still promise this. The [current Muse permissions documentation](https://dev.meta.ai/docs/muse-code/permissions) says `on-request` allows recognised non-dangerous shell stages without prompting; `--approval-judge off` sends eligible review decisions to the human. It does not change which calls require review. Even `untrusted` permits matching allow rules, and file reads/edits have separate behaviour. Replace the universal guarantee in both files. Before extending the exception to M1, record the installed version and supported outside-sandbox approval path, including whether every such invocation is explicitly escalated for human review. Verify that behaviour and state the exact bounded commands or batch the owner approves. If that cannot be established, keep the documented exception limited to the already approved M0 runs; the owner can execute reviewed commands manually. Do not mark this finding “done” while relying on an unverified guarantee.

2. **Must fix — verification labels must follow actual checks.** The verdict says the work becomes “independently checked” if code is pushed for review. A push only makes code available; an actual review/test and its recorded outcome must follow. Likewise, running the owner checklist does not automatically validate every acceptance row: successful outputs must match the final SHA, and budget/idle settings and install-log evidence remain separate. Update each row only when its own evidence supports the change.

**Should fix:** refuse the key scan when `MODEL_API_KEY` is unset or empty; otherwise an empty literal search matches arbitrary files. Keep the corrected scan explicitly pending until its outcome is recorded. Prefer a scanner that reads the key from the environment internally so it is not placed in process arguments.

**Top three actions:** correct the approval guarantee → make verification status evidence-based → guard the key scan.

Checked current documentation and repository state. Product `main` remains the seed at `59176961f59970e7192dd61a93ddcdba96897fd1`; no M0 implementation, live call or product tests were independently run. Refresh the PR description to match the revised report.
