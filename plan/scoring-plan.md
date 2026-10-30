# How StarGate scores: the plan against the judging rubric

Status: v2, 30 Oct 2026. Folds in [ChatGPT's review](../reviews/2026-10-30-chatgpt-scoring-plan.md).
Source: [owner-supplied rules excerpt](../docs/hackathon-rules-excerpt.md) (sections 8 and 9, partial). The official rules URL, the theme and problem statements (Q12), and the submission requirements (Q13) are **not yet attached**, so everything below about judging is "per the owner's excerpt". Track: Indie Developer (owner's statement). Owner's goal: top 5 at minimum.

## How judging works (per the excerpt)
1. **Stage One (pass/fail):** the project fits the theme and used the Meta Model API and/or Meta's open-weight models.
2. **Stage Two (0–10 each):** Impact 30%, Use of Meta AI tooling 25%, Demo 25%, Technical depth and execution 20%.
3. **Stage Three:** the top 5 per track are ranked by final judges watching the demo videos live, using the same rubric.

So the video carries a lot of weight in the final round. But it's scored on the same rubric, so it has to **show the substance**, not just look polished.

## Scope stays as agreed
- The submission uses **simulated phone profiles and the Android Emulator**. Real-device work stays in M7, after the hackathon (owner, 30 Oct: hold off hardware until the platform is done). There's no phone purchase and no physical boot in this plan. Any change to that goes through master plan section 7, with commands, recovery, install approvals and a schedule.
- Q8 (can the image be repacked in the codespace) and Q11 (where the emulator runs) must be settled before any extras.

## What each criterion needs

### Impact (30%)
- **The pitch, kept to what we can support:** old phones often sit unused. StarGate helps someone turn one into a small home server (file sharing and a local AI assistant) without needing to know Android internals. Any number we use (for example how many unused phones exist) needs a cited source, or it's left out.
- **Who benefits:** people who want their own files and a private assistant at home, and hobbyists who are tired of hand-flashing.
- **Careful wording:** the research step uses a cloud Meta model, so we don't claim "fully private" or "free". The services on the phone run locally. Vault and Home are future modules, not part of the current product story.
- **Prerequisite:** Q12. We pick one problem statement and use it in the opening of the video, the README and the write-up.

### Use of Meta AI tooling (25%): depth over feature count
| Keep | Meta tool | What it shows | Milestone |
|---|---|---|---|
| Research agent with tool calls and citations | `muse-spark-1.3` | It reasons live about one specific phone and cites sources. Deterministic code checks what it can (links resolve, repos exist, values are typed) and marks the rest unverified | M2 |
| Plain-English risk explanations | `muse-spark-1.3` | It turns bootloader and signing facts into honest sentences, with the facts themselves coming from the profile, not the model | M3 |
| A small Meta open-weight model as the phone's Assistant | Meta Llama (small, quantised) | The cloud Meta model plans the phone, and a Meta model then runs on it. It's only included if the measured RAM, CPU architecture and runtime fit allow it | M4 |
| The product was written by Muse | Muse Code CLI | Shown through the repo history and the write-up | Submission |

**Cut until the core demo is recorded:** voice commands (`muse-voice-transcribe-1.0`) and photo identification (`sam-3.1` or vision). One successful API call wouldn't prove a reliable feature. The M2 spike is limited to the tool-calling path the research agent needs.

### Technical depth and execution (20%)
Show the checks that are **actually enforced**: every fact has a status and evidence, research claims are validated before use, commands outside the allowlist are refused, the install log exists, and the image contents are checked against the selection. A short architecture diagram goes in the README and the video. A test count on its own isn't presented as proof of quality.

### Demo (25%): the video must prove the core outcome
Target length and format depend on Q13.
1. **Problem and pitch** (the chosen problem statement).
2. **Scan** of a **simulated** phone, labelled as simulated on screen, with unknowns visible.
3. **Research:** the agent's live steps, its citations, and something it rejected.
4. **Plan and fit:** a ranked strategy with risks, and an impossible selection refused with a reason.
5. **Two builds:** Files only, and Files + Assistant. Both artifacts are shown, they differ, and their contents match each selection. Sped-up build time is labelled.
6. **Boot both in the emulator** (labelled as the emulator): different home screens, a file transfer through Files, and a local model answering in Assistant.
7. **How it works**, and what's not done yet (the real-phone path is planned and not built).
Any pre-recorded fallback is labelled as one.

Record short clips at the end of every milestone from M2 onward.

## Evidence table (filled in as milestones finish)
| Criterion | Feature | Result that proves it | Video timestamp |
|---|---|---|---|
| Impact | Problem-statement fit (Q12) | | |
| Meta tooling | Research agent with citations | | |
| Meta tooling | Local Meta model on the device | | |
| Technical depth | Validated facts and claims | | |
| Demo | Two selection-dependent images booted | | |

## Open prerequisites
- **Q12:** the theme and problem statements (from the rules).
- **Q13:** the official rules URL and the submission requirements: video length and access, required deliverables, repo visibility, attribution and licensing, and the deadline timezone.
