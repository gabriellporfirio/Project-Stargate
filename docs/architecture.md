# Architecture

```
Pixel Media Checker.exe ──► _runtime\pythonw.exe _app\app.py [FILE]      desktop
     (launcher/)        └─► _runtime\python.exe  _app\app.py --check …   headless

app.py ─┬─ desktop.py ── workflow.py ─┐
        └─ cli.py ────────────────────┼─► helpers.analyzer.analyze_file(path, context)
                                       │        │
           presets.py ─► PlaybackContext        ├─ helpers.probe.probe_media ──► MediaMetadata
                                                ├─ helpers.rules.evaluate_scala / evaluate_dise
                                                └─► AnalysisReport ──► reporting.py (text / JSON)
```

## Launcher

`launcher/src/launcher.c` sets up an isolated environment for the bundled
Python, then runs `app.py` with every argument passed through and returns
its exit code. See [launcher/README.md](../launcher/README.md) for the exact
environment and error codes.

## Entry points

- **`app.py`** builds the argument parser from `cli.py`. With `--check FILE`
  it builds a `PlaybackContext` from the flags and calls `cli.run_cli`,
  which prints a text or JSON report and returns 0/1/2/3. Otherwise it
  opens the desktop app, optionally with a file to check straight away.
- **`desktop.py`** (Tk) turns the selected *Player* and *Layout* into a
  context with `presets.make_context`. It runs `workflow.check_files` on a
  background thread and polls a queue to update the window. `appearance.py`
  holds the theme.
- **`workflow.py`** wraps each file's report in a `FileResult`. It maps it to
  one of four user-facing actions, merges identical findings from Scala and
  Dise into one line, and turns rule names into short instructions. A
  failure on one file never stops a batch.

## Playback context and presets

`helpers/context.py` defines `PlaybackContext`: which platforms to check
(Scala, Dise or both), the Scala playback engine, the Dise software version
and player hardware, the expected canvas size, the PDF workflow, and whether
several videos play at once. It validates every field on creation.
`presets.py` names the common combinations, e.g. *Dise One — Samsung* or
*3×1 landscape*, and both the CLI defaults and the desktop app use them.

## Reading files (`helpers/probe.py`)

`probe_media(path)` first checks the file is reachable, non-empty and has a
supported extension, then picks a reader:

| Media | Reader | Where it runs |
| --- | --- | --- |
| PDF | pypdf: page count, decodes every page's content stream | Worker process |
| Images (except WMF) | Pillow: size, mode, frames, EXIF orientation, full decode | Worker process |
| Video, audio, WMF | `ffprobe -show_streams -show_format` | Subprocess |
| …if ffprobe fails | PyAV: metadata plus first decoded frame | Worker process |

The worker process (`python -m helpers.probe --worker <reader> <file>`)
keeps crashes in native libraries and slow or damaged files from taking
down the desktop app. Each read has a 90-second timeout.

ffprobe is looked up in `_app/tools/`, then the `PIXEL_FFPROBE` environment
variable, then `PATH`.

There are two error types:

- **`ProbeError`**: the file itself is the problem (damaged, encrypted,
  unsupported). It is shown to the user as the reason.
- **`EngineError`**: a reader is missing or crashed. If every reader fails
  this way, the user is told to re-extract the app rather than blame the
  file.

Everything a reader finds goes into one `MediaMetadata` dataclass
(`helpers/models.py`).

## Rules (`helpers/rules.py`)

`evaluate_scala` and `evaluate_dise` each return a `PlatformResult`, a list
of `Finding`s with a status:

| Status | Effect |
| --- | --- |
| `PASS` | Meets the guideline |
| `INFO` | Shown, but never affects the result |
| `REVIEW` | Needs confirming or testing on the player |
| `FAIL` | An explicit restriction applies |

A platform's status is its worst non-`INFO` finding, or `REVIEW` if it has
none. The report's overall status is the worst of the selected platforms.
The CLI exit code and the desktop verdict both come from it. Every rule is
listed in [checks.md](checks.md).

## Reports (`helpers/reporting.py`)

`format_text_report` and `format_json_report` render an `AnalysisReport`:
the checker version, timestamp, playback context, technical summary,
per-platform findings, and probe notes. `technical_rows` also feeds the
*File properties* block in the desktop details view.
