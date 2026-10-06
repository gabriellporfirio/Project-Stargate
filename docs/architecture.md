# Architecture

```
Pixel Media Checker.exe ──► _runtime\pythonw.exe _app\app.py [FILE]
     (launcher/)

app.py ── desktop.py ── workflow.py ──► helpers.analyzer.analyze_file(path, context)
                                                 │
          presets.py ─► PlaybackContext          ├─ helpers.probe.probe_media ──► MediaMetadata
                                                 ├─ helpers.rules.evaluate_scala / evaluate_dise
                                                 └─► AnalysisReport ──► workflow.py (verdict, details)
```

## Launcher

`launcher/src/launcher.c` sets up an isolated environment for the bundled
Python, then runs `app.py` with every argument passed through and returns
its exit code. See [launcher/README.md](../launcher/README.md) for the exact
environment and error codes.

## Entry points

- **`app.py`** opens the desktop app. A file dropped onto the launcher, or
  opened with it, arrives as the first argument and is checked as soon as
  the window opens. The app has no command-line mode.
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
*3×1 landscape*, which are what the desktop app offers.

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
The desktop verdict comes from it. Every rule is listed in
[checks.md](checks.md).

## File properties (`helpers/reporting.py`)

`technical_rows` turns `MediaMetadata` into the label/value rows of the
*File properties* block in the desktop details view, with `human_size`,
`human_duration` and `human_bitrate` for readable values.
