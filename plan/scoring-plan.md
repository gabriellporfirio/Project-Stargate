# How StarGate scores: the plan against the judging rubric

Status: v1 draft, 30 Oct 2026. Source: the hackathon rules' section 8 (Judging Process) and section 9 (Prizes), pasted by the owner. Track: **Indie Developer**. Goal: **top 5 at minimum** (5th place is $25k, 1st is $150k).

## How judging works
1. **Stage One (pass/fail):** the project fits the theme and visibly uses the Meta Model API and/or Meta's open-weight models.
2. **Stage Two (0–10 each):** Impact 30%, Use of Meta AI tooling 25%, Demo 25%, Technical depth and execution 20%.
3. **Stage Three:** the top 5 per track get ranked by final judges **watching the demo videos live**, using the same rubric.

So to place at all, we need to be top 5 in Stage Two. To place high, **the video has to win the room**. A working product that looks dull on video loses to a slicker one.

## What each criterion needs from StarGate

### Impact (30%)
- **The story:** billions of old phones sit in drawers. StarGate turns one into a private home server (files, a personal AI assistant, a password vault) without the user needing to know what a bootloader is. That means less e-waste, more privacy, and no subscription.
- **Who benefits:** non-technical people who want their own cloud, plus homelab hobbyists who are tired of hand-flashing.
- **Must do:** tie this explicitly to one of the hackathon's **problem statements** (Q12: we don't have that list yet). Say it in the first 15 seconds of the video, in the README and in the write-up.

### Use of Meta AI tooling (25%): go well beyond one chat call
The live model list for this key (M0) shows more than a text model. Every item below is **unverified until a live test**, and each one gets a small spike before we commit to it:

| Idea | Meta tool | Why it impresses | Where it fits | Status |
|---|---|---|---|---|
| Research agent with tools and citations | `muse-spark-1.3` (tool calling, reasoning) | It reasons live on screen about this exact phone and cites sources. Code rejects anything it invents | M2 (already planned) | Planned; tool-calling support to confirm in M2 |
| **A Meta model running on the reclaimed phone** | Meta open-weight Llama, small quantised build | The cloud Meta model plans the phone, and a Meta model then lives on it. That's the strongest "two kinds of Meta AI" story | Assistant module, M4 | Planned; which model fits is decided by the M3 fit engine |
| Talk to your phone server | `muse-voice-transcribe-1.0` | Voice commands in the app ("add a share for photos") look great on video | M6 app, small add-on | Idea; needs a live test |
| Identify the phone from a photo | `sam-3.1` and/or a vision-capable model | Point a camera at a mystery phone and StarGate knows what it is before you plug it in | M6, optional | Idea; whether any listed model accepts images is unknown |
| Plain-English risk explainer | `muse-spark-1.3` | It turns signing and bootloader facts into one honest sentence for a normal person | M3 (already planned) | Planned |
| Built with Muse | Muse Code CLI | The whole product was written by Meta's agent, from a reviewed plan. Say it in the write-up and show the repo history | Submission | True by construction |

Rule: deterministic code still decides what is safe. That's part of the craft story, not a limit.

### Technical depth and execution (20%)
Our edge: every phone fact has a source and a status, AI claims are checked before use, there's an install log, and the tests are real. To make it visible:
- a short "how it works" diagram in the README and the video (probe → research → strategy → build → boot)
- an `ARCHITECTURE.md` with the safety rules, and a test count badge
- no rough edges in the demo path. Crashes on camera cost more than missing features.

### Demo (25%) and the final-round video
- **Biggest single lever: a real phone booting StarGate OS.** An emulator works, but a physical phone lighting up with the StarGate home screen is the "genuinely cool" moment. Your production phone stays off-limits, so this means a **cheap used test phone** (Q5), ideally one with a well-supported unlockable bootloader. It would need to arrive by Mon 2 Nov to be useful. That's your decision.
- **Video plan** (target 2–3 minutes, to confirm against the rules):
  1. 0:00–0:15: the problem (a drawer of old phones) and the hook
  2. 0:15–0:45: plug in, scan, and the live research agent citing sources
  3. 0:45–1:30: choose services, the fit engine blocking an impossible choice, then build
  4. 1:30–2:15: boot. The StarGate home screen appears, then Files works and the on-phone Llama Assistant answers (and voice, if built)
  5. 2:15–2:45: how it works, all Meta-powered, built by Muse
- Record short clips at the end of every milestone (M2 onward) so the video isn't made from scratch on Wednesday.
- The live demo must survive judges poking at it: a scripted "golden path" plus a pre-recorded fallback.

## Changes this implies (proposed, for your approval)
1. **Q12 (new):** paste the theme and the problem statements from the rules, so we pick one and say it everywhere.
2. **Q13 (new):** paste the submission requirements (video length, format, what has to be public). This replaces the open part of Q1.
3. **Q5 becomes urgent:** decide on a cheap test phone by Sat 31 Oct if we want a real-device moment in the video.
4. **M2 adds** a 30-minute spike that tests tool calling, `muse-voice-transcribe-1.0` and whether any model accepts images. The results decide the voice and photo rows above.
5. **M6 adds** voice commands, if the spike passes. Photo identification is optional and goes last.
6. **Wed 4 Nov is video day:** script, record and edit. That's already in the schedule, and stays protected.
