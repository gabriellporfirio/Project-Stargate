# ChatGPT re-review: M4c Assistant cloud mode v2.1

Reviewed PR #30 at `bceaea17f9bc55802a12be3a75abbc50748012b8` on 1 November 2026. **Verdict: one calculation correction remains.**

The credential findings are resolved: the Keystore-failure test now checks storage, logs and transport; backup proof inspects the packaged rules and the installed app's backup flag. The shared ledger, reservations before dispatch, retained reservations for unknown usage, fixed phone allocations and one-build-per-proof-run rule address the previous accounting gaps. The 429 clarification is also fixed.

**Must fix — make the cost reservation a genuine upper bound (§6, line 86).** “2,000 characters counted as 2,000 input tokens” is not a guaranteed maximum. Tokenization is model-specific, and character count does not establish the billable token count. [Meta documents that identical text can have different token counts across models](https://dev.meta.ai/docs/token-counting), and [billing varies with language and content](https://dev.meta.ai/help/billing/api-bill). Unicode input can invalidate a one-character/one-token assumption. A request can therefore pass the stated reservation check while its actual cost exceeds the reserved amount.

Replace that formula with a justified conservative bound for each permitted model's complete billable input and bounded output. Bind each phone allocation to its permitted model/prices, or reserve for the most expensive permitted choice, since the Meta model ID remains editable. Add an offline test with maximum-length multibyte input and a near-exhausted budget, plus a model change within a phone allocation: an underfunded request must stop before transport.

Keep this correction limited to the reservation formula and its tests. No other merge blockers found in this revision. Approved M4 work can continue.

Specification review only; no installs, product tests, builds, emulator commands or live inference calls were performed.
