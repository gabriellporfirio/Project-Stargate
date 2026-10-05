from __future__ import annotations

import json

from .models import AnalysisReport, MediaMetadata, PlatformResult


def human_size(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    return f"{value} B"


def human_duration(value: float | None) -> str:
    if value is None:
        return "Not reported"
    minutes, seconds = divmod(value, 60)
    hours, minutes = divmod(int(minutes), 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{seconds:05.2f}"
    return f"{minutes:02d}:{seconds:05.2f}"


def human_bitrate(value: int | None) -> str:
    if value is None:
        return "Not reported"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f} Mbps"
    return f"{value / 1_000:.0f} kbps"


def technical_rows(meta: MediaMetadata) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [
        ("File", meta.filename),
        ("Path", str(meta.path)),
        ("Media type", meta.media_type.title()),
        ("Extension", meta.extension or "None"),
        (
            "Format" if meta.media_type == "document" else "Container",
            meta.format_long_name or meta.format_name or "Not reported",
        ),
        ("File size", human_size(meta.size_bytes)),
        ("Probe backend", meta.probe_backend),
        ("Inspection", meta.inspection),
    ]
    if meta.media_type != "document":
        rows.extend(
            [
                ("Duration", human_duration(meta.duration_seconds)),
                ("Overall bitrate", human_bitrate(meta.overall_bit_rate)),
                ("Streams", str(meta.stream_count)),
            ]
        )
    if meta.media_type in {"video", "image"}:
        rows.extend(
            [
                (
                    "Video/image codec",
                    meta.video_codec_long_name or meta.video_codec or "Not reported",
                ),
                (
                    "Video profile / level",
                    (
                        f"{meta.video_profile or 'Not reported'}@L{meta.video_level / 10:.1f}"
                        if meta.video_level is not None
                        and meta.video_codec in {"h264", "avc", "avc1"}
                        else meta.video_profile or "Not reported"
                    ),
                ),
                ("Resolution", meta.resolution),
                (
                    "Display dimensions",
                    " x ".join(str(x or "?") for x in meta.display_dimensions),
                ),
                ("Rotation", f"{meta.rotation} degrees"),
                ("Pixel format", meta.pixel_format or "Not reported"),
                (
                    "Frame rate",
                    (
                        f"{meta.average_frame_rate:.3f} fps"
                        if meta.average_frame_rate
                        else "Not reported"
                    ),
                ),
                ("Video bitrate", human_bitrate(meta.video_bit_rate)),
                ("Bitrate source", meta.video_bit_rate_source or "Not reported"),
                ("Field order", meta.field_order or "Not reported"),
                ("Colour space", meta.color_space or "Not reported"),
                ("Colour transfer", meta.color_transfer or "Not reported"),
                ("Colour primaries", meta.color_primaries or "Not reported"),
            ]
        )
    if meta.audio_codec or meta.audio_stream_count or meta.media_type == "audio":
        rows.extend(
            [
                (
                    "Audio codec",
                    meta.audio_codec_long_name or meta.audio_codec or "Not reported",
                ),
                ("Audio profile", meta.audio_profile or "Not reported"),
                (
                    "Audio sample rate",
                    (
                        f"{meta.audio_sample_rate} Hz"
                        if meta.audio_sample_rate
                        else "Not reported"
                    ),
                ),
                (
                    "Audio channels",
                    str(meta.audio_channels) if meta.audio_channels else "Not reported",
                ),
                ("Audio layout", meta.audio_channel_layout or "Not reported"),
                ("Audio bitrate", human_bitrate(meta.audio_bit_rate)),
            ]
        )
    if meta.media_type == "document":
        rows.append(("PDF pages", str(meta.pdf_pages or "Unknown")))
    if meta.media_type == "image":
        rows.extend(
            [
                ("Image colour mode", meta.image_mode or "Unknown"),
                ("Image frames", str(meta.image_frames)),
            ]
        )
    return rows


def _platform_lines(result: PlatformResult) -> list[str]:
    lines = [f"{result.platform.upper()}: {result.status_label}", result.note, ""]
    for finding in result.findings:
        lines.append(f"[{finding.status.name}] {finding.rule}")
        lines.append(f"  Detected: {finding.observed}")
        lines.append(f"  Expected: {finding.expected}")
        if finding.detail:
            lines.append(f"  Note: {finding.detail}")
        lines.append("")
    return lines


def format_text_report(report: AnalysisReport) -> str:
    meta = report.metadata
    lines = [
        "MEDIA CHECK REPORT",
        "=" * 72,
        f"Generated: {report.generated_at}",
        f"Checker: v{report.checker_version}",
        f"File: {meta.filename}",
        f"Path: {meta.path}",
        f"Type: {meta.media_type.title()}",
        f"Overall: {report.overall_status.name}",
        f"Playback setup: {report.context.summary()}",
        "",
        "TECHNICAL SUMMARY",
        "-" * 72,
    ]
    lines.extend(f"{key}: {value}" for key, value in technical_rows(meta))
    lines.extend(["", "PLATFORM RESULTS", "-" * 72])
    for result in report.selected_results:
        lines.extend(_platform_lines(result))
    if meta.probe_notes:
        lines.extend(["PROBE NOTES", "-" * 72, *meta.probe_notes, ""])
    lines.extend(
        [
            "INTERPRETATION",
            "-" * 72,
            "PASS = matches the checks for the selected setup.",
            "REVIEW = confirm the setup, adjust the export or test on the player.",
            "FAIL = an explicit restriction applies to the selected setup.",
            "This is a file check. Actual playback, image quality and the complete screen layout still need checking.",
            "",
        ]
    )
    return "\n".join(lines)


def format_json_report(report: AnalysisReport, *, indent: int = 2) -> str:
    return json.dumps(report.to_dict(), indent=indent, ensure_ascii=False)
