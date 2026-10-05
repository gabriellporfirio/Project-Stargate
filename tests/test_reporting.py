import json

import pytest

from helpers.analyzer import analyze_metadata
from helpers.context import PlaybackContext
from helpers.reporting import (
    format_json_report,
    format_text_report,
    human_bitrate,
    human_duration,
    human_size,
    technical_rows,
)


@pytest.mark.parametrize(
    "value, expected",
    [(512, "512 B"), (1536, "1.50 KB"), (5 * 1024**3, "5.00 GB"), (3 * 1024**5, "3072.00 TB")],
)
def test_human_size(value, expected):
    assert human_size(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [(None, "Not reported"), (75.5, "01:15.50"), (3725, "1:02:05.00")],
)
def test_human_duration(value, expected):
    assert human_duration(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [(None, "Not reported"), (500_000, "500 kbps"), (8_000_000, "8.00 Mbps")],
)
def test_human_bitrate(value, expected):
    assert human_bitrate(value) == expected


def test_video_rows_include_profile_level_and_frame_rate(video_meta):
    rows = dict(technical_rows(video_meta()))
    assert rows["Video profile / level"] == "High@L4.0"
    assert rows["Frame rate"] == "25.000 fps"
    assert rows["Resolution"] == "1920 x 1080"
    assert "PDF pages" not in rows


def test_document_rows_skip_stream_details(pdf_meta):
    rows = dict(technical_rows(pdf_meta()))
    assert rows["PDF pages"] == "3"
    assert rows["Format"] == "PDF 1.7"
    assert "Duration" not in rows


def test_audio_rows_appear_when_audio_is_present(video_meta):
    rows = dict(technical_rows(video_meta(audio_codec="aac", audio_sample_rate=48000)))
    assert rows["Audio codec"] == "aac"
    assert rows["Audio sample rate"] == "48000 Hz"


def test_text_report_sections(video_meta):
    report = analyze_metadata(
        video_meta(probe_notes=["Two audio streams."]),
        PlaybackContext(platform="scala"),
    )
    text = format_text_report(report)
    for heading in (
        "MEDIA CHECK REPORT",
        "TECHNICAL SUMMARY",
        "PLATFORM RESULTS",
        "PROBE NOTES",
        "INTERPRETATION",
    ):
        assert heading in text
    assert "Playback setup: Scala only" in text
    assert "SCALA: REVIEW" in text  # the probe note needs review
    assert "DISE:" not in text  # not selected


def test_json_report_structure(video_meta):
    report = analyze_metadata(
        video_meta(), PlaybackContext(dise_version="general", dise_player="pc")
    )
    data = json.loads(format_json_report(report))
    assert data["overall_status"] == "pass"
    assert data["checker_version"] == report.checker_version
    assert data["generated_at"].endswith("Z")
    assert data["context"]["dise_player"] == "pc"
    assert data["metadata"]["video_codec"] == "h264"
    assert set(data["platforms"]) == {"scala", "dise"}
    assert data["platforms"]["dise"]["status"] == "pass"
    assert all(
        finding["status"] in {"pass", "info", "review", "fail"}
        for finding in data["platforms"]["scala"]["findings"]
    )
