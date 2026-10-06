"""Smoke-test a portable build on Windows.

    python packaging/smoke_test.py "dist/Pixel Media Checker"

Checks the bundled runtime and app with the bundled python.exe (in the
environment the launcher sets), then that the launcher opens the desktop app.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SAMPLES = r"""
import sys
from fractions import Fraction
from pathlib import Path

import av
from PIL import Image
from pypdf import PdfWriter

out = Path(sys.argv[1])
Image.new("RGB", (1920, 1080), "white").save(out / "still.png")
Image.new("CMYK", (800, 600)).save(out / "print.jpg")
writer = PdfWriter()
writer.add_blank_page(595, 842)
writer.write(out / "menu.pdf")
with av.open(str(out / "clip.mp4"), "w") as container:
    stream = container.add_stream("libx264", rate=25)
    stream.width, stream.height, stream.pix_fmt = 1280, 720, "yuv420p"
    for index in range(25):
        frame = av.VideoFrame(1280, 720, "yuv420p")
        for plane in frame.planes:
            plane.update(bytes([index * 8]) * plane.buffer_size)
        frame.pts, frame.time_base = index, Fraction(1, 25)
        for packet in stream.encode(frame):
            container.mux(packet)
    for packet in stream.encode():
        container.mux(packet)
"""

RUNTIME_CHECK = r"""
import sys, tkinter, PIL.ImageTk, pypdf, av
print(sys.prefix)
print(tkinter.Tcl().eval("info patchlevel"))
print("\n".join(sys.path))
"""

# Checks files the way the desktop app does, with its default player and layout.
CHECK_FILES = r"""
import json, sys
from pathlib import Path
from presets import DEFAULT_LAYOUT, DEFAULT_PLAYER, make_context
from workflow import check_files

context = make_context(DEFAULT_PLAYER, DEFAULT_LAYOUT)
results = {
    result.path.name: [
        result.action.value,
        result.report.metadata.probe_backend if result.report else "",
    ]
    for result in check_files([Path(arg) for arg in sys.argv[1:]], context)
}
print(json.dumps(results))
"""

DESKTOP = r"""
import tkinter as tk
from desktop import MediaChecker
root = tk.Tk()
MediaChecker(root)
root.update()
root.destroy()
"""

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: object = "") -> None:
    print(("ok   " if condition else "FAIL ") + name, flush=True)
    if not condition:
        FAILURES.append(f"{name}: {detail}")


def main() -> int:
    if os.name != "nt":
        print("The portable build can only be smoke-tested on Windows.", file=sys.stderr)
        return 2
    bundle = Path(sys.argv[1]).resolve()
    launcher = bundle / "Pixel Media Checker.exe"
    runtime = bundle / "_runtime"
    app = bundle / "_app"
    bundled_ffprobe = (app / "tools" / "ffprobe.exe").is_file()

    # The same environment the launcher prepares (see launcher/README.md).
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env.update(
        PYTHONHOME=str(runtime),
        PYTHONNOUSERSITE="1",
        PYTHONUTF8="1",
        TCL_LIBRARY=str(runtime / "tcl" / "tcl8.6"),
        TK_LIBRARY=str(runtime / "tcl" / "tk8.6"),
        PATH=f"{runtime};{runtime / 'DLLs'};{os.environ.get('PATH', '')}",
    )

    def python(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(runtime / "python.exe"), *args],
            cwd=app,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300,
            check=False,
        )

    result = python("-c", RUNTIME_CHECK)
    check("bundled runtime imports tkinter, Pillow, pypdf and PyAV", result.returncode == 0, result.stderr)
    if result.returncode == 0:
        prefix, tcl_version, *path = result.stdout.splitlines()
        check("runtime is self-contained", Path(prefix).resolve() == runtime, prefix)
        check("Tcl/Tk 8.6 is found", tcl_version.startswith("8.6"), tcl_version)
        outside = [entry for entry in path if entry and not Path(entry).resolve().is_relative_to(bundle)]
        check("no packages load from outside the bundle", not outside, outside)

    result = python("-c", DESKTOP)
    check("desktop window builds", result.returncode == 0, result.stderr)

    with tempfile.TemporaryDirectory(prefix="pmc smoke ", ignore_cleanup_errors=True) as scratch:
        samples = Path(scratch)
        result = python("-c", SAMPLES, str(samples))
        check("sample files are created", result.returncode == 0, result.stderr)

        names = ("still.png", "menu.pdf", "print.jpg", "missing.mp4", "clip.mp4")
        result = python("-c", CHECK_FILES, *(str(samples / name) for name in names))
        check("files are checked", result.returncode == 0, result.stderr)
        if result.returncode == 0:
            results = json.loads(result.stdout)
            for name, expected in (
                ("still.png", "Pass"),
                ("menu.pdf", "Check before scheduling"),
                ("print.jpg", "Fail - check with client"),
                ("missing.mp4", "Could not check"),
            ):
                check(f"{name}: {expected}", results[name][0] == expected, results[name])
            action, backend = results["clip.mp4"]
            check(
                "clip.mp4: Pass or Check before scheduling",
                action in ("Pass", "Check before scheduling"),
                action,
            )
            expected = "ffprobe" if bundled_ffprobe else "PyAV"
            check(f"video is read with {expected}", backend == expected, backend)

        # Opened with a file, the launcher starts pythonw.exe and waits while
        # the window is open. A broken bundle makes the app exit at once, and
        # a launcher error shows a dialog without starting pythonw.exe.
        process = subprocess.Popen([str(launcher), str(samples / "clip.mp4")])
        try:
            process.wait(timeout=15)
            check("launcher keeps the desktop app open", False, f"exit code {process.returncode}")
        except subprocess.TimeoutExpired:
            children = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"(Get-CimInstance Win32_Process -Filter 'ParentProcessId={process.pid}').Name",
                ],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            ).stdout.split()
            check("launcher opens the desktop app with pythonw.exe", "pythonw.exe" in children, children)
        finally:
            # Stop the launcher and the app it started.
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True, check=False
            )
            process.wait(timeout=60)

    if FAILURES:
        print("\n".join(["", "Failures:", *FAILURES]), file=sys.stderr)
        return 1
    print("smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
