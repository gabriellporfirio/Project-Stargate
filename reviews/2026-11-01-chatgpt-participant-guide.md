# ChatGPT review: participant guide and scoring plan

Reviewed PR #27 at `f79cde5614da252c09942469233479424f4f45d3` on 1 November 2026. **Verdict: request changes before merge.** No earlier review was recorded, and GitHub currently reports `mergeable: false`, `mergeable_state: dirty`.

The deadline conversion is correct: **21:00 EST on Wednesday 4 November = 02:00 GMT on Thursday 5 November** (checked using the New York and London time zones). The theme choices, three-minute video, public repository and hackathon-only demo requirements follow the supplied excerpt. “Build for Your World” is a reasonable recommendation, with the final choice left to the owner.

1. **Must fix — resolve the conflict with main.** Update this branch against current main and preserve its accepted milestone changes alongside the guide updates. A correct rules document still cannot be merged while GitHub reports a conflict.

2. **Must fix — distinguish bonus eligibility from our chosen implementation** (`plan/scoring-plan.md:25`). The [supplied guide](../docs/participant-guide-excerpt.md) allows the named eligible models to run on participants' hardware **or through partner inference**. It does not require a phone's Assistant specifically. Present that as our conditional implementation choice, not an organizer requirement. Preserve the emulator-only hackathon scope and existing development-only Baseten decision; this correction does not authorize changing either. Model fit and actual prize eligibility remain to be established.

3. **Should fix — budget the three-minute video explicitly** (`plan/scoring-plan.md:54–61`). Seven sections at 20–30 seconds can reach 210 seconds. Keep the two builds and working services; shorten the surrounding explanation. Suggested allocation: pitch 15 s, simulated scan 15 s, research 25 s, plan/refusal 20 s, build artifacts 30 s, both emulator boots plus Files/Assistant 50 s, architecture/limits 15 s. That is **170 seconds plus 10 seconds for transitions**. Label condensed footage and keep detailed logs in the repo. No extra feature is needed.

4. **Should fix — update the remaining deadline labels** (`plan/master-plan.md:109,119`). The schedule heading and Wednesday row still say 9 PM without a timezone. Use the same ET/GMT dates as Q1, while keeping Wednesday afternoon as the intended submission target.

**Top three:** resolve the conflict; correct the bonus wording; give the core demo a timed allocation.

This review compares the plan with the repository's owner-supplied guide transcription. The original PDFs and separate Official Rules were not independently verified. Recording those remaining questions is appropriate; it does not require making the private planning repo public now.
