from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .models import AnalysisReport, MediaMetadata
from .context import PlaybackContext
from .probe import probe_media
from .rules import evaluate_dise, evaluate_scala

CHECKER_VERSION = "1.0"


def analyze_metadata(
    metadata: MediaMetadata, context: PlaybackContext | None = None
) -> AnalysisReport:
    context = context or PlaybackContext()
    return AnalysisReport(
        metadata=metadata,
        scala=evaluate_scala(metadata, context),
        dise=evaluate_dise(metadata, context),
        generated_at=datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        checker_version=CHECKER_VERSION,
        context=context,
    )


def analyze_file(
    path: str | Path, context: PlaybackContext | None = None
) -> AnalysisReport:
    return analyze_metadata(probe_media(path), context)
