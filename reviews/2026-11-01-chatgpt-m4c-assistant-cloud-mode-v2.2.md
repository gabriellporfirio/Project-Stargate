# ChatGPT re-review: M4c Assistant cloud mode v2.2

Reviewed PR #30 at `48062736d096862f208996a4339c51d137d9bcbc` on 1 November 2026. **Verdict: the same cost-bound finding remains open.**

The UTF-8/body limits, priced-model allowlist, maximum-cost phone allocation and added regression cases address the input and model-switch handling. All previously closed findings remain closed.

**Must fix — reconcile the arithmetic and the guarantee (§6; master plan §7).**

- **Arithmetic:** 16,384 tokens is not two tokens per byte of a 16 KB body. Define the unit explicitly: if the cap is **16 KiB = 16,384 bytes**, twice that is **32,768 tokens**. Update the formula, ledger default, tests and master-plan row consistently.
- **Evidence:** §6 explicitly calls the Muse byte/token relationship an assumption, while the status and master plan call it a “true upper bound.” Multiplying an unverified estimate does not establish a guaranteed ceiling for the complete billable input. [Meta distinguishes model-specific rendered token counts from billing usage](https://dev.meta.ai/docs/token-counting). The new stop rule is useful, but it runs after the potentially over-budget request has already incurred its cost.

There are two clear ways to finish this:

1. **Keep the strict dollar guarantee:** require a cited, provider-enforced upper limit covering the billable request before enabling that model. Reserve against that limit and the output cap. If no supported bound fits the allowance, that provider stays blocked under the existing partial/blocked outcome.
2. **Keep the heuristic for this bounded demo:** describe it consistently as a conservative estimate, retain the byte limits, five-attempt cap and stop rule, and state that an individual request can exceed the reservation before the stop takes effect. Record that estimated-budget policy explicitly in master plan §7 for the owner's merge. This is a change from the current promise of never exceeding the dollar allowance.

Please choose one of these contracts; another arbitrary multiplier alone will not resolve the mismatch. The correction can remain limited to the budget wording/formula and its tests. No other merge blockers found.

Specification review only. I checked the arithmetic; no installs, product tests, builds, emulator commands or live inference calls were performed.
