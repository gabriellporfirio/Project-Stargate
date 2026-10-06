"""The version is stated in three places; they must agree."""

import re
from pathlib import Path

from helpers.analyzer import CHECKER_VERSION

LAUNCHER = Path(__file__).resolve().parents[1] / "launcher"


def launcher_version():
    header = (LAUNCHER / "src" / "version.h").read_text()
    return dict(re.findall(r"#define PMC_VERSION_(\w+) (\S+)", header))


def test_launcher_string_matches_its_numbers():
    v = launcher_version()
    numbers = f"{v['MAJOR']}.{v['MINOR']}"
    if v["PATCH"] != "0":
        numbers += f".{v['PATCH']}"
    assert v["STRING"] == f'"{numbers}"'


def test_manifest_matches_launcher():
    v = launcher_version()
    manifest = (LAUNCHER / "launcher.manifest").read_text()
    identity = re.search(r'<assemblyIdentity version="([^"]+)"', manifest).group(1)
    assert identity == f"{v['MAJOR']}.{v['MINOR']}.{v['PATCH']}.0"


def test_app_reports_the_launcher_version():
    assert f'"{CHECKER_VERSION}"' == launcher_version()["STRING"]
