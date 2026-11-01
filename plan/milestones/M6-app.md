# M6: The app, end to end (spec)

Status: v2, 1 Nov 2026. v2 folds in [GPT's night-batch review](../../reviews/2026-11-01-chatgpt-night-batch-pr34.md): the phone's web server is now its own base component (Link), every screen is tied to the current inputs by hash, and the browser rules are written down (sections 2, 2a, 2b, 6). v1 wired M1 to M5 into the guided app from the approved mockup (https://claude.ai/artifact/RFzSwh3CZbmsgrAfbD7MjD). It follows master-plan section 7 (1 Nov): no product name, only the logo mark; the phone shows controls only; the full experience lives on the computer; **cable first**, with Wi-Fi only once the cable works; the demo boots in the Android Emulator and says so.

## Goal
Two connected parts, both clickable end to end on simulated phones:
1. **The platform** (on the computer): the guided journey that checks a phone, offers what fits, researches, plans, builds the real emulator image (M4) and shows the real-phone install plan (M5).
2. **The phone's page** (served by the booted image, opened on the computer over the cable): Files and the Assistant chat, plus the phone's own controls-only home screen.

## 1. The platform (computer side)
- **Where it runs:** in the codespace, next to M1 to M5 and the keys. `stargate app` starts a small local web server on `127.0.0.1` (port in docs), using Python's standard library only, and the owner opens it through the codespace's **private** forwarded port, as in M4's transfer step. It never listens on other addresses (tested). No new Mac installs.
- **The nine steps** (the mockup's order), each calling the real code:

| Step | What it calls | Shown label |
|---|---|---|
| Welcome | none | |
| Connect | M1 `scan --sim <profile>`. Real USB stays disabled (M1's stub); the screen explains how to turn on developer options, with brand-specific help only from M2 facts or "unknown" | SIMULATED profile |
| Questions | A few plain questions that pre-select services | |
| Your phone | M1 profile: facts with measured, inferred or unknown | SIMULATED |
| Services | M3 `plan`: fits, unconfirmed or refused, with reasons and numbers. Not offered means a refusal with its reason | |
| Research | M2 report (live or replay, labelled), then M5 `install-plan` with the Meta model's edits, quotes, links and rule results | "Live" or "Replay of a live run on <date>" |
| Build | M4 `build` for the accepted plan: real progress, the build ID, the image size against the limit, and the checks | |
| Boot | The Mac steps for this build, ready to copy, with the target fixed to "Android Emulator (this demo)". The real-phone path shows the M5 plan with "not run" | |
| Done | What was built, and a link to open the phone's page after boot | |

- **Live calls:** none are needed to click through. Research and the install plan use **replays** by default. A live run is opt-in per step, uses M2's and M5's budgets, and the label switches to "Live". Keys never reach the browser: the server makes the calls, and pages never show or log a key.
- **Honesty rules:** every simulated value carries SIMULATED. Every model text carries "model explanation, not checked" (M2), except M5 edits that code accepted, which show the rule results.

### 1a. Every screen is tied to the current inputs (new in v2)
Rendering a real file isn't enough: the file must belong to the phone and choices on screen now.
- **One session record** holds the current profile, answers and selection, each with its SHA-256. Every output (M2 report, M3 plan, M5 plan, M4 build, and any replay) records the hashes of the inputs it was made from.
- **A screen shows an output only if its input hashes equal the current ones.** Otherwise it shows "out of date" and the button to re-run it. The "Details" view shows the output's hash and its input hashes.
- **Changes flow down.** Changing the profile or selection marks the M2 report, M3 plan, M5 plan and build as stale. New research facts that M3 reads re-run M3, and everything after it becomes stale.
- **Build is blocked** for a stale plan, a refused plan, or a plan whose input hashes don't match (shown with the reason, and M4's own gate still applies).
- **Jobs have IDs.** Each run gets a job ID and its input hashes. A result that arrives for an older job is discarded and logged, never shown.
- A replay is shown only if its recorded input hashes equal the current ones, and it keeps its replay label.

### 1b. Browser rules for the platform (new in v2)
Loopback and a private forwarded port don't replace these:
- **Sign-in:** `stargate app` prints a one-time start link with a random token in the terminal. Opening it sets a session cookie (`HttpOnly`, `SameSite=Strict`, `Secure` when served over the forwarded https URL) and the token stops working. Every request without a valid session is refused (401).
- **Changes only by POST.** Every action that changes something (run a step, start a build, go live) is a POST with a CSRF token in a header that must match the session. GET never changes anything.
- **Host and Origin checks:** the `Host` header must be `127.0.0.1:<port>`, `localhost:<port>`, or the one forwarded host the owner passes on the command line. A POST's `Origin` must be one of those. Anything else is refused (403). No CORS headers are ever sent.
- **Safe rendering:** model text, source quotes and file names are inserted as plain text (`textContent`), never as HTML. Every page sends a Content-Security-Policy that allows only the app's own scripts and styles (no inline scripts, no outside hosts).
- **Limits:** request bodies at most 64 KB; one live run at a time per step.

## 2. The phone's page (computer side, served by the phone)
- **Link: the base component that serves the page.** Link is a small app of its own, included in **every** build, like the launcher. It is the only app on the phone that listens on a socket. It listens on `127.0.0.1` inside the emulator only, and the owner reaches it with `adb -s "$SERIAL" forward` as in M4 3a. It serves a small web page (the tabs for the selected services, the logo and the status line "Connected by cable").
- **Files and the Assistant don't listen on sockets.** Each one offers an Android **bound service** that Link calls. The services are protected with `android:permission` at `protectionLevel="signature"`, so only apps signed with the same key may bind.
- **Only selected services appear.** A Files-only build is launcher + Link + Files. An Assistant-only build is launcher + Link + Assistant, with **no** Files app (as M4 requires). Link shows only the tabs whose service is in the build, and its manifest lists what it may bind to.
- **Files tab:** list, upload and download. All of M4 3a's rules apply, and they are enforced **in both places**: Link checks the access code, path rules and size limits before calling Files, and Files checks the path rules and size limits again inside its service.
- **Assistant tab:** chat with the phone's Assistant. The Assistant APK keeps **no** network permission in the local variant (M4c). The answer, the mode and model ID, and the one-line stats come back to the page. If the build has the cloud variant (M4c), the page shows the mode switch. Otherwise it shows "On the phone" only.
- **The status line is information only, never a switch** (owner, 1 Nov).

### 2a. Browser rules for the phone's page (new in v2)
- **Access code to session:** the page asks for the access code shown on the phone. A correct code sets a session cookie (`HttpOnly`, `SameSite=Strict`) and a CSRF token. Wrong codes are refused, and five wrong codes in a row lock sign-in for one minute.
- **Changes only by POST** with the CSRF header. Upload, delete and asking a question are POSTs.
- **Host and Origin:** only `127.0.0.1:<port>` and `localhost:<port>`. No CORS headers.
- **Safe rendering:** answers and file names are inserted with `textContent`, and every page sends a strict Content-Security-Policy.
- **Chat limits:** a question is at most 2,000 characters and 8,000 bytes. One answer is generated at a time; a second question while one is running gets "busy" (429). An answer that takes longer than 60 seconds is stopped and reported.

### 2b. Signing (new in v2)
Launcher, Link, Files and the Assistant are signed with the same key. The build checks that every app in the image has the same signing certificate (SHA-256 of the certificate, read from each built APK) and records it in `build-manifest.json`. A mismatch fails with 8. A test-only app signed with a different key is built for the negative test (section 7) and is never put in an image.

## 3. The phone's own screen (controls only)
- **Home:** the launcher shows a large clock, the logo mark in its own header (drawn by the launcher, not by changing Android's status bar), and one centred tile per selected service plus Status. It works in portrait and landscape.
- **Files controls:** running or stopped, start and stop, show or renew the access code.
- **Assistant controls:** ready or not, the model ID and hashes (small), the local or cloud switch (cloud variant only), and "Self-test" (asks a fixed question and shows the stats line).
- **Status:** build ID, selected services, and the connection. **Phone network:** a switch that warns first ("Services will only be reachable by cable"). It uses Android's own internet settings panel (`Settings.Panel.ACTION_INTERNET_CONNECTIVITY`) and needs no extra privilege. A direct toggle is out of scope unless it works for our system app without new privileges, which Muse checks and reports.
- **Out of scope** (section 7 / GPT): system updates, a privileged reboot, and any new updater.

## 4. Wi-Fi (stretch, only after the cable demo works)
Not built in M6. The page may show a disabled "Wi-Fi (coming later)" option. Building it needs a separate design reviewed by GPT first: pairing and revoking computers, encryption and the trust model, binding only to the home network, the phone's network switch closing open sessions, and negative tests for unpaired clients. A real phone during the hackathon is **cable only** (owner, 1 Nov).

## 5. No branding
No product name anywhere in the UI. The logo mark (from GPT, file in the product repo with its source noted) appears in the platform header, at the bottom of the phone page's sidebar next to the status line, and in the launcher's home header. A test scans the UI files and APK labels for "StarGate" and "Spare".

## 6. Tests (offline)
- **Platform server:** listens on `127.0.0.1` only.
- **Inputs by hash (1a):** changing the profile or selection marks every later output stale and the screen shows "out of date"; a research change re-runs M3; Build is refused for a stale, refused or mismatched plan; a result from an older job is discarded; a replay with different input hashes isn't shown.
- **Platform browser rules (1b):** no session gives 401; the start token works once; a POST without the CSRF header, with a wrong one, or from a foreign `Origin` is refused; a wrong `Host` is refused; no response has CORS headers; a GET never changes state; model text containing `<script>` or `<img onerror>` is shown as text; the CSP header is present on every page.
- Replays need no network. A live step without a key shows M0's error, not a crash.
- **Link (2, 2a):** binds to `127.0.0.1` only; M4 3a's tests still pass through Link; the access-code lockout; CSRF, Host and Origin refusals; injection in file names and answers is shown as text; a 2,001-character question is refused; a second question while one runs gets 429; a slow answer stops at 60 s.
- **Composition:** Files-only, Assistant-only and Files + Assistant builds each contain exactly launcher + Link + their services. An Assistant-only build has no Files app. Link shows only the tabs in the build.
- **Bound services and permissions:** the signature permission is in each service's merged manifest; Link is the only app with a listening socket; the local Assistant has no permissions and the cloud Assistant has exactly `INTERNET` (read from the built APKs); Files has no network permission beyond what M4 allows; every app shares one signing certificate (2b).
- The launcher: only selected tiles, the logo in its header, and both orientations (layout test).
- The branding scan from section 5.

## 7. Mac proof (owner-run, written by Muse)
Reuses M4 section 6 and the device guard on every adb line. Boot the Files + Assistant image. `adb forward` the Link port. Open `http://127.0.0.1:<port>` in Safari and sign in with the access code. Upload and download a file with matching hashes. Ask one question in the Assistant tab with the emulator's networking off. **Bound-service checks:** Link reaches both services (positive); then the owner installs the test-only, differently signed app on the emulator only and runs its one action, which must be refused by both services (negative), and uninstalls it. Screenshot the home screen in portrait and landscape. Then `emu kill` and `adb devices`.

## 8. How the work is split
- **Builder Muse:** the platform (section 1, 1a, 1b) and the build and boot steps.
- **Second Muse:** Link, the bound services, signing checks and launcher (sections 2, 2a, 2b and 3), sharing the build lock as before.
- **Order:** Link with the Files tab first, then the Assistant relay, then the launcher. The platform can start straight away against M1 to M5's outputs.

## Done when
- The platform clicks through all nine steps on `flagship` and `old32`, rendering outputs that match the current inputs, with labels as in section 1.
- On the Mac, the Files + Assistant image boots, and the phone's page works over the cable (Files both ways, one Assistant answer offline, the negative bound-service test refused).
- All tests in section 6 pass, and the full suite still passes.

## Out of scope
Wi-Fi (section 4), real USB devices, flashing, updates, privileged reboot, the vault, and any VPN module.

## Demo (fits the video plan)
Profile → services with one refusal → research and the Meta install-plan decision → build → boot in the emulator → the phone's page: a file arrives, and the Assistant answers with the network off.
