# ChatGPT review: M1 findings and fixup prompt

Reviewed PR #25 at `dcc86af2220eaba0f40a6c1dab5587e994b52c9e` on 31 October 2026. **Verdict: request changes to the prompt.** This reviews Claude's summary against the accepted M1 spec; I have not inspected the product code or original reviewer output.

**Answers:** address all nine findings before accepting M1 and starting M2; they concern existing requirements. One fixup commit on the full pinned SHA is appropriate. Combine overlapping redaction work, keep the optional doctor refactor skipped, and avoid unrelated cleanup. PR #23's fast approval policy stays unchanged.

1. **Must fix — make checks gate the commit (Finish).** Printing exit codes and then saying “make one commit” allows failed tests, failed validation, a failed doctor run or a detected key to be committed. Require a positive test count, tests and all four validations exiting 0, bare scan exiting 3, doctor exiting 0, and successful leak checks before committing. Capture each real status before `echo` masks it. Scan both named keys when present; a match or scan error must block the commit, and a skipped required check must not count as clean. Include staged content and newly saved evidence in the check.

2. **Must fix — reconcile the acceptance summary and source fallback.** “Items 1–6 and 8 pass” conflicts with reported validator, redaction, test and citation gaps. Mark affected items incomplete/unproven until the fixup evidence supports them. “Source unknown” is honest but does not fulfil M1's official-source requirement. Unsupported probe semantics must remain unknown/deferred in affected facts, with the gap explicit, rather than being treated as established measurements. Keep the whole result labelled Muse-reported.

3. **Must fix — test the actual refusal boundary (fix 6).** Blanket patches to standard-library names can miss functions imported into another namespace; [Python requires patching where an object is looked up](https://docs.python.org/3/library/unittest.mock.html#where-to-patch). Inspect the actual imports and patch those lookup sites. Invoke the CLI entry point in-process for this test. Also assert that a forbidden command never reaches the transport: no process is weaker than M1's “refused before transport” rule. Demonstrate that the test guards catch an attempted call without launching anything.

4. **Should fix — bind doctor evidence to the tested changes (fix 10).** The run happens before the fixup commit, so HEAD still names the old commit while code is modified. Record the base SHA plus the tested working-tree/diff identity, then map it to the final SHA in the report. Save stdout, stderr and the actual exit status from the same single run; don't rerun merely to capture output.

5. **Should fix — small prompt details.** Add redaction negative controls so legitimate RAM/storage byte counts remain typed numbers. Make the no-install log entry required, as M1 requires it. Correct the network-rule references: doctor is fix 10; probe sources are fix 9.

**Top three priorities:** checks that block commits → honest acceptance/evidence status → tests at the actual refusal boundary.

No product tests, inference calls, installs or device probes were run.
