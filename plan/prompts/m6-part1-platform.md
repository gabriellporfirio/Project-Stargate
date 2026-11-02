# M6 Part 1: the platform (builder Muse)

Spec: `plan/milestones/M6-app.md` v2.1, sections 1, 1a, 1b, 5 and 6 (platform tests only). Design reference: `design/m6-mockup/`. Paste only after GPT approves.

Part 2 (later, builder): wire in M5 once its live run is done, plus the Boot and Done steps against Link. The second Muse builds Link, the bound services, signing and the launcher (sections 2, 2a, 2b, 3) after M5 and the M4c fixup.

## Paste into the builder Muse
```
StarGate M6, Part 1: the platform (the guided computer app). You are the builder Muse. Spec and design: git -C /workspaces/Project-Stargate fetch origin, then read at the exact commit PLAN_SHA (git -C /workspaces/Project-Stargate show PLAN_SHA:<path>): plan/milestones/M6-app.md (v2.1; this part covers sections 1, 1a, 1b, 5 and the platform tests in 6), plan/master-plan.md section 7, and design/m6-mockup/ (README.md first; the HTML files are a picture of the look, not code to copy). The spec wins where this prompt or the mockup differs. Record PLAN_SHA in the report.

Rules (as before): never push; never --yolo; keys never read, printed or written (the server only passes the existing env var names to the existing M2 client); NO network and NO live Meta or Baseten calls in this part; no downloads or installs without ONE "INSTALL APPROVAL REQUIRED" block and my OK; /usr/local/bin/python3, standard library only for the server; no npm, no build tools, no outside fonts or CDNs; shared build lock (flock /workspaces/.android-build.lock ...) for any Android build; /workspaces/m4a-tools/out/ artifacts are read-only here; never weaken or skip a test.

Start: create the worktree /workspaces/m6 on a new branch m6-platform from m4a-build at 5a9c7e6 (check git log -1 shows it, the tree is clean and the full suite is green there: 590 tests, 589 pass, 1 skip; stop and report if not). Do not merge the M5 branch in this part: it is still in progress.

Step 1: the server and its browser rules (spec 1 and 1b).
- `stargate app [--port 8770] [--forwarded-host <host>]`: a small server on 127.0.0.1 only (ThreadingHTTPServer), serving plain HTML, CSS and JavaScript files from the package. Never another address.
- Sign-in exactly as 1b: the terminal prints a one-time start link with a random token; GET shows only a "Sign in" button and changes nothing; the POST (with an allowed full Origin) sets an HttpOnly, SameSite=Strict session cookie (Secure when the forwarded https host is used) and a CSRF token, and the start token stops working. Everything else without a session is 401.
- Every change is a POST with the CSRF header; GET never changes anything. Host must be 127.0.0.1:<port>, localhost:<port> or the one --forwarded-host. POST Origin compared as a full origin against exactly http://127.0.0.1:<port>, http://localhost:<port>, https://<forwarded host>; missing Origin refused; anything else 403. No CORS headers ever. Strict Content-Security-Policy on every response (own scripts and styles only, no inline scripts). Bodies at most 64 KB. One run at a time per step.
- Model text, quotes and file names are inserted with textContent only.

Step 2: the session record and inputs by hash (spec 1a).
- One session record: profile, answers, selection, each with its SHA-256. Every output records its input hashes. A screen shows an output only when its input hashes equal the current ones; otherwise "out of date" with a re-run button. "Details" shows the output hash and its input hashes.
- Changes flow down (profile or selection change marks M2, M3, M5 and the build stale; new research facts re-run M3). Jobs have IDs; a result for an older job is discarded and logged. A replay is shown only if its recorded input hashes match.
- Build is blocked for a stale, refused or hash-mismatched plan, with the reason (M4's own gate still applies).

Step 3: the nine steps (spec 1 table), each calling the real code in-process or by the existing CLI:
- Welcome; Connect (M1 scan --sim <profile>, SIMULATED label; real USB stays M1's stub; developer-options help only from M2 facts or "unknown"); Questions (a few plain questions that pre-select services); Your phone (M1 facts with measured, inferred or unknown); Services (M3 plan: fits, unconfirmed or refused with reasons and numbers).
- Research: the M2 report from an existing recorded replay, labelled "Replay of a live run on <date>", shown only when its input hashes match. If no matching recorded replay exists, show "No recorded research for this phone yet" and record which ones exist in the report: never fabricate one. The M5 install-plan panel shows "Install plan: added in Part 2" in this part.
- Build: for an accepted plan, either reuse an existing build in /workspaces/m4a-tools/out/ ONLY if its build-manifest.json records the same plan hash as the current plan, or run M4 build under the lock into a new folder under /workspaces/m6-tools/out/. Show real progress, the build ID, image size against the limit, and the check results.
- Boot: the Mac steps for this build, generated from its build-manifest.json (image name, hashes, AVD settings, model payload hashes when present), ready to copy, target fixed to "Android Emulator (this demo)". Real-phone path shows "Install plan: added in Part 2".
- Done: what was built; the phone's page link shows "arrives with Link (M6 Part 3)".
- Live calls: none. A "Go live" control may appear but stays disabled in this part with "Live runs: not in this part".
- Honesty labels: SIMULATED on every simulated value; "model explanation, not checked" on M2 model text.

Step 4: the look (design/m6-mockup/README.md): dark background #06080F, teal #5EEAD4 and indigo #818CF8 accents, rounded panels, faint grid, soft glows, a step rail, short plain sentences, warnings in amber. Short fade-and-rise and progress animations, all off under prefers-reduced-motion. system-ui and ui-monospace fonts. Works at 1280 px and stays usable at 390 px. No product name anywhere; the logo mark (design/m6-mockup/logo-light.png, copied into the package with its source noted) only in the platform header. Real buttons, labels and focus outlines; text contrast at least 4.5:1.

Step 5: tests (offline), from spec 6 for the platform: listens on 127.0.0.1 only; the inputs-by-hash cases; the 1b browser rules (no session 401, start token once, start-link GET changes nothing, CSRF missing or wrong refused, foreign Origin and wrong scheme or port refused, missing Origin refused, wrong Host refused, no CORS headers on any response, no GET changes state, <script> and <img onerror> in model text shown as text, CSP on every page, 64 KB limit); replays need no network; a live step without a key shows M0's error, not a crash; the branding scan over UI files for "StarGate" and "Spare" (case-insensitive whole words in UI text); a click-through test of all nine steps for flagship (files,assistant) and old32 (Build blocked by the refused plan, with its reason) through the HTTP API. Full suite must stay green.

Commit each step with a clear message. Then STOP and save /tmp/m6-part1-report.md: first line "PLATFORM PART 1 READY" or "PARTIAL: <reason>" / "BLOCKED: <reason>"; PLAN_SHA; the starting commit; each spec item with file:line; which M2 replays exist and which steps show them; the build-reuse decision for flagship; the test count; every commit SHA; and exact codespace commands for me to open it: start the server, forward port 8770 as Private, and the start link. Print the report.
```
