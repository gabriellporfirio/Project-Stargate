from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging
from helpers.analyzer import analyze_file
from helpers.context import PlaybackContext
from helpers.models import AnalysisReport, Status
from helpers.probe import ProbeError
from helpers.reporting import technical_rows


class Action(str, Enum):
    PASS = "Pass"
    REVIEW = "Check before scheduling"
    RETURN = "Fail - check with client"
    ERROR = "Could not check"


@dataclass(frozen=True)
class FileResult:
    path: Path
    report: AnalysisReport | None = None
    error: str = ""

    @property
    def action(self):
        if self.error or self.report is None:
            return Action.ERROR
        return {Status.PASS: Action.PASS, Status.FAIL: Action.RETURN}.get(
            self.report.overall_status, Action.REVIEW
        )

    @property
    def issues(self):
        found = {}
        if self.report:
            for platform in self.report.selected_results:
                for finding in platform.findings:
                    if finding.status < Status.REVIEW:
                        continue
                    key = (
                        finding.rule,
                        finding.observed,
                        finding.expected,
                        finding.detail,
                        finding.status,
                    )
                    names, _ = found.get(key, ([], finding))
                    found[key] = (names + [platform.platform], finding)
        return sorted(found.values(), key=lambda item: item[1].status, reverse=True)

    @property
    def reason(self):
        if self.action == Action.ERROR:
            return self.error or "This file has not been checked."
        if self.action == Action.PASS:
            return "No issues found for this setup."
        issues = self.issues
        if not issues:
            return "Confirm the setup before scheduling."
        messages = dict.fromkeys(short_message(finding) for _, finding in issues)
        return "\n".join(f"• {message}" for message in messages)


def short_message(finding):
    rule, observed = finding.rule, finding.observed
    messages = {
        "Audio track": "Audio track present; confirm it is needed.",
        "Frame rate": f"Frame rate: {observed}. Confirm player support.",
        "Video bitrate": f"Bitrate: {observed}. Confirm player support.",
        "Content size": "Confirm the layout or request the correct size.",
        "SoC profile": f"Encoding: {observed}. Confirm player support.",
        "SoC codec": "Confirm the player before scheduling.",
        "Player details": "Confirm the player before scheduling.",
        "Image colour": "Request an RGB image.",
        "Video colour": "Check the video colour format.",
        "Rotation": "Check orientation; the file uses a rotation tag.",
        "PDF workflow": "Confirm PDF import, or request images.",
        "Extra tracks": "Extra tracks found; confirm which should play.",
        "Scan type": "Request progressive video.",
    }
    if rule == "Player resolution":
        return (
            "Request an HD export for Samsung SoC."
            if finding.status == Status.FAIL
            else f"Size: {observed}. Confirm required resolution."
        )
    return messages.get(rule, finding.detail or f"Check {rule.lower()}: {observed}.")


def check_files(paths: list[Path], context: PlaybackContext):
    """Yield every file in selection order; keep going after individual failures."""
    for path in paths:
        try:
            yield FileResult(path, report=analyze_file(path, context))
        except ProbeError as error:
            yield FileResult(path, error=str(error))
        except OSError:
            yield FileResult(path, error="Cannot access this file. Try a local copy.")
        except Exception:
            logging.exception("Unexpected inspection failure: %s", path)
            yield FileResult(
                path,
                error="This file could not be checked. Try again or reopen the app.",
            )


def details(result: FileResult):
    lines = [result.path.name, result.action.value, ""]
    issues = result.issues
    if not issues:
        lines.extend([result.reason, ""])
    for platforms, finding in issues:
        lines.extend(
            [
                f"• {' / '.join(platforms)} · {finding.rule}",
                f"  {short_message(finding)}",
                f"  Detected: {finding.observed}",
                f"  Expected: {finding.expected}",
                "",
            ]
        )
    if result.report:
        wanted = {
            "Path",
            "File size",
            "Resolution",
            "Video/image codec",
            "Video profile / level",
            "Frame rate",
            "Video bitrate",
            "Audio codec",
            "PDF pages",
        }
        lines.append("File properties")
        lines.extend(
            f"{name}: {value}"
            for name, value in technical_rows(result.report.metadata)
            if name in wanted
        )
    return "\n".join(lines)


def summary(results, setup):
    lines = [f"Media check — {setup}", ""]
    for result in results:
        lines.append(f"{result.path.name} — {result.action.value}")
        if result.issues:
            lines.extend(
                f"  • {' / '.join(platforms)}: {short_message(finding)} [{finding.observed}]"
                for platforms, finding in result.issues
            )
        elif result.action != Action.PASS:
            lines.append(f"  {result.reason}")
        lines.append("")
    return "\n".join(lines).rstrip()
