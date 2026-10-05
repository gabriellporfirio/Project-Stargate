from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any
from .context import PlaybackContext


class Status(IntEnum):

    PASS = 0
    INFO = 1
    REVIEW = 2
    FAIL = 3

    @property
    def label(self) -> str:
        return self.name.title()


@dataclass(frozen=True)
class Finding:
    status: Status
    rule: str
    observed: str
    expected: str
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["status"] = self.status.name.lower()
        return result


@dataclass
class MediaMetadata:
    path: Path
    media_type: str
    extension: str
    size_bytes: int
    format_name: str = ""
    format_long_name: str = ""
    duration_seconds: float | None = None
    overall_bit_rate: int | None = None
    probe_backend: str = ""

    video_codec: str = ""
    video_codec_long_name: str = ""
    video_profile: str = ""
    video_level: int | None = None
    width: int | None = None
    height: int | None = None
    pixel_format: str = ""
    average_frame_rate: float | None = None
    nominal_frame_rate: float | None = None
    video_bit_rate: int | None = None
    video_bit_rate_source: str = ""
    field_order: str = ""
    color_space: str = ""
    color_transfer: str = ""
    color_primaries: str = ""
    bits_per_raw_sample: int | None = None

    audio_codec: str = ""
    audio_codec_long_name: str = ""
    audio_profile: str = ""
    audio_sample_rate: int | None = None
    audio_channels: int | None = None
    audio_channel_layout: str = ""
    audio_bit_rate: int | None = None

    stream_count: int = 0
    variable_frame_rate: bool | None = None
    probe_notes: list[str] = field(default_factory=list)
    video_stream_count: int = 0
    audio_stream_count: int = 0
    subtitle_stream_count: int = 0
    rotation: int = 0
    sample_aspect_ratio: str = ""
    image_mode: str = ""
    image_frames: int = 1
    pdf_pages: int | None = None
    inspection: str = "metadata"

    @property
    def display_dimensions(self) -> tuple[int | None, int | None]:
        return (
            (self.height, self.width)
            if self.rotation % 180
            else (self.width, self.height)
        )

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def resolution(self) -> str:
        if self.width and self.height:
            return f"{self.width} x {self.height}"
        return "Not reported"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["path"] = str(self.path)
        return result


@dataclass
class PlatformResult:
    platform: str
    findings: list[Finding]
    note: str = ""
    selected: bool = True

    @property
    def status_label(self) -> str:
        return self.status.name if self.selected else "NOT CHECKED"

    @property
    def status(self) -> Status:
        if not self.findings:
            return Status.REVIEW
        actionable = [
            finding.status
            for finding in self.findings
            if finding.status is not Status.INFO
        ]
        return max(actionable, default=Status.REVIEW)

    @property
    def counts(self) -> dict[str, int]:
        return {
            name: sum(
                1 for finding in self.findings if finding.status.name.lower() == name
            )
            for name in ("pass", "info", "review", "fail")
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "status": self.status.name.lower() if self.selected else "not_checked",
            "selected": self.selected,
            "counts": self.counts,
            "note": self.note,
            "findings": [finding.to_dict() for finding in self.findings],
        }


@dataclass
class AnalysisReport:
    metadata: MediaMetadata
    scala: PlatformResult
    dise: PlatformResult
    generated_at: str
    checker_version: str
    context: PlaybackContext = field(default_factory=PlaybackContext)

    @property
    def selected_results(self) -> list[PlatformResult]:
        return [result for result in (self.scala, self.dise) if result.selected]

    @property
    def overall_status(self) -> Status:
        return max(
            (result.status for result in self.selected_results), default=Status.REVIEW
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "checker_version": self.checker_version,
            "generated_at": self.generated_at,
            "overall_status": self.overall_status.name.lower(),
            "context": self.context.to_dict(),
            "metadata": self.metadata.to_dict(),
            "platforms": {
                "scala": self.scala.to_dict(),
                "dise": self.dise.to_dict(),
            },
        }
