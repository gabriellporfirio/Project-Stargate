# ChatGPT review: M2 research agent

Reviewed PR #24 at `cd8ad9466c5a8953869174edc16624a67040d74e` on 31 October 2026. **Verdict: request changes.** The agent/pipeline fallback and development-only Baseten boundary are sensible. PR #23's fast approval policy remains accepted.

1. **Must fix — citation matching is not claim verification (§3).** A real excerpt about another variant, or saying “not supported,” can currently validate the opposite claim. Separate citation integrity from claim eligibility. M3 should consume only narrow, typed facts extracted/checked against the exact device and source, not arbitrary model prose. Code must assign status and citation hashes/times from its own fetch records. Test wrong-device evidence, contradictory excerpts and a genuine unrelated quote; none may authorise a compatibility conclusion.

2. **Must fix — define the fetch boundary (§2).** Enumerate exact HTTPS hosts/routes and validate every redirect; reject private/local destinations, URL credentials and non-HTTP schemes. Validate tool arguments and treat page instructions as untrusted data. Keep provider credentials out of research requests and test profile filtering across all tools. Update postmarketOS to [Nura](https://nura.eco/blog/2026/09/27/nura-rename/): the old wiki redirects to `wiki.nura.eco`. My wiki requests encountered access blocks; denied/challenge pages must become unverified, not evidence of unsupported devices.

3. **Must fix — replay the model too (§4).** Recorded tool responses alone cannot reproduce the report without another Meta call. Record model responses/tool decisions as well, or replay a validated final report with its evidence and steps. Test with all outbound networking disabled; preserve recorded/synthetic provenance in JSON as well as the display.

4. **Must fix — bound the whole run (§0/§2).** Set numeric Meta/Baseten call, token and retry limits, and include inference, pagination, redirects and retries in the deadline/request budgets. Cap decoded content. [GitHub](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) allows only 60 unauthenticated requests/hour/IP; [search](https://docs.github.com/en/rest/search/search) has a separate 10/minute limit. Count HTTP requests, honour rate-limit responses, and define cache keys/freshness.

5. **Should fix — finish the output contract.** Specify subject identity, mode/provenance, per-topic coverage, partial/completed state and exit codes. Zero findings must not satisfy “per topic it found.” Parse actual CLI stdout in tests; progress belongs on stderr under `--json`. Reuse one live run for human and JSON evidence so the five-minute demo doesn't require two three-minute runs.

6. **Should fix — narrow source claims and scope.** Prefer [LineageOS's own device data](https://github.com/LineageOS/lineage_wiki/blob/main/_data/devices/enchilada.yml), distinguishing current support from historical versions/build availability. [HF metadata](https://huggingface.co/docs/hub/model-cards) describes publisher assertions: record exact revision/files, byte sizes, base model and licence; it doesn't prove runtime fit. Mark uncovered stock-firmware/Treble topics explicitly unknown. Keep the undecided Baseten audit optional for core M2; the spike should not deploy infrastructure or download weights.

**Top three priorities:** trustworthy M3 inputs → bounded fetch/model execution → fully offline, reproducible reports.

Primary-source/document review only; no product tests, Meta/Baseten inference or device probes were run.
