# ChatGPT re-review: M2 research agent v2

Reviewed PR #24 at `7d2db899783f05abf534384d8e21ece6715ff51e` on 31 October 2026. **Verdict: request changes — one remaining blocker.**

V2 resolves the full-replay gap, separates model prose from facts, defines fetch restrictions and run limits, and makes the demo and acceptance criteria concrete. Baseten remains optional and development-only. PR #23's approval policy remains accepted.

1. **Must fix — repository matching still does not establish the device relationship (§3b, line 63).** A name/description containing a codename can belong to an unrelated repository; existence plus that substring does not establish a device tree, kernel or vendor source. It also rejects valid shared kernels: [LineageOS's enchilada data](https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/enchilada.yml) explicitly names `android_kernel_oneplus_sdm845`, whose [repository](https://github.com/LineageOS/android_kernel_oneplus_sdm845) has no `enchilada` in its name and has a null description. Derive typed device/repository relationships from explicit authoritative links such as the YAML's `tree` and `kernel.repo`, then confirm existence. Keep unbound search results as candidates, ineligible as established relationships for M3. Missing a substring means unknown association, not proven mismatch. Test both a valid shared kernel and an unrelated repository mentioning the codename.

2. **Should fix — finish budget accounting (§0/§2).** Completion limits do not bound the source text and accumulated history sent as input. Add a numeric input/context cap and enforce remaining call/token/time allowances *before* each request, including retries; lower the final completion cap to the remaining allowance. The per-run GitHub cap also cannot guarantee staying within an hourly allowance shared by an IP; keep the header-based handling and remove that guarantee. [GitHub documents the IP-wide limit](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

3. **Should fix — make validation rules consistent (§2/§3/§6).** Replace the leftover `unverified` outcome with the defined fetch outcome and `unknown` fact status. Explicitly give facts IDs. A source saying “unsupported” may correctly yield a `found` negative fact; the test should forbid a positive support conclusion, not every fact. Missing fact IDs can be checked deterministically, but arbitrary prose contradictions cannot be guaranteed detectable: constrain checked assertions or label remaining prose unchecked. Replay comparison must allow its intentional provenance change.

4. **Optional — use the spike to settle HF details.** Record the revision-specific request and explicit file-size metadata query; [HF documents that file sizes require requesting metadata](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api#huggingface_hub.HfApi.model_info). Missing size/licence/base-model fields stay unknown.

**Top three priorities:** explicit repository/device relationships → input and remaining-budget limits → consistent report/test semantics.

Specification and primary-source review only; no product tests, paid inference, installs or device probes were run.
