# M6: The app, end to end (spec)

Status: v1, 1 Nov 2026, for review. Wires M1 to M5 into the guided app from the approved mockup (https://claude.ai/artifact/RFzSwh3CZbmsgrAfbD7MjD). It follows master-plan section 7 (1 Nov): no product name, only the logo mark; the phone shows controls only; the full experience lives on the computer; **cable first**, with Wi-Fi only once the cable works; the demo boots in the Android Emulator and says so.

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
- **Honesty rules:** every simulated value carries SIMULATED. Every model text carries "model explanation, not checked" (M2), except M5 edits that code accepted, which show the rule results. No step shows a hard-coded result: each screen renders a real output file, and its hash is shown in a "Details" view.

## 2. The phone's page (computer side, served by the phone)
- **One phone component serves it: the Link server.** M4's Files app grows into the Link server. It listens on `127.0.0.1` inside the emulator only, and the owner reaches it with `adb -s "$SERIAL" forward` as in M4 3a. It serves a small web page (Files and Assistant tabs, the logo and the status line "Connected by cable") and the APIs below. All of M4 3a still applies: the access code, the path rules, the size limits, and refusing no or wrong codes.
- **Files tab:** list, upload and download, as in M4.
- **Assistant tab:** chat with the phone's Assistant. The Assistant APK keeps **no** network permission (M4c local variant). The Link server relays each question to it through an Android **bound service** that only apps signed with the same key may call (`android:permission` with `protectionLevel="signature"`). A test shows that an app signed differently is refused. The answer, the mode and model ID, and the one-line stats come back to the page. If the build has the cloud variant (M4c), the page shows the mode switch. Otherwise it shows "On the phone" only.
- **Only selected services appear.** A Files-only build has no Assistant tab, and its Link server has no relay.
- **The status line is information only, never a switch** (owner, 1 Nov).

## 3. The phone's own screen (controls only)
- **Home:** the launcher shows a large clock, the logo mark in its own header (drawn by the launcher, not by changing Android's status bar), and one centred tile per selected service plus Status. It works in portrait and landscape.
- **Files controls:** running or stopped, start and stop, show or renew the access code.
- **Assistant controls:** ready or not, the model ID and hashes (small), the local or cloud switch (cloud variant only), and "Self-test" (asks a fixed question and shows the stats line).
- **Status:** build ID, selected services, and the connection. **Phone network:** a switch that warns first ("Services will only be reachable by cable"). It uses Android's own internet settings panel (`Settings.Panel.ACTION_INTERNET_CONNECTIVITY`) and needs no extra privilege. A direct toggle is out of scope unless it works for our system app without new privileges, which Muse checks and reports.
- **Out of scope** (section 7 / GPT): system updates, a privileged reboot, and any new updater.

## 4. Wi-Fi (stretch, only after the cable demo works)
Not built in M6 v1. The page may show a disabled "Wi-Fi (coming later)" option. Building it needs a separate design reviewed by GPT first: pairing and revoking computers, encryption and the trust model, binding only to the home network, the phone's network switch closing open sessions, and negative tests for unpaired clients. A real phone during the hackathon is **cable only** (owner, 1 Nov).

## 5. No branding
No product name anywhere in the UI. The logo mark (from GPT, file in the product repo with its source noted) appears in the platform header, at the bottom of the phone page's sidebar next to the status line, and in the launcher's home header. A test scans the UI files and APK labels for "StarGate" and "Spare".

## 6. Tests (offline)
- The platform server listens on `127.0.0.1` only, and every step renders from a real output file (a test swaps the file and the screen changes).
- Replays need no network. A live step without a key shows M0's error, not a crash.
- The Link server: M4 3a's tests still pass, the page and APIs refuse no or wrong codes, and it binds to `127.0.0.1` only.
- The relay: the signature permission is in the merged manifest. A differently signed caller is refused. The Assistant APK still has no network permission (read from the built APK). A Files-only build contains no relay.
- The launcher: only selected tiles, the logo in its header, and both orientations (layout test).
- The branding scan from section 5.

## 7. Mac proof (owner-run, written by Muse)
Reuses M4 section 6 and the device guard on every adb line. Boot the Files + Assistant image. `adb forward` the Link port. Open `http://127.0.0.1:<port>` in Safari. Upload and download a file with matching hashes. Ask one question in the Assistant tab with the emulator's networking off. Screenshot the home screen in portrait and landscape. Then `emu kill` and `adb devices`.

## 8. How the work is split
- **Builder Muse:** the platform (section 1) and the build and boot steps.
- **Second Muse:** the Link server, relay and launcher (sections 2 and 3), sharing the build lock as before.
- **Order:** the Link server's Files tab first, then the relay, then the launcher. The platform can start straight away against M1 to M5's outputs.

## Done when
- The platform clicks through all nine steps on `flagship` and `old32`, rendering real outputs, with labels as in section 1.
- On the Mac, the Files + Assistant image boots, and the phone's page works over the cable (Files both ways, one Assistant answer offline).
- All tests in section 6 pass, and the full suite still passes.

## Out of scope
Wi-Fi (section 4), real USB devices, flashing, updates, privileged reboot, the vault, and any VPN module.

## Demo (fits the video plan)
Profile → services with one refusal → research and the Meta install-plan decision → build → boot in the emulator → the phone's page: a file arrives, and the Assistant answers with the network off.
