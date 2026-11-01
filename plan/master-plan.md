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
| Q1 | ~~Hackathon deadline~~ Answered: submissions due **Wed 4 Nov, 9:00 PM Eastern Time**, which is **2:00 AM GMT on Thu 5 Nov** ([participant guide](../docs/participant-guide-excerpt.md), 31 Oct). Late submissions aren't considered | You | Now |
| Q2 | ~~Which Meta model IDs and endpoint the Meta API gives your key~~ Answered in M0 (30 Oct): `POST https://api.meta.ai/v1/chat/completions`, Bearer key. The key lists `muse-spark-1.3`, `muse-spark-1.2`, `muse-spark-1.1`, two `-contributor` variants, `muse-wonder-1.0`, `muse-image-1.0`, `muse-voice-transcribe-1.0` and `sam-3.1`. The product uses `muse-spark-1.3` | Muse, from a live call | M0 |
| Q3 | Partly answered (30 Oct): the hackathon Baseten key works only with `meta-models/muse-spark-open-1026`. Development-only use (product principle, 30 Oct) is **superseded on 1 Nov**: Baseten is now an optional, user-supplied partner provider for the Assistant's open-weight mode only ([M4c](milestones/M4c-assistant-cloud-mode.md)). Endpoint, features and billing are checked in the M2 spike | You + Muse | M2 |
| Q4 | Your production phone: model, Android version, bootloader unlocked? | You | M7 planning |
| Q5 | Would you buy a cheap used test phone (a supported model) instead of risking the production one? | You | Before M7 |
| Q6 | A Linux build machine for full Android builds: cloud VM, home server, or skip? | You | M5 |
| Q7 | ~~Which emulator image and Android version Muse uses as the stand-in phone~~ Answered (1 Nov): the stock Android 14 (API 34) arm64 AOSP image, `system-images;android-34;default;arm64-v8a`, booted on your Mac (M4 spike) | Muse, documented | M4 |
| Q8 | ~~Can an emulator system image be unpacked, extended with StarGate OS and repacked in the Linux codespace (no virtualization needed for that step)?~~ Answered (1 Nov): yes. The spike's repacked image booted on your Mac and its marker file read back from the running system (Path A) | Muse, by trying it in M4 and documenting the result | M4 |
| Q9 | ~~How Muse CLI signs in on a headless Linux cloud workspace~~ Answered in M0 (30 Oct): the normal Meta account login works inside the codespace, with no API key needed for Muse | Muse docs + M0 | M0 |
| Q10 | ~~Is `Project-StarGate-Meta-Hackathon` private~~ Answered: it's **public**, and its seed (README + devcontainer) is already pushed. Still open: when do we first push product code? Anything pushed is public | You | M0 |
| Q11 | ~~Where the emulator runs for M4~~ Answered (31 Oct): on your Mac (MacBook Pro, Apple M5, 16 GB RAM, owner-stated), with arm64 emulator images. Needs one approved install; the exact block comes from the [M4 spike](milestones/M4-spike.md) | You | Before M4 |
| Q12 | ~~The theme and problem statements~~ Answered (31 Oct, [participant guide](../docs/participant-guide-excerpt.md)): two problem statements, **Build for Your World** and **Push the Frontier**, plus a list of anti-projects, none of which StarGate resembles. Which one StarGate answers is your call (the [scoring plan](scoring-plan.md) recommends Build for Your World) | You | Before the video script |
| Q13 | Mostly answered (31 Oct, [participant guide](../docs/participant-guide-excerpt.md)): a **three-minute demo video**, a **public repository**, everyone listed on the submission page, and the demo may show only work built during the hackathon. Still open: the Official Rules document itself (licensing and attribution terms), and whether this private planning repo must also be public | You | Before submission |
| Q14 | Does `muse-spark-1.3` support tool calling and structured JSON output on the Meta API? This decides agent mode or pipeline mode for research | Muse, from the M2 spike | M2 |
| Q15 | Partly answered (1 Nov): **Muse Glimmer** has 30B parameters, Apache 2.0 licence, "runs on a single GPU" ([Hugging Face](https://huggingface.co/meta-models/Muse-Glimmer-30B), owner-supplied from Meta's developer page). Its [model card](https://huggingface.co/meta-models/Muse-Glimmer-30B) lists 24–32 GB deployment targets, outside the approved demo budget (6 GB emulator on a 16 GB Mac), so it can't be the phone's Assistant. Muse Spark Open's size and formats are still unknown | Muse, from official docs | M4 |
| Q16 | ~~Can a normal Meta API key call Muse Spark Open?~~ Answered (1 Nov): no. [Meta's model catalog](https://dev.meta.ai/docs/models) says Muse Spark Open isn't served through the Meta Model API (cited in ChatGPT's M4c review). The open-weight mode uses an optional Baseten key ([M4c](milestones/M4c-assistant-cloud-mode.md) section 2) | You, from Meta's developer docs | M4c |

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
Full spec: [milestones/M2-research-agent.md](milestones/M2-research-agent.md).
**Demo:** `stargate research "<a real model name>"` shows live search steps and a cited report.

### M3: Strategy and fit engines
Full spec: [milestones/M3-strategy-fit.md](milestones/M3-strategy-fit.md).
It ranks how to build the OS for that phone: community tree build / generic system image / stock firmware rebuild / Linux / on-top-of-Android fallback, with reasons, risks and signing implications. The fit engine checks memory, storage, kernel features and AI model size. Over-budget selections are blocked.
**Demo:** two simulated phones give different ranked plans, and an impossible selection is refused with a reason.

### M4: A StarGate OS image, built and booted in the emulator
Full spec: [milestones/M4-image-build.md](milestones/M4-image-build.md). A bounded [spike](milestones/M4-spike.md) runs first, alongside M2, to answer Q7, Q8 and the toolchain question before the full M4 spec is written.
This is where the image gets built. The builder takes a selection (e.g. Files + Assistant) and produces an emulator system image with the launcher and those modules baked in. It checks the image: format, size fit, and contents matching the selection exactly. Building happens in the cloud workspace. Booting happens in the Android Emulator on whichever host Q11 picks.
If Q8 shows the image can't be repacked in the codespace, the fallback is a stock emulator image with StarGate OS installed on top. The plan labels that a **configuration bundle, not an image**, and moves image repacking to the Linux build machine (Q6).
**Demo:** build once with Files + Assistant and once with Files only. Boot each, and see a different home screen. Files serves a share, and Assistant answers with a small model.

### M5: Real-phone image plan
For a real phone (from the M2 research and M3 ranking), the builder produces the full, specific build plan: base source or firmware, kernel and features, partition sizes, signing steps, the module list, and the validation checks it will run. It runs that build only on a Linux build machine, and only if Q6 says yes. Without one, the plan is the deliverable, marked "not built".
**Demo:** `stargate build-plan --sim flagship --services files,assistant` prints a readable, cited plan, and two different phones give two different plans.

### M4c: Assistant cloud mode
Full spec: [milestones/M4c-assistant-cloud-mode.md](milestones/M4c-assistant-cloud-mode.md). After M4's local Assistant works, the Assistant also offers Meta cloud (`muse-spark-1.3`) and open-weight cloud (Muse Spark Open) modes. A local-only build keeps no network permission.

### M6: The StarGate app
The full guided app from the mockup, wired to M1–M5. You can click through end to end on simulated phones, and Build produces the real emulator image from M4. Install shows exact steps but doesn't run them.
**Demo:** a full click-through in the browser, ending with the image booting in the emulator.

### M7: Real-device test (only with explicit approval)
A written test plan for a specific phone covering: exact commands, what changes, how to recover, what could go wrong. On the production phone, only a non-flashing `fastboot boot` test, and only if Q4 confirms it's possible. Strongly preferred: a cheap test phone (Q5).
**Demo:** the phone shows the StarGate home screen, or we get a precise report of why it couldn't.

### Schedule (deadline Wed 4 Nov, 9:00 PM ET = Thu 5 Nov, 2:00 AM GMT)

| Day | Milestone |
|---|---|
| Thu 29 Oct (tonight) | Plan reviewed by ChatGPT, approved by you |
| Fri 30 Oct | M0 clean reset + M1 device profiles |
| Sat 31 Oct | M2 research agent |
| Sun 1 Nov | M3 strategy + fit engines |
| Mon 2 Nov | M4 StarGate OS image built and booted in the emulator |
| Tue 3 Nov | M6 app + M5 real-phone image plan (last day for organiser troubleshooting) |
| Wed 4 Nov (aim to submit in the afternoon; hard deadline 9:00 PM ET = 2:00 AM GMT Thu 5 Nov) | Demo video, submission write-up, buffer. No new features |

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
| 30 Oct 2026 | **Product principle:** StarGate is free to use, and the only key a user needs is their own **Meta API key**. Baseten (`muse-spark-open-1026`) is used only during development, never in the product people run | Your direction: it benefits both Meta and the user, with one key for an intelligent platform that builds their whole system |
| 31 Oct 2026 | **M4 spike runs alongside M2**, in a separate worktree, to answer Q7, Q8 and the toolchain question by Sun 1 Nov | M4 is the core of the demo and the riskiest step. Finding a blocker on Monday would leave no time to change path |
| 31 Oct 2026 | **Q11: the emulator runs on your Mac** (Apple M5, 16 GB), using arm64 images, after one approved install | Your answer. The codespace has no hardware virtualization |
| 31 Oct 2026 | **Rules facts recorded from the participant guide:** deadline 9:00 PM ET on 4 Nov (2:00 AM GMT on 5 Nov), three-minute video, public repo, demo shows only hackathon work, two problem statements. Q1, Q12 and most of Q13 answered; Q15 added (Muse Glimmer as the on-phone model) | The owner supplied the guide as PDFs on 31 Oct. The event pages block automated reading, so these stay owner-supplied |
| 31 Oct 2026 | **M3 spec drafted while M1 and the M4 spike run.** Bootloader lock is inferred from the verified-boot state (rule R-LOCK-FROM-VBS), because M1 found no official source for the property it read | Keeps Muse busy without waiting on reviews. M3 needs the lock state for strategy decisions |
| 1 Nov 2026 | **M3 spec v2 after ChatGPT's review.** Strategies that pass the rules are called `candidate`, not "possible", and list what's still unchecked. Unlock has one state from an ordered table. Model choice keeps unknowns as `unconfirmed`, and refuses only when every model definitely fails. Research must match the profile's phone. `plan-v1` carries an exact handoff for M4. A refusal's exit code (7) wins over an explanation failure. Bounded documentation reads are allowed while writing the docs | ChatGPT found the v1 rules could claim more than the facts prove. These changes keep every conclusion honest and give M4 one exact input |
| 1 Nov 2026 | **M3 spec v2.1: the M4 handoff carries the decision.** It includes the selection result, refusal reasons, input provenance and `build_allowed` (`emulator_only` or `none`). M4 must validate the whole plan and builds only when it's allowed | ChatGPT's re-review: a refused plan could otherwise look the same as an accepted one to M4 |
| 1 Nov 2026 | **Scoring plan v3 corrected after ChatGPT's review:** the open-weight bonus allows our own hardware or partner inference, so running the model in the phone's Assistant is our chosen route, not an organiser rule. The video has a timed 170-second outline. Schedule labels now give ET and GMT | ChatGPT checked the plan against the supplied guide. Scope (emulator only) and Baseten (development only) are unchanged |
| 1 Nov 2026 | **M4 spec v1 drafted before the spike's Mac results**, covering both routes (image or configuration bundle). The Mac result picks the route. The Assistant's runtime and model are decided in a first step that stops for your OK, preferring a Meta model | Lets GPT review while the Mac test runs, so M4 can start on Sunday instead of Monday |
| 1 Nov 2026 | **M4 spec v2 after ChatGPT's review.** The Assistant's runtime and complete model payload (format, tokenizer, support files) are pinned in step 0, with where the files live on each route and a hash chain up to the app. Each module is built only when selected, and the checks read real APK and model contents. The two Muse workers get separate worktrees, file ownership, one integrator and shared disk and live-call limits. Files must prove loopback-only listeners, refuse wrong codes and bad paths, and cap uploads. M4 now reports complete, partial or blocked, and a "not ready" Assistant is partial. A build with the Assistant selected but no resolved model stops (exit 9) | ChatGPT's review of v1 (five must-fix, one should-fix) |
| 1 Nov 2026 | **M4 spec v2.1:** the expected model hashes come from the approved Assistant manifest, which the build binds to the plan's model, revision and file names and sizes before building. M3's schema is unchanged | ChatGPT's re-review: M3's handoff has file sizes but no per-file hashes |
| 1 Nov 2026 | **The Assistant gets local and cloud modes (M4c), after M4.** Muse Glimmer (30B) can't run on the phone, so the open-weight bonus goes through Muse Spark Open by partner inference. StarGate still needs only the user's Meta key; the open-weight mode is optional and may use a partner key (Baseten for the demo) unless Q16 shows the Meta key works | Your direction (1 Nov): the phone is limited by its hardware, so it gets a small local model and cloud models, which also fits the open-weight bonus |
| 1 Nov 2026 | **Assistant runtime and model chosen (M4b step 0d):** ExecuTorch 1.5.1 (Meta's on-device runtime, Android library with `LlmModule`, minimum Android 6.0) running Llama 3.2 1B Instruct SpinQuant INT4 as a ready-made `.pte` (`executorch-community`, pinned at `911221e`, licence llama3.2). All five downloads matched their published SHA-256. The Files + Assistant emulator gets **6 GB RAM** (4 GB left only about 200 MB spare). llama.cpp with a GGUF file stays the verified alternative | Meta's own runtime with a real Android library beat launching a command-line program from the app; you approved downloading both to decide on facts |
| 1 Nov 2026 | **M4c spec v2 after ChatGPT's review.** Q16 answered: Muse Spark Open isn't on the Meta Model API, so the Meta key stays the only required key and the open-weight mode takes an optional Baseten key (Q3's development-only rule is superseded for this one mode). The Assistant comes in two APK variants (local with no permissions, cloud with internet only), recorded and checked in the build manifest. Providers, key routing, errors, key storage and enforced call and spend limits are pinned. M4c is time-boxed to 4 hours and never holds up the core demo | ChatGPT's review of v1 (four must-fix, one should-fix) |
| 1 Nov 2026 | **M4c spec v2.1 after ChatGPT's re-review.** One shared ledger in the product repo is the only record of cloud calls and spend. Every attempt, retry included, and its largest possible cost are reserved and saved before sending, against pinned prices; unpriced models are refused. Each cloud build reserves a fixed share for the phone, so a wiped emulator can't restore allowance. Adds a Keystore-failure test and a per-package backup check in place of the bare `bmgr` step | ChatGPT's re-review of v2 (two must-fix, one optional) |
| 1 Nov 2026 | **M4c spec v2.2: a byte-capped cost reservation.** Questions are capped at 8,000 UTF-8 bytes and the request body at 16 KB. Each allowed model has a pinned input-token ceiling (corrected in v2.3), and phone shares are priced for the most expensive allowed model. The phone refuses unlisted model IDs. If real usage ever exceeds a reservation, cloud calls for that provider stop | ChatGPT's re-review of v2.1 (one must-fix): characters don't bound tokens |
| 1 Nov 2026 | **M4c cost policy (v2.3): a conservative estimate, not a guarantee.** The default input-token ceiling is 32,768 (two tokens per byte of the 16,384-byte body cap). No provider publishes a billable-input limit for these models, so the reservation is an estimate: actual charges can be higher than the ledger shows (a request can cost more than its estimate, or be billed after a timeout or a reply without `usage`). The $5 Baseten and $2 Meta limits apply to the ledger's recorded costs plus reservations, not to actual charges; what is firm is 5 attempts per provider with capped input and output. The gate stops a provider if `usage` ever exceeds a reservation, and the owner compares billing pages with the ledger after the run (wording corrected in v2.4). Chosen over requiring a cited provider limit first, which no provider offers today and would block the open-weight demo | ChatGPT's re-review of v2.2 asked the owner to pick one of these two policies explicitly |
| 1 Nov 2026 | **M4a starts early, in two parts.** Part 1 (plan gate, manifest binding, `build-v1`, contents checks on APKs and model folders, section 7 items, launcher and Files apps) starts now. Part 2 (spike merge, route packaging, Route A image checks, demo builds, Mac steps) waits for the Mac result as before | The Mac test hasn't run yet, and none of Part 1 depends on the route, so the builder Muse would otherwise sit idle |
| 1 Nov 2026 | **M4 takes Route A (image).** On your Mac, the stock image booted. The spike's repacked image (Path A) booted as `stargate-spike-a`, and its marker read back from `/system/stargate-marker.txt` (`selection=stargate-spike-a`, `random=5c056da9fc167da1caf8d9c05d1040d1`), with no install or push after boot. Path B (stock image plus launcher) also passed and stays the fallback. Repacked images are booted with `-sysdir` pointing at a folder that holds them; on your Mac (emulator 37.2.13.0) `-system` booted the stock image instead. Evidence: [plan/evidence/m4-spike-mac-results.md](evidence/m4-spike-mac-results.md) | The M4 spike's Mac test (owner-run, 1 Nov); M4 spec section 2 picks Route A when Path A passes. Spike commit `c3c3739f017a0c24623b481e569193f3c3e28570` on `m4-spike` (Mac results recorded in its `docs/m4-spike.md`) |
