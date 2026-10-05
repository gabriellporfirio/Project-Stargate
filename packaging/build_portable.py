"""Assemble the portable Windows build of Pixel Media Checker.

    dist/Pixel Media Checker/
        Pixel Media Checker.exe   launcher (launcher/build/launcher.exe)
        _app/                     app/ from this repository
        _app/tools/ffprobe.exe    downloaded or copied FFmpeg ffprobe
        _runtime/                 Windows CPython 3.12 with requirements.txt installed

The runtime is copied from an installed Windows CPython (the interpreter
running this script by default), so this normally runs on Windows. The
packages are installed as win_amd64 wheels for that Python version.

Example:

    python packaging/build_portable.py --ffprobe C:\\tools\\ffprobe.exe --zip
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_NAME = "Pixel Media Checker"
PYTHON_VERSION = "3.12"

# Parts of a standard Windows CPython install that the app never uses.
SKIPPED_LIB_DIRS = {
    "__pycache__",
    "ensurepip",
    "idlelib",
    "lib2to3",
    "site-packages",
    "test",
    "turtledemo",
    "venv",
}
SKIPPED_TCL_DIRS = {"demos"}


def log(message: str) -> None:
    print(f"[build] {message}", flush=True)


def read_version() -> str:
    header = (ROOT / "launcher" / "src" / "version.h").read_text()
    match = re.search(r'#define PMC_VERSION_STRING "([^"]+)"', header)
    if not match:
        raise SystemExit("PMC_VERSION_STRING not found in launcher/src/version.h")
    return match.group(1)


def copy_tree(source: Path, target: Path, skipped: set[str] = frozenset()) -> None:
    shutil.copytree(
        source,
        target,
        ignore=lambda folder, names: [
            name for name in names if name in skipped or name.endswith((".pyc", ".pyo"))
        ],
    )


def copy_app(target: Path) -> None:
    log("Copying app/ to _app/")
    copy_tree(ROOT / "app", target, skipped={"__pycache__", "tools"})


def copy_runtime(python_home: Path, target: Path) -> None:
    executable = python_home / "python.exe"
    version_dll = python_home / f"python{PYTHON_VERSION.replace('.', '')}.dll"
    if not executable.is_file() or not version_dll.is_file():
        raise SystemExit(
            f"{python_home} is not a Windows CPython {PYTHON_VERSION} install "
            f"(expected python.exe and {version_dll.name})."
        )
    for folder in ("DLLs", "Lib", "tcl"):
        if not (python_home / folder).is_dir():
            raise SystemExit(
                f"{python_home} has no {folder} folder. Use a full python.org-style "
                "install (the embeddable zip has no Tcl/Tk for the desktop app)."
            )

    log(f"Copying the Python runtime from {python_home}")
    target.mkdir(parents=True)
    for item in python_home.iterdir():
        if item.is_file() and (
            item.suffix.lower() == ".dll"
            or item.name.lower() in {"python.exe", "pythonw.exe", "license.txt"}
        ):
            shutil.copy2(item, target / item.name)
    copy_tree(python_home / "DLLs", target / "DLLs")
    copy_tree(python_home / "Lib", target / "Lib", SKIPPED_LIB_DIRS)
    copy_tree(python_home / "tcl", target / "tcl", SKIPPED_TCL_DIRS)
    (target / "Lib" / "site-packages").mkdir()


def install_packages(site_packages: Path) -> None:
    log("Installing requirements.txt into _runtime\\Lib\\site-packages")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-compile",
            "--only-binary=:all:",
            "--platform=win_amd64",
            f"--python-version={PYTHON_VERSION}",
            "--implementation=cp",
            f"--target={site_packages}",
            "--requirement",
            str(ROOT / "requirements.txt"),
        ],
        check=True,
    )
    # Console-script shims are not used by the app.
    shutil.rmtree(site_packages / "bin", ignore_errors=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_ffprobe(url: str, expected_sha256: str, tools: Path) -> None:
    with tempfile.TemporaryDirectory() as scratch:
        archive = Path(scratch) / "ffmpeg.zip"
        log(f"Downloading {url}")
        with urllib.request.urlopen(url, timeout=300) as response, archive.open("wb") as out:
            shutil.copyfileobj(response, out)
        actual = sha256(archive)
        log(f"Archive SHA-256: {actual}")
        if expected_sha256 and actual.lower() != expected_sha256.lower():
            raise SystemExit(f"Checksum mismatch: expected {expected_sha256}, got {actual}")
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
            probe = [name for name in names if name.lower().endswith("bin/ffprobe.exe")]
            if len(probe) != 1:
                raise SystemExit(f"Expected one bin/ffprobe.exe in the archive, found {probe}")
            with bundle.open(probe[0]) as source, (tools / "ffprobe.exe").open("wb") as out:
                shutil.copyfileobj(source, out)
            # Ship FFmpeg's licence beside the binary.
            licences = [
                name
                for name in names
                if name.count("/") == 1 and Path(name).name.upper().startswith("LICENSE")
            ]
            if licences:
                (tools / "FFMPEG-LICENSE.txt").write_bytes(bundle.read(licences[0]))


def add_ffprobe(args: argparse.Namespace, tools: Path) -> None:
    if args.no_ffprobe:
        log("Skipping ffprobe; videos will be read with PyAV only")
        return
    tools.mkdir(parents=True, exist_ok=True)
    if args.ffprobe:
        log(f"Copying {args.ffprobe}")
        shutil.copy2(args.ffprobe, tools / "ffprobe.exe")
    else:
        fetch_ffprobe(args.ffprobe_url, args.ffprobe_sha256, tools)


def make_zip(bundle: Path, version: str) -> Path:
    archive = bundle.parent / f"Pixel-Media-Checker-{version}-win64.zip"
    log(f"Writing {archive.name}")
    archive.unlink(missing_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for path in sorted(bundle.rglob("*")):
            out.write(path, path.relative_to(bundle.parent).as_posix())
    return archive


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--launcher",
        type=Path,
        default=ROOT / "launcher" / "build" / "launcher.exe",
        help="Built launcher executable (default: launcher/build/launcher.exe)",
    )
    parser.add_argument(
        "--python-home",
        type=Path,
        default=Path(sys.base_prefix),
        help="Windows CPython 3.12 install to copy (default: the running interpreter's)",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--ffprobe", type=Path, help="Local ffprobe.exe to bundle")
    source.add_argument("--ffprobe-url", help="FFmpeg Windows build .zip to take ffprobe from")
    source.add_argument(
        "--no-ffprobe", action="store_true", help="Build without ffprobe (PyAV only)"
    )
    parser.add_argument("--ffprobe-sha256", default="", help="Expected SHA-256 of --ffprobe-url")
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="Output folder")
    parser.add_argument("--zip", action="store_true", help="Also write a .zip of the build")
    parser.add_argument(
        "--expect-version",
        default="",
        help="Fail unless the version in launcher/src/version.h matches (a leading v is ignored)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    version = read_version()
    if args.expect_version and args.expect_version.removeprefix("v") != version:
        raise SystemExit(
            f"Version mismatch: building {version}, expected {args.expect_version}. "
            "Update launcher/src/version.h and launcher.manifest."
        )
    if not args.launcher.is_file():
        raise SystemExit(f"Launcher not found: {args.launcher} (run `make -C launcher`)")

    bundle = args.output / BUNDLE_NAME
    if bundle.exists():
        shutil.rmtree(bundle)
    args.output.mkdir(parents=True, exist_ok=True)
    log(f"Building {BUNDLE_NAME} {version} in {bundle}")

    copy_app(bundle / "_app")
    add_ffprobe(args, bundle / "_app" / "tools")
    copy_runtime(args.python_home, bundle / "_runtime")
    install_packages(bundle / "_runtime" / "Lib" / "site-packages")
    shutil.copy2(args.launcher, bundle / f"{BUNDLE_NAME}.exe")

    if args.zip:
        make_zip(bundle, version)
    log("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
