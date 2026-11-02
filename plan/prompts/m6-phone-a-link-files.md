# M6 phone side, Part A: Link, Files behind it, signing and the home screen (third Muse)

Spec: `plan/milestones/M6-app.md` v2.1, sections 2, 2a, 2b, 3, 5 and their tests in 6. Design reference: `design/m6-mockup/` (`computer-side-phone-page.html` and `phone-home.html`). Paste only after GPT approves.

Part B (later): the Assistant behind Link. It changes the approved Assistant APK (a bound service, new signing), so it needs a new Assistant handoff, and it waits until the M4c bring-your-own-key fixup has landed.

## Paste into the new third Muse (terminal 5)
```
StarGate M6 phone side, Part A: Link, Files behind it, signing and the home screen. You are a new Muse. Spec and design: git -C /workspaces/Project-Stargate fetch origin, then read at the exact commit PLAN_SHA (git -C /workspaces/Project-Stargate show PLAN_SHA:<path>): plan/milestones/M6-app.md (v2.1; this part covers sections 2, 2a, 2b, 3 and 5, their tests in 6, and the Mac proof pattern in 7), plan/milestones/M4-image-build.md (v2.3; its build, checks and Mac-step patterns still apply), plan/master-plan.md section 7, and design/m6-mockup/ (README.md first). The spec wins where this prompt or the mockup differs. Record PLAN_SHA in the report.

Rules: work only in /workspaces/m6-phone and /workspaces/m6-phone-tools; every other workspace folder is read-only, and /workspaces/m4a-tools/out/ and /workspaces/m4b-tools/out/ are frozen; never push; never --yolo; keys and signing secrets never printed or written into logs or the repo (report a keystore by path and certificate SHA-256 only); NO network and NO live calls; no downloads or installs without ONE "INSTALL APPROVAL REQUIRED" block and my OK; /usr/local/bin/python3; shared build lock (flock /workspaces/.android-build.lock ...) for every Android or image build; never weaken or skip a test. Out of scope here: the Assistant (Part B), Wi-Fi, updates, privileged reboot.

Start: create the worktree /workspaces/m6-phone on a new branch m6-phone from m4a-build at 5a9c7e6 (check git log -1 shows it, the tree is clean and the full suite is green: 590 tests, 589 pass, 1 skip; stop and report if not). Another Muse works on the platform in /workspaces/m6 at the same time: stay out of stargate/app and the platform's files.

Step 0: inventory (no changes). Find and write down in the report: where the launcher and Files app sources live, how they are built today, which key signs each (keystore path and certificate SHA-256 only), the ports and access-code code in Files, and how M4 build adds apps to an image. If building Link needs anything not already installed, STOP with one INSTALL APPROVAL REQUIRED block.

Step 1: Link (spec 2 and 2a).
- A new small app, package com.stargate.link, in EVERY build like the launcher. It is the only app that listens on a socket: 127.0.0.1 only, the same port Files used in M4 3a (8080), reached with adb -s "$SERIAL" forward. It serves the phone's page: the tabs for the services in the build, the logo mark at the bottom of the sidebar, and the status line "Connected by cable" (information only, never a switch). Look per design/m6-mockup/computer-side-phone-page.html, plain HTML, CSS and JavaScript served from the APK, no outside hosts.
- Browser rules exactly as 2a: the access code is POSTed (the one request without a session, still needing an allowed full Origin); a correct code sets an HttpOnly, SameSite=Strict session cookie and a CSRF token; five wrong codes in a row lock sign-in for one minute; renewing the code or stopping Link signs out every session. Changes only by POST with the CSRF header. Host only 127.0.0.1:<port> or localhost:<port>; POST Origin exactly http://127.0.0.1:<port> or http://localhost:<port>; missing Origin refused; no CORS headers. textContent only for file names. Strict CSP on every page.
- Files tab: list, upload, download, with all of M4 3a's rules (path rules, size limits, 50 MB upload limit), checked in Link BEFORE calling Files.
- The Assistant tab does not appear in Part A builds, and nothing pretends it works.

Step 2: Files behind Link (spec 2).
- Files stops listening on any socket. It offers an Android bound service protected by android:permission with protectionLevel="signature"; Link's manifest lists what it may bind to.
- File bytes never travel inside one Binder call: pass a ParcelFileDescriptor pipe and copy in chunks; only names, sizes and results go in the call.
- Files re-checks path rules and size limits inside its service.

Step 3: signing (spec 2b).
- Our own packages that the build includes (launcher, Link, Files; the Assistant later) are signed with one key. The build reads each built APK's signing certificate SHA-256, checks they are all the same, records it in build-manifest.json, and fails with 8 on a mismatch among them. Stock Android packages are never compared and never re-signed.
- Build a test-only app signed with a different key that tries to bind to Files. It is never put in an image (test that).

Step 4: the phone's home screen (spec 3).
- Home: large clock, the logo mark in the launcher's own header (not Android's status bar), one centred tile per selected service plus Status. Portrait and landscape. Look per design/m6-mockup/phone-home.html.
- Link controls on a base screen (so every build has them): running or stopped, start and stop, show or renew the access code (renew or stop signs out every session).
- Files controls: running or stopped, storage used.
- Status: build ID, selected services, connection. Phone network: warns first ("Services will only be reachable by cable"), then opens Settings.Panel.ACTION_INTERNET_CONNECTIVITY. Check whether a direct toggle works for our system app without new privileges and report; do not add privileges.
- No product name anywhere (spec 5). The logo file comes from design/m6-mockup/logo-light.png with its source noted.

Step 5: composition and the build.
- M4 build adds Link to every build. Files-only = launcher + Link + Files. Files + Assistant and Assistant-only builds are composition-tested with synthetic images only in Part A (the Assistant comes in Part B); an Assistant-only build must have no Files app.
- Section 5 image checks gain: Link present; only Link listens (from the manifests); the signature permission in Files' merged manifest; one signing certificate across our packages.
- Build ONE real image: Files-only from demo/plans/ (re-validate the plan first) into /workspaces/m6-phone-tools/out/build-files-link, under the lock. It must exit 0 with all checks passing or fail with its documented code (no faking, no retry loops). Record bytes and inodes against the system free space. Gzip it and record both hashes.

Step 6: tests (offline), from spec 6: Link binds 127.0.0.1 only; M4 3a's Files tests pass through Link; access-code lockout; CSRF, Host and Origin refusals including wrong scheme or port and missing Origin; no CORS headers; injection in file names shown as text; sign-in POST works once per code and renew/stop ends sessions; composition for all three build kinds; the signature permission present; Link the only listener; Files has no network permission beyond M4's; the differently signed test app is refused and a mismatched project package fails with 8 while stock certificates are ignored; a 50 MB upload and download stream through Link and Files with matching hashes and no Binder call carries file bytes; the launcher shows only selected tiles, the logo in its header, both orientations (layout test); the branding scan. Full suite must stay green.

Step 7: Mac steps in docs/m6-phone.md for the Files-only + Link image, using exactly the M4 Part 3C patterns (environment block, sg_guard before EVERY adb line with AVD stargate-m6-files-link, cleanup log row first, sysdir of symlinks, -no-snapshot -wipe-data -no-metrics, zsh -n check): boot record with build ID; screenshots of home in portrait and landscape; adb forward of Link's port; sign in in Safari with the access code and upload and download a file with matching hashes; the refusals (no code, wrong code, wrong Origin by curl) give their codes; the negative bound-service test (install the test-only app on the EMULATOR ONLY, run its one action, which must be refused, uninstall it); listeners (only Link on 127.0.0.1:8080); emu kill; adb devices. Name the Mac files with an m6- prefix.

Commit each step with a clear message. Then STOP and save /tmp/m6-phone-a-report.md: first line "PHONE PART A READY, MAC PROOF PENDING" or "PARTIAL: <reason>" / "BLOCKED: <reason>"; PLAN_SHA; the Step 0 inventory; each spec item with file:line; the signing certificate SHA-256 and how it is used; the direct network-toggle finding; build exit code, manifest path, image and .gz hashes, bytes and inodes; the test count; every commit SHA. Print the report.
```
