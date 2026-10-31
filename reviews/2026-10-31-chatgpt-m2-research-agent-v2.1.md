# ChatGPT re-review: M2 research agent v2.1

Reviewed PR #24 at `321ea848cc7e5c2fb8f61267db31eb6f867e2e77` on 31 October 2026. **Verdict: approve at specification level. No remaining blocking findings.**

The repository-matching blocker is resolved. Established device/tree/kernel relationships require an authoritative structured link and a separate existence check, with `linked_by` preserving the evidence. Shared kernels are explicitly supported; name/search matches stay in `repos.candidates` and cannot supply established relationships to M3. Both regression cases are required tests.

The follow-up notes are also addressed: input limits and checks before requests; retries included in the run allowance; reduced completion caps when the budget is nearly exhausted; honest handling of shared GitHub limits; consistent statuses and fact IDs; valid negative findings; model explanations labelled unchecked; replay equality allowing only its provenance change; and revision-specific HF metadata with missing fields left unknown.

The previously accepted boundaries remain intact: complete offline replay, code-owned facts, restricted fetching, one live demo run producing all outputs, optional development-only Baseten, no real-phone work or installs, and PR #23's approval policy.

- **Must fix:** none identified in this revision.
- **Should fix:** none required for merging the spec. Confirming live source URLs, field meanings and model capabilities remains the explicitly planned spike, not a claim already proven by this review.
- **Optional:** refresh the PR description; it still describes the old `verified` claim scheme and `--offline` option, whereas v2.1 uses typed facts and `--replay`.

**Top three implementation checks:** prove the two repository-association cases → enforce budgets before sending requests → reproduce the recorded report with all networking blocked.

Ready for the owner's merge. The Muse prompt should pin the reviewed M1 checkpoint and preserve the approved public-device selection and bounded spike.

This approves the plan, not a working implementation. No product tests, inference calls, installs or device probes were run.
