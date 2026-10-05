# Changelog

All notable changes are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/). The version lives in
`launcher/src/version.h`.

## [Unreleased]

### Added

- Source repository for the app, imported from the shipped 1.2.0 portable build.
- Source for the `Pixel Media Checker.exe` launcher, reconstructed from the
  1.2.0 binary and verified to behave identically.
- Automated tests for the analysis engine, CLI, presets, batch workflow,
  desktop app and launcher.
- CI on Windows and Linux; a release workflow that builds, smoke-tests and
  publishes the portable zip.
- Documentation: architecture, checks reference, building and releasing.

### Known issues

- The launcher sends `--runtime-check` to the app, which does not recognise
  it yet; the command exits with a usage error.
- Reports show checker version `1.0` (`CHECKER_VERSION` in
  `app/helpers/analyzer.py`) while the app is 1.2.0.

## [1.2.0]

Baseline: the portable build in use before this repository existed.

- Desktop app and `--check` command line for video, image, audio and PDF files.
- Scala and Dise rules for formats, size and layout, bitrate, frame rate,
  SoC encoding profiles, colour, audio and extra tracks.
- Player presets (PC, Dise One and Premium / Lite on PC, SoC, Samsung and LG)
  and multi-screen layouts.
