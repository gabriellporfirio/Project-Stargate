# CLAUDE.md

Standards for working on Pixel Media Checker. They apply to every change,
whoever makes it. Read this before writing code; when something here
conflicts with a habit or a default, this file wins.

Pixel Media Checker checks video, image, audio and PDF files against Scala
and Dise digital-signage delivery guidelines. It ships as a portable Windows
folder: `Pixel Media Checker.exe` (launcher) + `_app/` (this repo's `app/`)
+ `_runtime/` (embedded Python 3.12). See [docs/architecture.md](docs/architecture.md).

## Repository layout

| Path | Contents |
| --- | --- |
| `app/` | Python application. Ships as `_app/`; run from inside it |
| `app/helpers/` | `probe` (reads files) → `rules` (decides) → `reporting` (formats); `context`, `models`, `analyzer` |
| `app/desktop.py`, `appearance.py`, `workflow.py`, `presets.py` | Tk desktop app, its theme, batch logic, player/layout presets |
| `app/app.py`, `cli.py` | Entry point and `--check` command line |
| `launcher/` | C source for `Pixel Media Checker.exe` (MinGW-w64) |
| `packaging/` | Builds and smoke-tests the portable folder |
| `tests/` | pytest suite; sample media is generated at test time |
| `docs/` | Architecture, checks reference, building, and `docs/design/` (company design language) |

## Commands

```sh
pip install -r requirements-dev.txt     # Python 3.12
ruff check .                            # must pass
pytest                                  # xvfb-run -a pytest on headless Linux
python app/app.py                       # desktop app
python app/app.py --check FILE [--json] # headless check; exit 0 pass, 1 review, 2 fail, 3 error
make -C launcher                        # build the launcher (needs MinGW-w64)
make -C launcher test wine-test         # launcher tests (wine-test needs Wine)
```

Build and release: [docs/building.md](docs/building.md).

## Ground rules

1. **`app/` is the shipped `_app/` folder.** Modules import each other as
   top-level names (`from helpers.probe import …`, `from presets import …`),
   the launcher runs `_app\app.py` with `_app` as the working directory, and
   the file-reader worker is started as `python -m helpers.probe`. Don't
   turn `app/` into a package, rename modules or move them without updating
   the launcher, packaging and tests together.
2. **Target Python 3.12 with Tcl/Tk 8.6 on 64-bit Windows.** The launcher
   hard-codes `tcl\tcl8.6`. Don't use features newer than 3.12.
3. **Pin every runtime dependency exactly** in `requirements.txt`, and only
   add packages that publish `win_amd64` wheels for CPython 3.12. They are
   installed into `_runtime` from wheels, with no compiler.
4. **Never commit binaries or media**: no Python runtime, ffprobe, `.exe`,
   build output or sample videos. Tests create their own media with Pillow,
   pypdf and PyAV.
5. **Windows behaviour comes first.** Start subprocesses with
   `CREATE_NO_WINDOW` and a timeout. Expect paths with spaces and non-ASCII
   names, and network shares. `pythonw.exe` has no console, so the desktop
   path must never rely on `print`.
6. **Keep diffs focused.** `ruff check .` must pass (ruff's default rules).
   Formatting is not enforced: don't reformat code you aren't otherwise
   changing.

## Code design

### Structure

- Keep the pipeline in one direction: `probe` produces `MediaMetadata`;
  `rules` turn metadata plus a `PlaybackContext` into `Finding`s;
  `reporting` and `workflow` turn findings into words. The UI and CLI never
  make rule decisions, and rules never format text for a particular screen.
- Model data with dataclasses. Configuration-like objects are frozen and
  validate themselves in `__post_init__` (see `PlaybackContext`), raising
  `ValueError` with a message a user could act on.
- Add new player profiles and layouts in `presets.py`, not in the UI.
- Prefer small private helpers (`_name`) over deep class hierarchies;
  follow the existing module's style.

### Errors

- Raise `ProbeError` when the **file** is the problem. Its message is shown
  to the user as-is, so write it as a plain instruction ("This PDF is
  incomplete or damaged. Export a new copy.").
- Raise `EngineError` when the **app** is the problem (a reader is missing
  or crashed).
- Catch broad exceptions only at boundaries (CLI, batch loop, worker, Tk
  callbacks). There, log the detail with `logging.exception` and show a
  plain message. Users never see a traceback.
- Run native readers (Pillow, pypdf, PyAV) in the isolated worker process
  with a timeout, so a crash or a hang on a bad file cannot take down the
  desktop app.

### Rules and statuses

- `PASS` meets the guideline. `INFO` is shown but never changes the result.
  `REVIEW` is anything unconfirmed. `FAIL` is only for an **explicit,
  published restriction**. When in doubt, use `REVIEW`.
- Every finding has a stable rule name, observed value, expected value and,
  where useful, a detail. Rule names are keys elsewhere: `short_message()`
  in `workflow.py` maps them to the one-line instructions the desktop app
  shows, so update both together.
- A rule change needs the guideline it comes from (document and date) in
  the PR, a test in `tests/test_rules.py`, and an update to
  [docs/checks.md](docs/checks.md). Update `DISE_SOURCE` or `SCALA_SOURCE`
  when the guideline document changes.

### Desktop app (Tk)

- Long work runs on a background thread. Results go back through a
  `queue.Queue` that the UI polls with `root.after`. Never touch a widget
  from a worker thread.
- A check of many files keeps going after one fails. Each file gets its own
  result (see `workflow.check_files`).
- Unexpected callback errors go to `callback_error`, which logs them and
  shows a friendly dialog; don't let them escape.
- Visual rules are in [Design language](#design-language) below.

### Launcher (C)

- C11, compiled with `-Wall -Wextra -Werror`. Its behaviour (interpreter
  choice, environment, exit codes 10–16) is a contract documented in
  [launcher/README.md](launcher/README.md) and checked by
  `launcher/tests/wine_test.py`. Change all three together.
- The version lives in `launcher/src/version.h` and `launcher/launcher.manifest`.

### Comments and docs

- Comments explain **why** (a constraint, a past bug, a non-obvious
  choice), not what the next line does. Keep them short.
- Update the matching doc in the same PR: rules → `docs/checks.md`;
  structure → `docs/architecture.md`; build or release → `docs/building.md`;
  launcher behaviour → `launcher/README.md`; anything users notice →
  `CHANGELOG.md` under *Unreleased*.

## User-facing text

- **British English**: colour, licence, organise.
- Sentence case, plain words, full stops. Lead with what to do: "Export an
  RGB copy.", "Confirm the player before scheduling."
- Use the fixed action vocabulary exactly: **Pass**, **Check before
  scheduling**, **Fail - check with client**, **Could not check**.
- No jargon in headlines; technical values go in *Details* and in reports
  ("Detected" / "Expected").
- No error codes, stack traces or blame. Say what happened and what to try
  ("Cannot access this file. Try a local copy.").

## Design language

The company design language lives in [docs/design/](docs/design/):
`tokens.css` (tokens) and `pixel-ui.css` (components), frosted-glass theme
of 25 September 2026. **It is the source of truth for every visual
decision.** The desktop app is Tk, so `app/appearance.py` mirrors the tokens
in its `COLORS` table and the `apply_theme` styles.

### Translating tokens to Tk

Tk has no transparency or backdrop blur. The CSS itself says that without
blur, glass falls back to solid (`--bg-solid`). The app therefore uses
**each translucent token flattened over `--bg-solid` (#2b2b2b)**:
`channel = round(value × alpha + 0x2b × (1 − alpha))`. Opaque tokens are
used as-is.

| `COLORS` key | Token | Value |
| --- | --- | --- |
| `paper` | `--bg` | `#232323` (window background) |
| `card` | `--bg-solid` | `#2B2B2B` (cards and panels) |
| `inner` | `--bg-inner` | `#383838` (inputs, rows inside a card) |
| `hover` | `--bg-hover` | `#454545` |
| `line` | `--border` | `#494949` |
| `highlight` | glass highlight, `rgba(255,255,255,.22)` | `#5A5A5A` (secondary button borders) |
| `selected` | `--selected` | `#505050` (list selection) |
| `ink` | `--text-primary` | `#F2F2F2` |
| `secondary` | `--text-secondary` | `#BBBBBB` |
| `muted` | `--text-muted` | `#9A9A9A` |
| `accent` | `--accent` | `#C0394B` |
| `accent_active` | `--accent-hover` | `#A8303F` |
| `accent_bright` | `--accent-bright` | `#DD5A6E` (focus ring, progress) |
| (primary button fill) | `--accent-gradient` | `#CC4659` → `#B8364A` |
| `pass` | `--on-green` | `#6EE7A0` |
| `review` | `--on-amber` | `#F5C26B` |
| `fail` | `--on-red` | `#FF9C9C` |
| `info` | `--accent-link` | `#EC8F9C` |

`hover` and `selected` sit a few steps lighter than the exact flattening
(`#444444`, `#4D4D4D`) so they show against the inner surfaces; keep them.
Derive any new colour with the formula above from an existing token.
**Never introduce a colour that has no token.** If the design needs a new
one, it is added to the company design language first.

### Shape and type

- Radii follow the tokens: cards and panels `--radius` (22),
  inputs and menus `--radius-sm` (12). Buttons are pills (`--radius-pill`;
  in Tk an 18px corner on a 36–40px-high button). Inputs are rounded,
  **not** pills.
- Fonts: body **Figtree**, headings **Cal Sans**, used when installed on the
  PC. Figtree falls back to Segoe UI, then Roboto, then Arial; Cal Sans falls
  back to the body font. `_fonts()` handles this, so don't hard-code a
  family elsewhere. Headings are never bold
  (Cal Sans has one weight).
- Tk sizes are points. Body 10, small and caption 9, buttons 10 bold, card
  results 15 bold, panel headings 12, window title 16. Reuse the named
  fonts from `apply_theme()` rather than adding sizes.

### Layout and spacing

- The window has a 16px frame (as `.app-shell`). Cards are laid out
  in a single column with 12–14px between rows. Result cards sit three across
  with 12px between them.
- Inside panels, content starts 20px from the left edge, as in
  `.panel-header` and `.panel-body`; header, body and rows line up down that
  edge. Result cards use 18px.
- Card labels are uppercase muted captions (`.stat-label`); the value under
  them is large and bold (`.stat-value`).
- The window must stay usable at its minimum size (860 × 580). Long text
  wraps or is shortened with an ellipsis in the middle (`compact_filename`),
  never clipped.

### Components

| Tk style (`appearance.py`) | Design language |
| --- | --- |
| `Card.TFrame` | `.panel` / `.stat-card` (glass card, solid in Tk) |
| `Primary.TButton` | `.btn-primary` (crimson gradient pill) |
| `Secondary.TButton` | `.btn` (neutral pill) |
| `Setup.TCombobox` | `select` / text inputs (rounded `--radius-sm`, `--bg-inner`, focus ring `--accent-bright`) |
| `CardCaption.TLabel` + `Result.TLabel` | `.stat-label` + `.stat-value` |
| `Muted.TLabel` | hint and summary text (`--text-muted`) |
| `Horizontal.TProgressbar` | `.portal-spinner` accent (`--accent-bright`), thin bar |
| `Vertical.TScrollbar` | neutral, `highlight` thumb on `card` trough |

### Rules for UI changes

- **Crimson is for action and focus only**: the one primary button in a
  view, focus rings, progress, the brand. Selected states (list selection,
  chosen items) are **neutral**, not crimson.
- Status colours are text colours on dark surfaces: Pass `pass`, Check
  before scheduling `review`, Fail and Could not check `fail`. Don't use
  them for anything else.
- One primary button per view; everything else is secondary.
- Reuse existing styles from `apply_theme()`. A new widget type gets a new
  named style there, built from the tokens, never per-widget colours or
  fonts.
- Any web UI added later (a report page, an internal portal view) uses
  `docs/design/tokens.css` and `pixel-ui.css` directly with their existing
  class names, and is not restyled.

## Process

- **Branches**: `feature/…`, `fix/…`, `docs/…`, `build/…`, created from
  `main`. Never commit straight to `main`.
- **Pull requests**: one topic each, using the PR template (Summary,
  Changes, Testing, Notes for reviewers). Split large work into stacked
  PRs: each targets the previous one's branch and says so in *Notes*. Merge
  them in order with merge commits, retargeting the next PR to `main` after
  each merge.
- **Commits**: imperative subject of 72 characters or fewer ("Add …", "Fix …",
  "Pin …"), a blank line, then a body explaining why. One logical change per
  commit. Keep a verbatim import separate from any edit to it, so the edit
  can be reviewed on its own.
- **CI** (`.github/workflows/ci.yml`) runs ruff, pytest on Windows and Linux,
  and the launcher build and tests. PRs that touch `packaging/`,
  `launcher/` or `requirements.txt` also build and smoke-test the portable
  app on Windows. A job that was cancelled before it got a runner is a
  GitHub capacity problem, not a code failure: re-run it.
- **Versions and releases**: bump `launcher/src/version.h` and
  `launcher/launcher.manifest` together, move *Unreleased* in `CHANGELOG.md`
  under the new version, merge, then push a `vX.Y.Z` tag. The release
  workflow publishes the zip. See [docs/building.md](docs/building.md).

## Known issues

- The launcher passes `--runtime-check`, which `app.py` doesn't accept yet,
  so it exits with a usage error.
- Reports show checker version `1.0` (`CHECKER_VERSION` in
  `app/helpers/analyzer.py`); the app is 1.2.0.
