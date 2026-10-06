# Building the portable app

The app ships as a folder that runs without installing anything:

```
Pixel Media Checker/
├── Pixel Media Checker.exe    launcher      ← launcher/ (C, built with MinGW-w64)
├── _app/                      application   ← app/
│   └── tools/ffprobe.exe      media reader  ← FFmpeg Windows build (downloaded)
└── _runtime/                  Python 3.12   ← copied from a Windows CPython install,
                                               plus requirements.txt
```

Only `app/` and `launcher/` live in git. The Python runtime and ffprobe are
large third-party binaries and are assembled at build time.

## Automated builds (recommended)

The **Release** workflow (`.github/workflows/release.yml`) does everything on
GitHub's runners:

| Trigger | Result |
| --- | --- |
| Pull request touching `packaging/`, `launcher/`, `requirements.txt` or the workflow | Build and smoke test only |
| **Actions → Release → Run workflow** | Build, smoke test, and attach the zip to the run as an artifact (kept 14 days) |
| Push a tag `vX.Y` (e.g. `v1.0`) | Build, smoke test, and publish `Pixel-Media-Checker-X.Y-win64.zip` as a GitHub release |

To cut a release:

1. Versions are `MAJOR.MINOR` (1.0, 1.1, 2.0). Set the new one in all three
   places, which `tests/test_version.py` checks agree:
   `launcher/src/version.h`, the `assemblyIdentity` in
   `launcher/launcher.manifest`, and `CHECKER_VERSION` in
   `app/helpers/analyzer.py` (shown by `--version` and in reports).
2. In `CHANGELOG.md`, move *Unreleased* under the new version with today's
   date (for 1.0, just add the date), and merge to `main`.
3. Tag and push, e.g. `git tag v1.0 && git push origin v1.0`.
   The build fails if the tag does not match `version.h`.

## Building on your own Windows machine

Requirements: 64-bit **Python 3.12** from python.org (the full installer, not
the embeddable zip, because the desktop app needs Tcl/Tk), and the launcher
built as `launcher/build/launcher.exe`. You can download the launcher from
the *Launcher* artifact of any CI run, or build it with MinGW-w64 (MSYS2 or
WSL): `make -C launcher`.

```powershell
py -3.12 packaging\build_portable.py --ffprobe C:\path\to\ffprobe.exe --zip
py -3.12 packaging\smoke_test.py "dist\Pixel Media Checker"
```

Useful options:

- `--ffprobe PATH` bundles an ffprobe.exe you already have.
- `--ffprobe-url URL [--ffprobe-sha256 HASH]` downloads an FFmpeg Windows
  `.zip` and takes `bin/ffprobe.exe` and the licence from it. The workflow
  uses the version-pinned *essentials* build from
  [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
- `--no-ffprobe` builds without ffprobe. Videos are then read with PyAV only.
- `--python-home DIR` copies a different Python 3.12 install than the one
  running the script.

## What the build trims

From the Python install it keeps `python.exe`, `pythonw.exe`, the DLLs,
`DLLs/`, `Lib/` and `tcl/`. It drops the standard-library test suite,
`idlelib`, `ensurepip`, `venv`, `lib2to3`, `turtledemo`, Tk demos, cached
bytecode and anything already in `site-packages`. It then installs the
pinned `requirements.txt` as Windows wheels into `_runtime\Lib\site-packages`.

## Licences

The bundle redistributes the Python runtime (PSF licence, `_runtime\LICENSE.txt`),
Pillow, pypdf and PyAV (licences in their `*.dist-info` folders), and FFmpeg's
ffprobe. The gyan.dev builds are GPL-licensed; the build copies FFmpeg's
licence to `_app\tools\FFMPEG-LICENSE.txt`.
