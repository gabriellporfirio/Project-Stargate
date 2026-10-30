# StarGate: master plan

Version 2 · 29 Oct 2026 · Status: v1 approved; this version folds in the first ChatGPT review

This is the single source of truth. Muse builds from it, and nothing gets built that isn't in it. Anything we don't know yet is listed as an open question, not assumed.

---

## 1. The vision in one paragraph

StarGate turns an old Android phone into a private home server. You run the StarGate app on your computer and plug in a phone. The app works out exactly what that phone is and what it can do, then researches what's available for it: OS bases, firmware, AI models that fit. It shows you what the phone can become, and you pick services such as Files (NAS), Assistant (local AI), VPN, Vault and Home. StarGate then builds a custom, minimal **StarGate OS** image for that exact phone, checks it, and installs it with your explicit OK. The phone boots to a clean home screen with one app per chosen service. Meta Llama does the research, ranking and explaining. Plain, predictable code decides what is safe and allowed.

## 2. Ground rules

1. **Muse builds and Meta models power the product** (hackathon rule). Claude and ChatGPT plan, review and mock up. They don't write product code.
2. **No phone until the platform is finished.** Everything is built and tested on simulated devices and the Android Emulator. Your only phone is your production VPN server, and it is off-limits until a final, separately approved test (M7 in section 5).
3. **Cloud first, nothing new on the Mac by default.** Development runs in a cloud workspace (GitHub Codespaces for M0–M3). Nothing gets installed on the Mac, not even project-local tools, unless Muse first shows an **INSTALL APPROVAL REQUIRED** block (host, tool and version, source, command, paths, privileges, disk and cost, how to undo) and you approve it. Cloud installs go through one reviewed bootstrap plan per workspace. Every install is logged in `INSTALL-LOG.md`.
4. **No assumptions.** Every fact the platform uses must be measured, cited or marked unknown. That goes for this plan too: see section 4.
5. **Small steps you can see.** Each milestone ends with a demo you can run yourself in under five minutes, and a plain-English report: what was built, what's real, what's simulated, and what's unknown.
6. **Nothing leaves the laptop** (push, publish, cloud builds) without your OK on that specific action.
7. **Core platform first, VPN optional at the end.** The priorities are device checks, Meta-assisted research and planning, supported service choices, and dynamic image building. Your existing StarGate VPN work is already done, so it isn't rebuilt here. It can be integrated at the end if time remains. Its private implementation and production setup stay outside this repo, and no core milestone depends on them.

## 3. What the finished product looks like

**The StarGate app** (on your computer). Steps: Meta AI setup → Connect → Scan → Research → Choose → Plan → Build → Install. Mockup: [design/stargate-platform-mockup.png](../design/stargate-platform-mockup.png).

**StarGate OS** (on the phone). A home screen showing only the chosen apps, each with its own management screen. Mockup: [design/stargate-os-mockup.png](../design/stargate-os-mockup.png).

**Services (modules):**

| Module | What the user gets | Built in which milestone |
|---|---|---|
| Files (NAS) | Shares on internal/SD/USB storage, users, how to connect | M4 (baked into the image) |
| Assistant | On-device chatbot with a model sized to the phone, measured speed | M4 (baked into the image) |
| VPN | Tailscale panel: account, start/stop, exit node, update | Optional, last, only if time remains. You already have working VPN in a separate project, so nothing is rebuilt here |
| Vault | Bitwarden-compatible password server management | After the hackathon |
| Home | Home-automation hub (only where the phone has enough memory) | After the hackathon |

## 4. Known facts and open questions

### Facts that shape the design

- **Replacing the OS needs an unlocked bootloader.** Changing any verified partition breaks its stock signature. So a phone either gets unlocked (and verification disabled, or re-signed with your own key where the phone supports that), or it gets the "on top of Android" fallback.
- **`fastboot boot` only boots a kernel + ramdisk (a boot image), once, without flashing.** It does not replace the system partition. A temporary test this way only works if the test environment is self-contained in that boot image, or if it's just a boot/kernel test. It also needs an unlocked bootloader, and some phones block it. So the test plan in section 6 has to be designed around this, and checked for your specific phone.
- **Full Android source builds need x86-64 Linux, around 400 GB of disk and 64 GB of RAM.** Your Mac can't do that. Lighter build paths, and emulator images, can work on the Mac.
- **Muse's command sandbox failed in our codespace** (30 Oct): `bwrap` couldn't create a user namespace, because the kernel doesn't allow unprivileged ones there. That's observed in this codespace only, not proven for every one. The codespace holds the Meta key, Muse's sign-in and access to this private plan, so losing isolation matters. The bounded exception is in section 7.
- **`muse-spark-1.3` is a reasoning model:** it spends part of its answer budget thinking before it replies. How much it thinks varies from run to run on the same prompt: a 64-token cap always gave an empty answer, and 256 passed once, then failed on a rerun. So every Meta call needs generous headroom (M0 uses 1024: 3 live runs in a row passed, with reasoning using 161–233 tokens), and an empty answer cut off by the cap must show up as `bad-response`, never be treated as success.
- **The Android Emulator runs natively on Apple Silicon Macs (arm64 system images).** It needs hardware virtualization, which GitHub Codespaces doesn't provide. So the emulator stand-in phone (M4) needs either one approved Mac install or a cloud machine that supports virtualization (Q11).

### Open questions (must be answered, not assumed)

| # | Question | Who answers | Needed by |
|---|---|---|---|
| Q1 | ~~Hackathon deadline~~ Answered: submissions due Wed 4 Nov, 9:00 PM. Submission requirements still to confirm | You | Now |
| Q2 | ~~Which Meta model IDs and endpoint the Meta API gives your key~~ Answered in M0 (30 Oct): `POST https://api.meta.ai/v1/chat/completions`, Bearer key. The key lists `muse-spark-1.3`, `muse-spark-1.2`, `muse-spark-1.1`, two `-contributor` variants, `muse-wonder-1.0`, `muse-image-1.0`, `muse-voice-transcribe-1.0` and `sam-3.1`. The product uses `muse-spark-1.3` | Muse, from a live call | M0 |
| Q3 | Which model you have on Baseten, and what we'd use it for | You + Muse | M2 |
| Q4 | Your production phone: model, Android version, bootloader unlocked? | You | M7 planning |
| Q5 | Would you buy a cheap used test phone (a supported model) instead of risking the production one? | You | Before M7 |
| Q6 | A Linux build machine for full Android builds: cloud VM, home server, or skip? | You | M5 |
| Q7 | Which emulator image and Android version Muse uses as the stand-in phone | Muse, documented | M4 |
| Q8 | Can an emulator system image be unpacked, extended with StarGate OS and repacked in the Linux codespace (no virtualization needed for that step)? | Muse, by trying it in M4 and documenting the result | M4 |
| Q9 | ~~How Muse CLI signs in on a headless Linux cloud workspace~~ Answered in M0 (30 Oct): the normal Meta account login works inside the codespace, with no API key needed for Muse | Muse docs + M0 | M0 |
| Q10 | ~~Is `Project-StarGate-Meta-Hackathon` private~~ Answered: it's **public**, and its seed (README + devcontainer) is already pushed. Still open: when do we first push product code? Anything pushed is public | You | M0 |
| Q11 | Where the emulator runs for M4: one approved Mac install, or a paid cloud VM with virtualization | You (decision card in the project thread) | Before M4 |
| Q12 | The hackathon theme and its problem statements: which one StarGate answers | You (from the rules) | Before the video script |
| Q13 | The official rules URL, plus the submission requirements: video length and access, deliverables, repo visibility, attribution and licensing, deadline timezone | You (from the rules) | Before the video script |

## 5. The path: milestones

Each milestone needs no phone, ends with a demo you run yourself, and is reviewed by Claude and ChatGPT before the next one starts.

### M0: Clean slate + cloud workspace (half a day)
On the Mac: the old Muse folders go to the Trash (reversible), and you get a read-only install inventory, with no installs. In the cloud: an approved Codespaces proposal, one reviewed bootstrap, a fresh repo, and `stargate doctor` making a real Meta inference call. Full spec: [milestones/M0-clean-reset.md](milestones/M0-clean-reset.md).
**Demo:** `stargate doctor` in the codespace shows `Meta inference: ok`, and the Mac has nothing new installed.

### M1: Device profiles and checks (simulated phones)
A device profile format (every fact has a value, source, and status of measured/inferred/unknown/conflicting). A read-only probe that would collect it over USB, with the command allowlist, tested only against recorded and synthetic outputs. Four contrasting simulated profiles: budget, flagship, old 32-bit, and locked bootloader. Full spec: [milestones/M1-device-profiles.md](milestones/M1-device-profiles.md).
**Demo:** `stargate scan --sim budget` prints a readable phone report with unknowns shown.

### M2: Research agent (Meta Llama)
Given a phone's identity (model or codename, no phone needed), the agent searches allowlisted sources: community OS builds and device trees, stock firmware, Treble reports, and AI models that fit. It returns a cited report. Code checks each link and repo actually exists. Rejected or unverified claims are shown.
**Demo:** `stargate research "<a real model name>"` shows live search steps and a cited report.

### M3: Strategy and fit engines
It ranks how to build the OS for that phone: community tree build / generic system image / stock firmware rebuild / Linux / on-top-of-Android fallback, with reasons, risks and signing implications. The fit engine checks memory, storage, kernel features and AI model size. Over-budget selections are blocked.
**Demo:** two simulated phones give different ranked plans, and an impossible selection is refused with a reason.

### M4: A StarGate OS image, built and booted in the emulator
This is where the image gets built. The builder takes a selection (e.g. Files + Assistant) and produces an emulator system image with the launcher and those modules baked in. It checks the image: format, size fit, and contents matching the selection exactly. Building happens in the cloud workspace. Booting happens in the Android Emulator on whichever host Q11 picks.
If Q8 shows the image can't be repacked in the codespace, the fallback is a stock emulator image with StarGate OS installed on top. The plan labels that a **configuration bundle, not an image**, and moves image repacking to the Linux build machine (Q6).
**Demo:** build once with Files + Assistant and once with Files only. Boot each, and see a different home screen. Files serves a share, and Assistant answers with a small model.

### M5: Real-phone image plan
For a real phone (from the M2 research and M3 ranking), the builder produces the full, specific build plan: base source or firmware, kernel and features, partition sizes, signing steps, the module list, and the validation checks it will run. It runs that build only on a Linux build machine, and only if Q6 says yes. Without one, the plan is the deliverable, marked "not built".
**Demo:** `stargate build-plan --sim flagship --services files,assistant` prints a readable, cited plan, and two different phones give two different plans.

### M6: The StarGate app
The full guided app from the mockup, wired to M1–M5. You can click through end to end on simulated phones, and Build produces the real emulator image from M4. Install shows exact steps but doesn't run them.
**Demo:** a full click-through in the browser, ending with the image booting in the emulator.

### M7: Real-device test (only with explicit approval)
A written test plan for a specific phone covering: exact commands, what changes, how to recover, what could go wrong. On the production phone, only a non-flashing `fastboot boot` test, and only if Q4 confirms it's possible. Strongly preferred: a cheap test phone (Q5).
**Demo:** the phone shows the StarGate home screen, or we get a precise report of why it couldn't.

### Schedule (deadline Wed 4 Nov, 9:00 PM)

| Day | Milestone |
|---|---|
| Thu 29 Oct (tonight) | Plan reviewed by ChatGPT, approved by you |
| Fri 30 Oct | M0 clean reset + M1 device profiles |
| Sat 31 Oct | M2 research agent |
| Sun 1 Nov | M3 strategy + fit engines |
| Mon 2 Nov | M4 StarGate OS image built and booted in the emulator |
| Tue 3 Nov | M6 app + M5 real-phone image plan (last day for organiser troubleshooting) |
| Wed 4 Nov (until 9 PM) | Demo video, submission write-up, buffer. No new features |

M7 (real phone) comes after the hackathon. The VPN module is optional and last, only if everything above is done.

### Hackathon cut line
If time is short, M5 shrinks to a plan for one simulated phone, but **M4 stays**: a real, selection-driven image booting in the emulator is the core of the demo. Together with M1–M3 and the M6 app, that shows the full chain: phone checks → supported choices → Meta-powered research and planning → a dynamically built image.

### Scoring
How every milestone and the demo video map to the judging rubric (owner-supplied excerpt, [docs/hackathon-rules-excerpt.md](../docs/hackathon-rules-excerpt.md)): [scoring-plan.md](scoring-plan.md). Goal: top 5 in the Indie Developer track at minimum. The demo stays on simulated phones and the emulator. Voice and photo extras are cut until the core demo is recorded.

## 6. Review workflow

For every milestone:
1. **Plan:** Claude writes the milestone spec (inputs, outputs, done-when) from this plan.
2. **Cross-review:** ChatGPT reviews the spec using the reviewer prompt in [review-workflow.md](review-workflow.md). Claude reconciles the two and lists any disagreements for you.
3. **You approve.**
4. **Build:** you send Muse the one prompt for that milestone.
5. **Verify:** you run the demo. You paste Muse's final report into this thread, and Claude and ChatGPT each review it against the done-when list.
6. **Fix or move on.**

## 7. Changes to this plan

Only by your decision, recorded here with the date and reason.

| Date | Change | Reason |
|---|---|---|
| 29 Oct 2026 | Plan v1 approved (PR #15) | Clean-slate restart |
| 29 Oct 2026 | Image building moved into the hackathon scope: M4 now builds and boots a real image in the emulator, and M5 produces real-phone build plans | ChatGPT review: the draft postponed image building, against the agreed priority order (checks → choices → built images) |
| 29 Oct 2026 | VPN module removed from M6 and made optional and last | You already have working VPN in a separate project, so there's no need to rebuild it here |
| 29 Oct 2026 | Clean slate and cloud first: the old Muse folders go to the Trash, development moves to Codespaces, and Mac installs need explicit approval | Your direction, recorded by ChatGPT on PR #18 |
| 30 Oct 2026 | M0 Part A done: the old folders are in the Trash and nothing was installed. Part B now starts the codespace from the product repo (README + devcontainer) | Codespaces secrets only reach codespaces linked to a repo |
| 30 Oct 2026 | M0 Part B **Muse-reported complete** (owner check pending): `stargate doctor` got real answers from `muse-spark-1.3` (3 consecutive runs at a 1024-token cap), 39 offline tests pass, and the only logged download is setuptools 84.2.1. Q2 and Q9 answered. `muse-spark-1.3` is the product's default Meta model | Live results from the codespace, reviewed in [reviews/2026-10-30-claude-m0-part-b-report.md](../reviews/2026-10-30-claude-m0-part-b-report.md) |
| 30 Oct 2026 | **Sandbox exception:** Muse's sandbox fails in our codespace, so its commands ran outside it during M0 (an undocumented path, with the automatic judge on). From M1 on, Muse runs with `--approval-mode untrusted --approval-judge off`. That makes shell commands stop for you, but not file edits inside the workspace, so it is **not** a guarantee that every action prompts. Before M1, you record `muse --version` and confirm with a harmless test command that a prompt really appears. If it doesn't, M1 stops. Network use is bounded per milestone | The owner approved bounded unsandboxed runs during M0. Details and limits are in [the M0 report review](../reviews/2026-10-30-claude-m0-part-b-report.md) |
| 30 Oct 2026 | **Muse approval setting changed to the fast mode:** from M1 on, Muse runs with `--approval-mode on-request --approval-judge on`. This replaces the `untrusted` + judge-off setting in the row above. Because the sandbox fails in the codespace, the automatic judge decides most outside-sandbox runs, so **you don't approve every command**. Safety checks are written into each milestone prompt instead: no installs unless listed, never push, never use `--disable-sandbox` or `--yolo`, bounded network use, a guarded key-leak scan before every commit, and a report of every command that ran outside the sandbox. The approval test is no longer required | Your decision (30 Oct, decision card): strict mode slowed Muse down too much for the deadline. Accepted risk: the codespace holds the Meta key, Muse's sign-in and read access to this plan, and the judge can approve commands without you |
