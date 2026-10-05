"""The command-line entry point, run the way the launcher runs it."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import cli
from presets import DEFAULT_PLAYER, PLAYERS

APP = Path(__file__).resolve().parents[1] / "app" / "app.py"


def run_app(*args):
    # The launcher always sets PYTHONUTF8=1 before starting app.py.
    return subprocess.run(
        [sys.executable, str(APP), *map(str, args)],
        env={**os.environ, "PYTHONUTF8": "1"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )


def test_version():
    result = run_app("--version")
    assert result.returncode == 0
    assert result.stdout.strip() == "Media Checker 1.0"


def test_parser_defaults_follow_the_default_preset():
    args = cli.build_parser().parse_args([])
    preset = PLAYERS[DEFAULT_PLAYER]
    assert (args.platform, args.dise_version, args.dise_player) == (
        preset.platform,
        preset.dise_version,
        preset.dise_player,
    )
    assert args.check is None and args.file is None


def test_passing_file_exits_0_with_json(make_image):
    result = run_app("--check", make_image(size=(1920, 1080)), "--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["overall_status"] == "pass"
    assert report["context"]["dise_player"] == "pc"


def test_review_exits_1(make_pdf):
    result = run_app("--check", make_pdf())
    assert result.returncode == 1
    assert "Overall: REVIEW" in result.stdout


def test_fail_exits_2(make_image):
    result = run_app("--check", make_image("print.jpg", mode="CMYK"))
    assert result.returncode == 2
    assert "Overall: FAIL" in result.stdout


def test_playback_flags_are_applied(make_image):
    result = run_app(
        "--check",
        make_image(size=(1080, 1920)),
        "--json",
        "--platform",
        "dise",
        "--dise-version",
        "one",
        "--dise-player",
        "lg",
        "--size",
        "1080x1920",
        "--multi-video",
    )
    report = json.loads(result.stdout)
    assert report["context"] == {
        "platform": "dise",
        "scala_engine": "unknown",
        "dise_version": "one",
        "dise_player": "lg",
        "canvas_width": 1080,
        "canvas_height": 1920,
        "pdf_workflow": "unknown",
        "simultaneous_videos": True,
    }
    assert report["platforms"]["scala"]["status"] == "not_checked"


@pytest.mark.parametrize("size", ["wide", "1920", "0x1080", "1920x1080x2"])
def test_invalid_size_exits_3_with_json_error(make_image, size):
    result = run_app("--check", make_image(), "--size", size)
    assert result.returncode == 3
    assert "WIDTHxHEIGHT" in json.loads(result.stdout)["error"]


def test_missing_file_exits_3(tmp_path):
    missing = tmp_path / "missing.mp4"
    as_json = run_app("--check", missing, "--json")
    assert as_json.returncode == 3
    assert "cannot be found" in json.loads(as_json.stdout)["error"]
    as_text = run_app("--check", missing)
    assert as_text.returncode == 3
    assert as_text.stderr.startswith("ERROR: ")


def test_unexpected_errors_are_reported_without_a_traceback(monkeypatch, capsys):
    def explode(path, context):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli, "analyze_file", explode)
    assert cli.run_cli("anything.mp4", json_output=True) == 3
    assert json.loads(capsys.readouterr().out) == {
        "error": "This file could not be checked."
    }
