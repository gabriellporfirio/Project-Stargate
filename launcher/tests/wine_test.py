"""Launcher behaviour tests: run build/launcher.exe under Wine with a fake
interpreter and check the command line, working directory, environment and
exit codes it hands to Python.

Run with `make -C launcher wine-test` (needs wine and the MinGW-w64 build).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1] / "build"
FAILURES: list[str] = []


def windows_path(path: Path) -> str:
    """Wine maps the Unix root to drive Z:."""
    return "Z:" + str(path).replace("/", "\\")


class Bundle:
    def __init__(self, root: Path):
        self.root = root / "Pixel Media Checker"
        self.runtime = self.root / "_runtime"
        self.app = self.root / "_app"
        self.runtime.mkdir(parents=True)
        self.app.mkdir()
        shutil.copy(BUILD / "fake_python.exe", self.runtime / "python.exe")
        shutil.copy(BUILD / "fake_pythonw.exe", self.runtime / "pythonw.exe")
        (self.app / "app.py").write_text("# placeholder\n")
        self.exe = self.root / "Pixel Media Checker.exe"
        shutil.copy(BUILD / "launcher.exe", self.exe)

    def run(self, *args: str, **env: str) -> tuple[int, dict[str, str]]:
        report = self.runtime / "report.txt"
        report.unlink(missing_ok=True)
        environment = {key: value for key, value in os.environ.items() if key != "DISPLAY"}
        environment.update(env)
        code = subprocess.run(
            ["wine", str(self.exe), *args], env=environment, timeout=120, check=False
        ).returncode
        values = {}
        if report.exists():
            for line in report.read_text(encoding="utf-8").splitlines():
                key, _, value = line.partition("=")
                values[key] = value
        return code, values


def check(name: str, condition: bool, detail: object = "") -> None:
    print(("ok   " if condition else "FAIL ") + name)
    if not condition:
        FAILURES.append(f"{name}: {detail}")


def argv(report: dict[str, str]) -> list[str]:
    return [report[f"argv{i}"] for i in range(len(report)) if f"argv{i}" in report]


def main() -> int:
    if not shutil.which("wine"):
        print("wine is not installed", file=sys.stderr)
        return 2
    os.environ.setdefault("WINEDEBUG", "-all")
    os.environ.setdefault("WINEDLLOVERRIDES", "mscoree,mshtml=")
    os.environ.setdefault("LANG", "C.UTF-8")
    with tempfile.TemporaryDirectory(prefix="launcher test ") as tmp:
        os.environ["WINEPREFIX"] = str(Path(tmp) / "prefix")
        subprocess.run(["wineboot", "-i"], capture_output=True, timeout=300, check=False)
        bundle = Bundle(Path(tmp))
        runtime, app = windows_path(bundle.runtime), windows_path(bundle.app)
        script = app + "\\app.py"

        code, report = bundle.run(PYTHONPATH="C:\\elsewhere")
        check("desktop launch exits with the app's code", code == 0, code)
        check("desktop launch uses pythonw.exe", report.get("interpreter") == "pythonw.exe", report)
        check(
            "desktop launch runs app.py",
            argv(report) == [runtime + "\\pythonw.exe", script],
            argv(report),
        )
        check("working directory is _app", report.get("cwd") == app, report.get("cwd"))
        check("PYTHONHOME is the runtime", report.get("PYTHONHOME") == runtime)
        check("PYTHONNOUSERSITE is set", report.get("PYTHONNOUSERSITE") == "1")
        check("PYTHONUTF8 is set", report.get("PYTHONUTF8") == "1")
        check("PYTHONPATH is cleared", "PYTHONPATH" not in report, report.get("PYTHONPATH"))
        check("TCL_LIBRARY", report.get("TCL_LIBRARY") == runtime + "\\tcl\\tcl8.6")
        check("TK_LIBRARY", report.get("TK_LIBRARY") == runtime + "\\tcl\\tk8.6")
        check(
            "PATH starts with the runtime and its DLLs",
            report.get("PATH", "").startswith(f"{runtime};{runtime}\\DLLs;"),
            report.get("PATH"),
        )

        # python.exe sits in the runtime too, but the launcher never uses it:
        # whatever the arguments, it opens the desktop app.
        for args in (["C:\\Media\\clip.mp4"], ["--check", "x.png"], ["--version"]):
            _, report = bundle.run(*args)
            check(f"{args} opens the desktop app", report.get("interpreter") == "pythonw.exe", report)

        tricky = [
            "C:\\Media Files\\clip one.mp4",
            'say "hi"',
            "C:\\trailing\\",
            "",
            'a\\"b',
            "Café — menu.pdf",
        ]
        _, report = bundle.run(*tricky)
        check("arguments reach Python unchanged", argv(report)[2:] == tricky, argv(report))

        code, _ = bundle.run(FAKE_EXIT="7")
        check("exit code is passed through", code == 7, code)
        code, _ = bundle.run("C:\\Media\\clip.mp4", FAKE_EXIT="2")
        check("exit code is passed through when a file is opened", code == 2, code)

        (bundle.runtime / "pythonw.exe").rename(bundle.runtime / "pythonw.bak")
        code, report = bundle.run()
        check("missing interpreter exits 13", code == 13 and not report, code)
        (bundle.runtime / "pythonw.bak").rename(bundle.runtime / "pythonw.exe")

        (bundle.app / "app.py").unlink()
        code, report = bundle.run()
        check("missing app.py exits 13", code == 13 and not report, code)

        # Stop Wine before its prefix is deleted with the temporary folder.
        subprocess.run(["wineserver", "-k"], capture_output=True, timeout=60, check=False)

    if FAILURES:
        print("\n".join(["", "Failures:", *FAILURES]), file=sys.stderr)
        return 1
    print("launcher: all behaviour tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
