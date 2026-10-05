# Pixel Media Checker

Desktop and command-line tool that checks video, image, audio and PDF files
against Scala and Dise digital-signage delivery guidelines before content is
scheduled.

The application ships as a portable Windows folder:

```
Pixel Media Checker.exe   native launcher
_app/                     Python application source (this repository's app/)
_runtime/                 embedded Python 3.12 runtime with dependencies
```

This repository holds the source for all three parts. Large binaries (the
Python runtime and `ffprobe.exe`) are not committed; they are assembled at
build time.
