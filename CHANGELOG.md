# Changelog

All notable changes are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions are
numbered `MAJOR.MINOR` (1.0, 1.1, 2.0); see
[docs/building.md](docs/building.md#automated-builds-recommended) for where
the version is set.

## [Unreleased]

### Removed

- The command-line mode: `--check`, `--json`, the playback flags and
  `--version`. The app is desktop-only; the launcher always opens the
  desktop window, and a file dropped onto it is checked straight away.
  This also removes the `--runtime-check` usage error listed under 1.0.

## [1.0] - 2026-10-06

The first version: the app as it was already in use, now built from this
repository.

### Features

- Desktop app and `--check` command line for video, image, audio and PDF files.
- Scala and Dise rules for formats, size and layout, bitrate, frame rate,
  SoC encoding profiles, colour, audio and extra tracks.
- Player presets (PC, Dise One and Premium / Lite on PC, SoC, Samsung and LG)
  and multi-screen layouts.

### Repository

- Source for the app, imported from the portable build that was in use.
- Source for the `Pixel Media Checker.exe` launcher, reconstructed from the
  shipped executable and verified to behave identically.
- Automated tests for the analysis engine, CLI, presets, batch workflow,
  desktop app, launcher and version numbers.
- CI on Windows and Linux; a release workflow that builds, smoke-tests and
  publishes the portable zip.
- Documentation: architecture, checks reference, building and releasing.
- `CLAUDE.md` with the project's code, design and process standards, and the
  company design language (`docs/design/`) that the desktop app follows.

### Known issues

- The launcher sends `--runtime-check` to the app, which does not recognise
  it yet; the command exits with a usage error.
