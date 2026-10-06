# Launcher

`Pixel Media Checker.exe` is a small native Windows program that opens the
desktop app with the bundled Python runtime. It contains no application logic.

```
Pixel Media Checker.exe
_runtime\pythonw.exe     runs the app without a console window
_app\app.py
```

(`_runtime\python.exe` is also in the folder; the app uses it to read files
in a separate process, but the launcher never starts it.)

## What it does

1. Finds the folder containing the executable.
2. Checks that `_runtime\pythonw.exe` and `_app\app.py` exist.
3. Prepares an environment that ignores any other Python on the machine:

   | Variable           | Value                                              |
   | ------------------ | -------------------------------------------------- |
   | `PYTHONHOME`       | `<folder>\_runtime`                                |
   | `PYTHONPATH`       | removed                                            |
   | `PYTHONNOUSERSITE` | `1`                                                |
   | `PYTHONUTF8`       | `1`                                                |
   | `TCL_LIBRARY`      | `<folder>\_runtime\tcl\tcl8.6`                     |
   | `TK_LIBRARY`       | `<folder>\_runtime\tcl\tk8.6`                      |
   | `PATH`             | `<runtime>;<runtime>\DLLs;` + the existing `PATH`  |

4. Runs `"<folder>\_runtime\pythonw.exe" "<folder>\_app\app.py" <arguments...>`
   with `_app` as the working directory, passing every argument through
   unchanged. In practice that is a file dropped onto the launcher or opened
   with it, which the app checks as soon as its window opens.
5. Waits for Python and returns its exit code.

If something goes wrong before Python starts, it shows an error message box
and exits with:

| Code | Meaning                                                            |
| ---- | ------------------------------------------------------------------ |
| 10   | The executable's own location could not be read                   |
| 11   | The executable's folder could not be determined                    |
| 12   | The install path is too long                                       |
| 13   | `_runtime` or `_app` is missing or incomplete                      |
| 14   | Out of memory                                                      |
| 15   | The arguments are too long for one command line                    |
| 16   | Windows could not start Python (the message includes the Windows error code) |

## Building

Requires a MinGW-w64 cross compiler, e.g. on Ubuntu:

```sh
sudo apt-get install gcc-mingw-w64-x86-64 binutils-mingw-w64-x86-64
make -C launcher          # -> launcher/build/launcher.exe
```

The packaging script copies `build/launcher.exe` into the portable folder as
`Pixel Media Checker.exe`. The icon comes from `app/assets/pixel.ico`; the
version is set in `src/version.h` and `launcher.manifest`.

## Tests

```sh
make -C launcher test       # argument quoting, compiled for the host
make -C launcher wine-test  # needs wine: runs the launcher against a fake pythonw.exe
```

The Wine test checks that the launcher always starts `pythonw.exe`, and the
arguments, working directory, environment and exit codes above.

## Origin

This source was reconstructed from the executable that shipped before this
repository existed, and when first added it behaved identically to the
original in the Wine behaviour test. Since then the original's command-line
mode (starting `python.exe` for `--check` and `--version`) has been removed,
because the app is desktop-only. The version resource and manifest otherwise
match the original's.
