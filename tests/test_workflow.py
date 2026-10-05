import logging
from pathlib import Path

import pytest

import workflow
from helpers.analyzer import analyze_metadata
from helpers.context import PlaybackContext
from helpers.models import Finding, Status
from workflow import Action, FileResult, check_files, details, short_message, summary

PC_SCALA_DISE = PlaybackContext(dise_version="general", dise_player="pc")


def result_for(meta, context=PC_SCALA_DISE):
    return FileResult(meta.path, report=analyze_metadata(meta, context))


def test_actions_follow_the_overall_status(video_meta, image_meta):
    assert result_for(video_meta()).action is Action.PASS
    assert result_for(video_meta(field_order="tt")).action is Action.REVIEW
    cmyk = image_meta(extension=".jpg", video_codec="mjpeg", image_mode="CMYK")
    assert result_for(cmyk).action is Action.RETURN
    assert FileResult(Path("x.mp4"), error="Broken").action is Action.ERROR


def test_pass_and_error_reasons(video_meta):
    assert result_for(video_meta()).reason == "No issues found for this setup."
    assert FileResult(Path("x.mp4"), error="Broken").reason == "Broken"
    assert FileResult(Path("x.mp4")).reason == "This file has not been checked."


def test_shared_issues_are_merged_across_platforms(video_meta):
    result = result_for(video_meta(field_order="tt"))
    (platforms, finding), = result.issues
    assert platforms == ["Scala", "Dise"]
    assert finding.rule == "Scan type"
    assert result.reason == "• Request progressive video."


def test_issues_are_sorted_most_severe_first(image_meta):
    meta = image_meta(
        extension=".jpg", video_codec="mjpeg", image_mode="CMYK", pixel_format="cmyk"
    )
    statuses = [finding.status for _, finding in result_for(meta).issues]
    assert statuses == sorted(statuses, reverse=True)
    assert statuses[0] is Status.FAIL


@pytest.mark.parametrize(
    "finding, message",
    [
        (Finding(Status.REVIEW, "Frame rate", "50 fps", ""), "Frame rate: 50 fps. Confirm player support."),
        (Finding(Status.FAIL, "Player resolution", "3840 x 2160", ""), "Request an HD export for Samsung SoC."),
        (Finding(Status.REVIEW, "Player resolution", "5000 x 800", ""), "Size: 5000 x 800. Confirm required resolution."),
        (Finding(Status.REVIEW, "New rule", "odd", "", "Explain it."), "Explain it."),
        (Finding(Status.REVIEW, "New rule", "odd", ""), "Check new rule: odd."),
    ],
)
def test_short_messages(finding, message):
    assert short_message(finding) == message


def test_check_files_keeps_going_after_failures(tmp_path, make_image):
    good = make_image(size=(1920, 1080))
    missing = tmp_path / "missing.png"
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not an image")
    results = list(check_files([good, missing, broken], PC_SCALA_DISE))
    assert [result.path for result in results] == [good, missing, broken]
    assert [result.action for result in results] == [
        Action.PASS,
        Action.ERROR,
        Action.ERROR,
    ]
    assert "cannot be found" in results[1].error


def test_check_files_turns_unexpected_errors_into_messages(monkeypatch, caplog):
    def raise_os_error(path, context):
        raise OSError("network share went away")

    monkeypatch.setattr(workflow, "analyze_file", raise_os_error)
    (result,) = check_files([Path("a.mp4")], PC_SCALA_DISE)
    assert result.error == "Cannot access this file. Try a local copy."

    def raise_bug(path, context):
        raise KeyError("bug")

    monkeypatch.setattr(workflow, "analyze_file", raise_bug)
    with caplog.at_level(logging.ERROR):
        (result,) = check_files([Path("b.mp4")], PC_SCALA_DISE)
    assert result.error.startswith("This file could not be checked.")
    assert "Unexpected inspection failure" in caplog.text


def test_details_lists_issues_and_file_properties(video_meta):
    meta = video_meta(path=Path("promo.mp4"), audio_codec="aac", audio_stream_count=1)
    text = details(result_for(meta))
    assert text.startswith("promo.mp4\nCheck before scheduling\n")
    assert "• Dise · Audio track" in text
    assert "File properties" in text
    assert "Resolution: 1920 x 1080" in text
    assert "Audio codec: aac" in text


def test_summary_covers_every_file(video_meta):
    passed = result_for(video_meta(path=Path("good.mp4")))
    failed = FileResult(Path("bad.mp4"), error="This file is empty.")
    text = summary([passed, failed], "PC — Scala + Dise · HD landscape")
    assert text.splitlines()[0] == "Media check — PC — Scala + Dise · HD landscape"
    assert "good.mp4 — Pass" in text
    assert "bad.mp4 — Could not check\n  This file is empty." in text
