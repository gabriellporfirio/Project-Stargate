# ChatGPT review: M0 clean reset

29 Oct 2026 · [PR #18](https://github.com/gabriellporfirio/Project-Stargate/pull/18) at `af3988697867dd94b2bb00eebafe4ef5a6607470` · against merged plan v2 at `b051f3acd232fa94930d7a72c783442d5b62e67a`.

**Verdict: changes needed before the Muse prompt.** Scope is appropriate. This reviews the specification; no laptop audit, archive move or live API test was performed.

## The four decisions

| Decision | Review |
|---|---|
| 1. Product repository | **Should fix:** keep it. GitHub currently lists no branches; recheck at execution. Explicitly initialise `main`; refuse an occupied destination rather than overwriting it. |
| 2. Archive by moving | **Must fix:** keep the approach, but verify resolved source paths/repository identities, record source-to-destination mappings, refuse collisions, and verify files plus Git history, dirty and untracked work survive. Preserve archive contents; moved virtual environments are not reliably runnable ([Python documentation](https://docs.python.org/3/library/venv.html#how-venvs-work)). |
| 3. Python 3.9.6 | **Must fix:** change this baseline. Python 3.9 reached end of life on 31 October 2025 ([support table](https://devguide.python.org/versions/)). Select and record a supported existing interpreter or a project-local runtime under `tools/`; leave Apple's Python untouched. Standard-library runtime code is fine. Specify venv creation, packaging dependencies and the install step that provides `stargate doctor`. |
| 4. Linked plan | **Must fix:** keep it, pinned to an approved merged commit containing both master plan and M0. Verify origin, commit and clean checkout; reuse a valid local clone without overwriting unrelated contents. Printing an arbitrary latest commit is insufficient. |

## Other findings

- **Must fix — inventory accuracy and privacy:** package presence cannot prove Muse installed it. Separate current inventory, changes attributable through available records, and unknown provenance. Record checked locations/commands and limitations; missing history is not “none installed.” Keep the audit read-only and record sanitised metadata, never raw shell profiles, credentials or secret-bearing commands. Do not invent historical install or uninstall commands.
- **Must fix — doctor contract:** define a configured credential source, verified HTTPS endpoint and model. Meta documents `https://api.meta.ai/v1`, bearer authentication and separate model-list/inference endpoints ([API reference](https://dev.meta.ai/docs/api-reference), [authentication](https://dev.meta.ai/docs/authentication)). Require one bounded authenticated inference with a validated response; report endpoint and requested/returned model, distinguishing discovery from inference success. Keep credentials restricted to their provider origin. Define timeouts, token/retry limits, explicit missing/auth/quota/network/error results and a nonzero exit for required failures. A failed request must not satisfy completion. Tests should cover these failures and secret redaction in stdout, stderr and logs, report a nonzero test count, and stay offline; record the live check separately.
- **Should fix — keep M0 small:** skip Baseten unless both credentials and model configuration exist. Drop blanket future-domain HEAD checks and the dummy Keychain test; neither establishes model access. Check only the configured credential source; optional/report-only checks must not block completion.

**Top three changes:** (1) safe archiving and a pinned plan; (2) supported Python with reproducible CLI setup; (3) truthful inventory and explicit doctor acceptance.
