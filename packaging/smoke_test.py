"""Smoke-test a portable build on Windows.

    python packaging/smoke_test.py "dist/Pixel Media Checker"

Checks exit codes through the launcher, and runs the bundled python.exe
directly (with the environment the launcher sets) where output matters.
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

    def launch(*args: str) -> int:
        return subprocess.run([str(launcher), *args], timeout=300, check=False).returncode

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

    with tempfile.TemporaryDirectory(prefix="pmc smoke ") as scratch:
        samples = Path(scratch)
        result = python("-c", SAMPLES, str(samples))
        check("sample files are created", result.returncode == 0, result.stderr)

        result = python("app.py", "--check", str(samples / "clip.mp4"), "--json")
        check("video check runs", result.returncode in (0, 1), result.stdout + result.stderr)
        if result.returncode in (0, 1):
            backend = json.loads(result.stdout)["metadata"]["probe_backend"]
            expected = "ffprobe" if bundled_ffprobe else "PyAV"
            check(f"video is read with {expected}", backend == expected, backend)

        check("launcher --version exits 0", launch("--version") == 0)
        for name, expected in (
            ("still.png", 0),
            ("menu.pdf", 1),
            ("print.jpg", 2),
            ("missing.mp4", 3),
        ):
            code = launch("--check", str(samples / name))
            check(f"launcher --check {name} exits {expected}", code == expected, code)
        code = launch("--check", str(samples / "clip.mp4"))
        check("launcher --check clip.mp4 exits 0 or 1", code in (0, 1), code)

    if FAILURES:
        print("\n".join(["", "Failures:", *FAILURES]), file=sys.stderr)
        return 1
    print("smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
