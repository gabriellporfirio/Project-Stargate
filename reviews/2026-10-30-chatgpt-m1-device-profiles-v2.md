# ChatGPT follow-up: M1 specification v2

Reviewed PR #21 at `81a57a07f6eb21a6840a88bd749e0dbb6fa8f363` on 30 October 2026. **Verdict: approve the M1 specification.** This supersedes the initial request for changes on the specification.

The three blocking findings are resolved: the format now declares typed facts, byte units and conflicting candidates; lock state, unlock support and unlock permission are separate; and partition capacity and runtime usability remain unknown rather than being inferred from unrelated facts. The numeric probe limits, expanded fixtures, complete JSON checks and direct unittest command address the other main findings. The optional refactor keeps M1 focused.

**Should fix before the Muse handoff:**

1. Clarify §5’s network wording: scans and automated tests stay offline, and the only product API activity is the bounded doctor regression run. Muse still needs read-only access to the approved plan and official Android sources to satisfy the required probe verification. Distinguish that documentation access from product network calls.

2. Obtain the accepted full M0 checkpoint SHA through PR #20’s reconciliation and pin it in the handoff. This approval does not establish that M0’s unpublished implementation, live results or sandbox exception have been verified.

3. In §1a, attach the “different values” requirement to `candidates`: evidence items in §1b have no `value` field. Each candidate needs its own evidence. Require at least two distinct typed candidate values; the top-level evidence list can aggregate those sources.

**Optional:** make the four-profile demo loop stop on the first failure so a later successful profile cannot obscure an earlier failed validation.

**Top three handoff checks:** documentation/network scope → accepted M0 pin → candidate/evidence consistency. No product code, tests, network inference or device probes were run.
