# Launcher

`Pixel Media Checker.exe` is a small native Windows program that starts the
bundled Python runtime on the bundled app. It contains no application logic.

```
Pixel Media Checker.exe
_runtime\pythonw.exe     used for the desktop app (no console window)
_runtime\python.exe      used when the arguments include --check, --version or --runtime-check
_app\app.py
```

## What it does

1. Finds the folder containing the executable.
2. Picks `python.exe` or `pythonw.exe` as above, and checks that it and
   `_app\app.py` exist.
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

4. Runs `"<python>" "<folder>\_app\app.py" <arguments...>` with `_app` as
   the working directory, passing every argument through unchanged.
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
make -C launcher test       # command-line quoting, compiled for the host
make -C launcher wine-test  # needs wine: runs the launcher against a fake python.exe
```

The Wine test checks the interpreter choice, arguments, working directory,
environment and exit codes from the tables above.

## Origin

This source was reconstructed from the shipped 1.2.0 executable. The
version resource and manifest are identical to the original, and the
original and rebuilt executables give identical results in the Wine
behaviour test.
