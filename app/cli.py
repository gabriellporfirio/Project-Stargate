import argparse
import json
import sys
from helpers.analyzer import CHECKER_VERSION, analyze_file
from helpers.context import (
    PlaybackContext,
    PLATFORMS,
    SCALA_ENGINES,
    DISE_PLAYERS,
    DISE_VERSIONS,
    PDF_WORKFLOWS,
)
from helpers.models import Status
from helpers.probe import ProbeError
from helpers.reporting import format_json_report, format_text_report
from presets import DEFAULT_PLAYER, PLAYERS


def build_parser() -> argparse.ArgumentParser:
    defaults = PLAYERS[DEFAULT_PLAYER]
    parser = argparse.ArgumentParser(
        description="Check a media file against Scala and Dise delivery profiles."
    )
    parser.add_argument("file", nargs="?", help="Open this file in the desktop app")
    parser.add_argument(
        "--check", metavar="FILE", help="Run a headless check and print a report"
    )
    parser.add_argument(
        "--json", action="store_true", help="With --check, output JSON instead of text"
    )
    parser.add_argument("--platform", choices=list(PLATFORMS), default=defaults.platform)
    parser.add_argument(
        "--scala-engine", choices=list(SCALA_ENGINES), default=defaults.scala_engine
    )
    parser.add_argument(
        "--dise-version", choices=list(DISE_VERSIONS), default=defaults.dise_version
    )
    parser.add_argument(
        "--dise-player", choices=list(DISE_PLAYERS), default=defaults.dise_player
    )
    parser.add_argument(
        "--pdf-workflow", choices=list(PDF_WORKFLOWS), default=defaults.pdf_workflow
    )
    parser.add_argument("--size", help="Expected content dimensions, e.g. 5760x1080")
    parser.add_argument(
        "--multi-video", action="store_true", help="Multiple videos play simultaneously"
    )
    parser.add_argument(
        "--version", action="version", version=f"Media Checker {CHECKER_VERSION}"
    )
    return parser


def run_cli(
    path: str, json_output: bool, context: PlaybackContext | None = None
) -> int:
    try:
        report = analyze_file(path, context)
    except ProbeError as exc:
        if json_output:
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    except Exception:
        message = "This file could not be checked."
        if json_output:
            print(json.dumps({"error": message}, indent=2))
        else:
            print(f"ERROR: {message}", file=sys.stderr)
        return 3
    print(format_json_report(report) if json_output else format_text_report(report))
    return {
        Status.PASS: 0,
        Status.REVIEW: 1,
        Status.FAIL: 2,
    }.get(report.overall_status, 3)
