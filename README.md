# Pixel Media Checker

Checks video, image, audio and PDF files against **Scala** and **Dise**
digital-signage delivery guidelines before content is scheduled, and tells
the operator in plain language whether the file is ready:

| Result | Meaning |
| --- | --- |
| **Pass** | Matches the checks for the selected player and layout |
| **Check before scheduling** | Something needs confirming (player support, layout, audio track…) |
| **Fail - check with client** | An explicit restriction applies; request a new export |
| **Could not check** | The file is missing, damaged, locked or unsupported |

It reads codec, container, resolution, frame rate, bitrate, H.264
profile/level, colour format, rotation, audio and extra tracks. It then
applies the rules for the chosen setup, e.g. *Dise One — Samsung* on a
*3×1 landscape* wall. See [docs/checks.md](docs/checks.md) for every rule.

## Using it

Download `Pixel-Media-Checker-<version>-win64.zip` from
[Releases](../../releases), extract it, and run **Pixel Media Checker.exe**.
Keep the executable, `_app` and `_runtime` together; nothing needs
installing.

1. Choose the **Player** and **Layout** the content is for.
2. Click **Choose files** and select one or more files. You can also drop a
   file onto the exe or use *Open with*.
3. Read the verdict per file; **Show details** lists each issue with the
   detected and expected values and the file's properties.

## Repository layout

| Path | Contents |
| --- | --- |
| [`app/`](app) | Python application; ships as `_app/` |
| [`app/helpers/`](app/helpers) | File readers (`probe`), Scala/Dise rules, report model and formatting |
| [`launcher/`](launcher) | C source for `Pixel Media Checker.exe` |
| [`packaging/`](packaging) | Assembles and smoke-tests the portable folder |
| [`tests/`](tests) | pytest suite (sample media is generated at test time) |
| [`docs/`](docs) | [Architecture](docs/architecture.md), [checks reference](docs/checks.md), [building and releasing](docs/building.md), [design language](docs/design/) |
| [`CLAUDE.md`](CLAUDE.md) | Code, design and process standards for every change |

## Development

Python 3.12 (the version bundled with the app) and, ideally, ffmpeg on
`PATH` so the ffprobe reader is exercised:

```sh
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
ruff check .
python app/app.py               # desktop app
```

The launcher builds with MinGW-w64: `make -C launcher`, with tests via
`make -C launcher test` and `make -C launcher wine-test`. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the pull request workflow and
[docs/building.md](docs/building.md) for building and releasing the
portable app.
