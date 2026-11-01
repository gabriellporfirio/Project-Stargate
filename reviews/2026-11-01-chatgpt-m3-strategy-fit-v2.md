# ChatGPT re-review: M3 strategy and fit engines, v2

Reviewed PR #28 at `0992d771a5ab6f47321e15c2e05d7812ff1ba0a3` on 1 November 2026. **Verdict: request one remaining correction to the M4 handoff.**

The strategy eligibility changes, ordered unlock states, per-model treatment of unknowns, resource budgets, input validation, exit-code precedence and bounded documentation reads address the earlier findings. The revised test requirements cover the examples raised in the first review.

1. **Must fix — preserve the decision at the builder boundary (§6, lines 115–116).** `selection_result`, subject and provenance are outside `handoff`, yet the spec says “M4 reads only this block.” The block contains unresolved checks, but not known failures. A Files-only plan with enough storage and one refused for insufficient storage can therefore have identical handoffs: the same services, no Assistant model, the same candidate strategies and the same unknown image-size check. M4 cannot distinguish them from the allowed input.

   The smallest fix is to require M4 to validate the complete `plan-v1` envelope and check its decision/provenance before consuming the build payload. Alternatively, make the handoff self-contained with those fields and refusal reasons. Specify that a refused plan never starts a build, and an unconfirmed plan remains limited to planning or a labelled emulator experiment. Add a contract test for the accepted/refused Files-only pair and preservation of synthetic/replay provenance. No new feature or extra live run is needed.

2. **Should fix — correct the milestone reference (§3b, line 68).** The master plan puts the working Files and Assistant modules in **M4**; M5 is the real-phone image plan. Resolve the app/runtime minimums when those modules are built in M4, rather than saying they first exist in M5.

3. **Should fix — make Files-only storage explicit (§4a, line 78).** Parenthesize Assistant app size plus model bytes under the same “if Assistant is selected” condition. This avoids charging the Assistant app to a Files-only selection. Cover that case in the existing resource-budget tests.

**Priorities:** preserve the refusal at the handoff; align the app milestone; clarify the conditional budget. The approved M4 spike can continue independently. This was a specification review: no product code, installs or live inference calls were run.
