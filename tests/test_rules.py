"""Scala and Dise delivery rules, evaluated on hand-built metadata."""

import pytest

from helpers.analyzer import analyze_metadata
from helpers.context import PlaybackContext
from helpers.models import Status
from helpers.rules import evaluate_dise, evaluate_scala, highest_status

PASS, INFO, REVIEW, FAIL = Status.PASS, Status.INFO, Status.REVIEW, Status.FAIL

# The app's default player preset, "PC — Scala + Dise".
PC_SCALA_DISE = PlaybackContext(dise_version="general", dise_player="pc")


def rule(result, name):
    matches = [finding for finding in result.findings if finding.rule == name]
    assert matches, f"{result.platform} has no {name!r} finding: {result.findings}"
    assert len(matches) == 1
    return matches[0]


def rules(result):
    return {finding.rule for finding in result.findings}


# Videos ---------------------------------------------------------------------


def test_clean_hd_video_passes_on_default_pc_preset(video_meta):
    report = analyze_metadata(video_meta(), PC_SCALA_DISE)
    assert report.scala.status is PASS
    assert report.dise.status is PASS
    assert report.overall_status is PASS
    # No layout was supplied, so the size is only informational.
    assert rule(report.scala, "Content size").status is INFO


def test_unknown_dise_player_needs_confirmation(video_meta):
    report = analyze_metadata(video_meta(), PlaybackContext())
    assert report.scala.status is PASS
    assert rule(report.dise, "Player details").status is REVIEW
    assert report.overall_status is REVIEW


@pytest.mark.parametrize(
    "profile, level, expected",
    [
        ("Main", 40, PASS),
        ("Constrained Baseline", 31, PASS),
        ("Main", 41, REVIEW),
        ("High", 40, REVIEW),
        ("", None, REVIEW),
    ],
)
def test_soc_players_need_baseline_or_main_up_to_level_4(
    video_meta, profile, level, expected
):
    context = PlaybackContext(platform="dise", dise_version="one", dise_player="soc")
    result = evaluate_dise(video_meta(video_profile=profile, video_level=level), context)
    assert rule(result, "SoC profile").status is expected


def test_pc_players_skip_the_soc_profile_check(video_meta):
    result = evaluate_dise(video_meta(video_profile="High"), PC_SCALA_DISE)
    assert "SoC profile" not in rules(result)


def test_dcp_is_rejected_by_scala(video_meta):
    meta = video_meta(extension=".dcp", format_name="dcp")
    result = evaluate_scala(meta, PC_SCALA_DISE)
    assert rule(result, "Video format").status is FAIL
    assert result.status is FAIL


@pytest.mark.parametrize(
    "engine, expected", [("win32", PASS), ("win64", FAIL), ("unknown", REVIEW)]
)
def test_wmv_depends_on_the_scala_playback_engine(video_meta, engine, expected):
    meta = video_meta(extension=".wmv", video_codec="wmv3", format_name="asf")
    result = evaluate_scala(meta, PlaybackContext(platform="scala", scala_engine=engine))
    assert rule(result, "Container").status is expected
    assert rule(result, "Video codec").status is expected


def test_samsung_4k_video_fails_on_dise_one(video_meta):
    meta = video_meta(width=3840, height=2160)
    one = PlaybackContext(platform="dise", dise_version="one", dise_player="samsung")
    legacy = PlaybackContext(
        platform="dise", dise_version="legacy", dise_player="samsung"
    )
    assert rule(evaluate_dise(meta, one), "Player resolution").status is FAIL
    assert rule(evaluate_dise(meta, legacy), "Player resolution").status is REVIEW


def test_high_bitrate_needs_review(video_meta):
    report = analyze_metadata(video_meta(video_bit_rate=30_000_000), PC_SCALA_DISE)
    assert rule(report.scala, "Video bitrate").status is REVIEW
    assert rule(report.dise, "Video bitrate").status is REVIEW


def test_estimated_bitrate_is_labelled(video_meta):
    meta = video_meta(video_bit_rate_source="estimated from container")
    finding = rule(evaluate_scala(meta, PC_SCALA_DISE), "Video bitrate")
    assert finding.status is PASS
    assert "(estimated average)" in finding.observed
    assert "peaks are not measured" in finding.detail


@pytest.mark.parametrize(
    "rate, expected", [(25.0, PASS), (29.97, PASS), (50.0, REVIEW), (None, REVIEW)]
)
def test_frame_rate_above_30_needs_review(video_meta, rate, expected):
    result = evaluate_scala(video_meta(average_frame_rate=rate), PC_SCALA_DISE)
    assert rule(result, "Frame rate").status is expected


def test_interlaced_video_needs_review(video_meta):
    result = evaluate_scala(video_meta(field_order="tt"), PC_SCALA_DISE)
    assert rule(result, "Scan type").status is REVIEW


@pytest.mark.parametrize(
    "changes",
    [
        {"pixel_format": "yuv420p10le"},
        {"pixel_format": "yuv422p"},
        {"color_transfer": "smpte2084"},
        {"bits_per_raw_sample": 10},
    ],
)
def test_non_sdr_or_non_420_colour_needs_review(video_meta, changes):
    result = evaluate_scala(video_meta(**changes), PC_SCALA_DISE)
    assert rule(result, "Video colour").status is REVIEW


def test_audio_track_is_flagged_for_dise_only(video_meta):
    meta = video_meta(audio_codec="aac", audio_stream_count=1, stream_count=2)
    report = analyze_metadata(meta, PC_SCALA_DISE)
    assert rule(report.dise, "Audio track").status is REVIEW
    assert rule(report.scala, "Audio codec").status is PASS


def test_webm_vp9_is_accepted_by_dise_one_only(video_meta):
    meta = video_meta(extension=".webm", video_codec="vp9", format_name="matroska,webm")
    one_pc = PlaybackContext(platform="dise", dise_version="one", dise_player="pc")
    one_soc = PlaybackContext(platform="dise", dise_version="one", dise_player="soc")
    legacy = PlaybackContext(platform="dise", dise_version="legacy", dise_player="pc")
    assert rule(evaluate_dise(meta, one_pc), "Video format / codec").status is PASS
    assert rule(evaluate_dise(meta, one_soc), "SoC codec").status is REVIEW
    assert rule(evaluate_dise(meta, legacy), "Video format / codec").status is REVIEW


def test_extra_tracks_need_review(video_meta):
    result = evaluate_scala(video_meta(subtitle_stream_count=1), PC_SCALA_DISE)
    assert rule(result, "Extra tracks").status is REVIEW


def test_simultaneous_videos_need_a_player_test(video_meta):
    context = PlaybackContext(
        dise_version="general", dise_player="pc", simultaneous_videos=True
    )
    assert rule(evaluate_dise(video_meta(), context), "Combined playback").status is REVIEW


def test_other_scala_engine_needs_confirmation(video_meta):
    context = PlaybackContext(platform="scala", scala_engine="other")
    assert rule(evaluate_scala(video_meta(), context), "Player details").status is REVIEW


def test_container_that_does_not_match_extension(video_meta):
    result = evaluate_scala(video_meta(format_name="avi"), PC_SCALA_DISE)
    assert rule(result, "File extension").status is REVIEW


# Layout and canvas ------------------------------------------------------------


def test_wide_content_without_a_layout_suggests_multi_screen(video_meta):
    finding = rule(
        evaluate_scala(video_meta(width=5760, height=1080), PC_SCALA_DISE),
        "Content size",
    )
    assert finding.status is REVIEW
    assert "possible 3x1 landscape" in finding.observed


def test_matching_wide_canvas_passes_with_general_pc_bitrate(video_meta):
    context = PlaybackContext(
        dise_version="general", dise_player="pc", canvas_width=5760, canvas_height=1080
    )
    result = evaluate_scala(video_meta(width=5760, height=1080), context)
    assert rule(result, "Content size").status is PASS
    assert rule(result, "Player resolution").status is PASS
    bitrate = rule(result, "Video bitrate")
    assert bitrate.status is PASS
    assert bitrate.expected == "General PC check: up to 20 Mbps"


def test_size_that_differs_from_the_layout_needs_review(video_meta):
    context = PlaybackContext(canvas_width=1920, canvas_height=1080)
    result = evaluate_scala(video_meta(width=1280, height=720), context)
    assert rule(result, "Content size").status is REVIEW


def test_rotation_tag_uses_the_displayed_orientation(video_meta):
    context = PlaybackContext(canvas_width=1080, canvas_height=1920)
    result = evaluate_scala(video_meta(rotation=90), context)
    assert rule(result, "Content size").status is PASS
    assert rule(result, "Rotation").status is REVIEW


# Images, PDFs and other media -----------------------------------------------------


def test_cmyk_jpeg_fails_scala_and_needs_review_on_dise(image_meta):
    meta = image_meta(
        extension=".jpg", video_codec="mjpeg", image_mode="CMYK", pixel_format="cmyk"
    )
    report = analyze_metadata(meta, PC_SCALA_DISE)
    assert rule(report.scala, "Image colour").status is FAIL
    assert rule(report.dise, "Image colour").status is REVIEW
    assert report.overall_status is FAIL


def test_image_with_wrong_extension_needs_review(image_meta):
    result = evaluate_scala(image_meta(video_codec="mjpeg"), PC_SCALA_DISE)
    assert rule(result, "File extension").status is REVIEW


def test_webp_images_need_dise_one(image_meta):
    meta = image_meta(extension=".webp", video_codec="webp")
    one = PlaybackContext(platform="dise", dise_version="one", dise_player="pc")
    assert rule(evaluate_dise(meta, one), "Image format").status is PASS
    assert rule(evaluate_dise(meta, PC_SCALA_DISE), "Image format").status is REVIEW


def test_pdf_is_accepted_through_composer_on_premium_and_lite(pdf_meta):
    context = PlaybackContext(
        dise_version="legacy", dise_player="pc", pdf_workflow="composer"
    )
    report = analyze_metadata(pdf_meta(), context)
    assert rule(report.dise, "PDF workflow").status is PASS
    assert rule(report.scala, "PDF workflow").status is REVIEW


def test_unreadable_media_type_fails(video_meta):
    report = analyze_metadata(video_meta(media_type="unknown"), PC_SCALA_DISE)
    assert rule(report.scala, "Media type").status is FAIL
    assert report.overall_status is FAIL


def test_unselected_platform_is_not_evaluated(video_meta):
    report = analyze_metadata(
        video_meta(video_bit_rate=99_000_000), PlaybackContext(platform="dise")
    )
    assert not report.scala.selected
    assert report.scala.findings == []
    assert report.selected_results == [report.dise]


def test_highest_status_defaults_to_review():
    assert highest_status([]) is REVIEW
