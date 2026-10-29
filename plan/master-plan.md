# StarGate: master plan

Version 1 · 29 Oct 2026 · Status: draft for review by you, Claude and ChatGPT

This is the single source of truth. Muse builds from it, and nothing gets built that isn't in it. Anything we don't know yet is listed as an open question, not assumed.

---

## 1. The vision in one paragraph

StarGate turns an old Android phone into a private home server. You run the StarGate app on your computer and plug in a phone. The app works out exactly what that phone is and what it can do, then researches what's available for it: OS bases, firmware, AI models that fit. It shows you what the phone can become, and you pick services such as Files (NAS), Assistant (local AI), VPN, Vault and Home. StarGate then builds a custom, minimal **StarGate OS** image for that exact phone, checks it, and installs it with your explicit OK. The phone boots to a clean home screen with one app per chosen service. Meta Llama does the research, ranking and explaining. Plain, predictable code decides what is safe and allowed.

## 2. Ground rules

1. **Muse builds and Meta models power the product** (hackathon rule). Claude and ChatGPT plan, review and mock up. They don't write product code.
2. **No phone until the platform is finished.** Everything is built and tested on simulated devices and the Android Emulator. Your only phone is your production VPN server, and it is off-limits until a final, separately approved test (section 6).
3. **No hidden installs.** Everything Muse installs goes inside the project folder: one `.venv`, one `tools/` folder. Anything installed system-wide (Homebrew, adb, Docker) must be asked for first and logged in `INSTALL-LOG.md`, with the command and how to undo it.
4. **No assumptions.** Every fact the platform uses must be measured, cited or marked unknown. That goes for this plan too: see section 4.
5. **Small steps you can see.** Each milestone ends with a demo you can run yourself in under five minutes, and a plain-English report: what was built, what's real, what's simulated, and what's unknown.
6. **Nothing leaves the laptop** (push, publish, cloud builds) without your OK on that specific action.

## 3. What the finished product looks like

**The StarGate app** (on your computer). Steps: Meta AI setup → Connect → Scan → Research → Choose → Plan → Build → Install. Mockup: [design/stargate-platform-mockup.png](../design/stargate-platform-mockup.png).

**StarGate OS** (on the phone). A home screen showing only the chosen apps, each with its own management screen. Mockup: [design/stargate-os-mockup.png](../design/stargate-os-mockup.png).

**Services (modules):**

| Module | What the user gets | Built in which milestone |
|---|---|---|
| Files (NAS) | Shares on internal/SD/USB storage, users, how to connect | M4 |
| Assistant | On-device chatbot with a model sized to the phone, measured speed | M4 |
| VPN | Tailscale panel: account, start/stop, exit node, update | M6 |
| Vault | Bitwarden-compatible password server management | Later |
| Home | Home-automation hub (only where the phone has enough memory) | Later |

## 4. Known facts and open questions

### Facts that shape the design

- **Replacing the OS needs an unlocked bootloader.** Changing any verified partition breaks its stock signature. So a phone either gets unlocked (and verification disabled, or re-signed with your own key where the phone supports that), or it gets the "on top of Android" fallback.
- **`fastboot boot` only boots a kernel + ramdisk (a boot image), once, without flashing.** It does not replace the system partition. A temporary test this way only works if the test environment is self-contained in that boot image, or if it's just a boot/kernel test. It also needs an unlocked bootloader, and some phones block it. So the test plan in section 6 has to be designed around this, and checked for your specific phone.
- **Full Android source builds need x86-64 Linux, around 400 GB of disk and 64 GB of RAM.** Your Mac can't do that. Lighter build paths, and emulator images, can work on the Mac.
- **The Android Emulator runs on Apple Silicon Macs (arm64 system images).** That's our stand-in phone for StarGate OS until a real one is allowed.

### Open questions (must be answered, not assumed)

| # | Question | Who answers | Needed by |
|---|---|---|---|
| Q1 | ~~Hackathon deadline~~ Answered: submissions due Wed 4 Nov, 9:00 PM. Submission requirements still to confirm | You | Now |
| Q2 | Which Meta model IDs and endpoint the Meta API gives your key | Muse, from a live call | M0 |
| Q3 | Which model you have on Baseten, and what we'd use it for | You + Muse | M2 |
| Q4 | Your production phone: model, Android version, bootloader unlocked? | You | M7 planning |
| Q5 | Would you buy a cheap used test phone (a supported model) instead of risking the production one? | You | Before M7 |
| Q6 | A Linux build machine for full Android builds: cloud VM, home server, or skip? | You | M5 |
| Q7 | Which emulator image and Android version Muse uses as the stand-in phone | Muse, documented | M4 |

## 5. The path: milestones

Each milestone needs no phone, ends with a demo you run yourself, and is reviewed by Claude and ChatGPT before the next one starts.

### M0: Clean reset (half a day)
Archive v1 and v2 folders (don't delete them). Create a fresh `stargate` repo. One `.venv`, `INSTALL-LOG.md`, `AGENTS.md` pointing to this plan, and `stargate doctor` making real test calls to Meta (and Baseten if used).
**Demo:** `stargate doctor` shows green or red for each check. `INSTALL-LOG.md` lists every install.

### M1: Device profiles and checks (simulated phones)
A device profile format (every fact has a value, source, and status of measured/inferred/unknown/conflicting). A read-only probe that would collect it over USB, with the command allowlist, tested only against recorded and synthetic outputs. Four contrasting simulated profiles: budget, flagship, old 32-bit, and locked bootloader.
**Demo:** `stargate scan --sim budget` prints a readable phone report with unknowns shown.

### M2: Research agent (Meta Llama)
Given a phone's identity (model or codename, no phone needed), the agent searches allowlisted sources: community OS builds and device trees, stock firmware, Treble reports, and AI models that fit. It returns a cited report. Code checks each link and repo actually exists. Rejected or unverified claims are shown.
**Demo:** `stargate research "<a real model name>"` shows live search steps and a cited report.

### M3: Strategy and fit engines
It ranks how to build the OS for that phone: community tree build / generic system image / stock firmware rebuild / Linux / on-top-of-Android fallback, with reasons, risks and signing implications. The fit engine checks memory, storage, kernel features and AI model size. Over-budget selections are blocked.
**Demo:** two simulated phones give different ranked plans, and an impossible selection is refused with a reason.

### M4: StarGate OS on the emulator
The launcher and the Files and Assistant modules running inside the Android Emulator on your Mac. The home screen shows only the chosen apps, Files serves a share, and Assistant runs a small model.
**Demo:** an emulator window with the StarGate home screen. You open Files and Assistant, and both work.

### M5: Image builder
It builds a StarGate OS image for the emulator target, with the chosen modules baked in, and checks it: format, size fit, contents match the selection exactly. It also generates the build plan for one real device from M2/M3 research, and runs it on a Linux machine only if Q6 says yes.
**Demo:** build with 2 modules and with 3 modules, boot each in the emulator, and see a different home screen each time.

### M6: The StarGate app
The full guided app from the mockup, wired to M1–M5. You can click through end to end on simulated phones and the emulator. Install shows exact steps but doesn't run them. VPN module panel added.
**Demo:** a full click-through in the browser.

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
| Mon 2 Nov | M4 StarGate OS on the emulator |
| Tue 3 Nov | M6 app on simulated phones (last day for organiser troubleshooting) |
| Wed 4 Nov (until 9 PM) | Demo video, submission write-up, buffer. No new features |

M5 and M7 come after the hackathon unless we're ahead of schedule.

### Hackathon cut line
If time is short, the demo is **M0–M4 plus the M6 app on simulated phones**. That already shows Meta-powered research and planning and a real StarGate OS running in the emulator. M5 and M7 come after.

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
