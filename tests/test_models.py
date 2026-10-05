from pathlib import Path

from helpers.models import AnalysisReport, Finding, PlatformResult, Status


def finding(status):
    return Finding(status, "Rule", "observed", "expected")


def test_status_order_and_labels():
    assert Status.PASS < Status.INFO < Status.REVIEW < Status.FAIL
    assert Status.REVIEW.label == "Review"


def test_finding_serialises_status_name():
    assert finding(Status.FAIL).to_dict()["status"] == "fail"


def test_platform_without_findings_needs_review():
    assert PlatformResult("Scala", []).status is Status.REVIEW


def test_info_findings_do_not_decide_the_status():
    assert PlatformResult("Scala", [finding(Status.INFO)]).status is Status.REVIEW
    result = PlatformResult("Scala", [finding(Status.PASS), finding(Status.INFO)])
    assert result.status is Status.PASS


def test_worst_finding_wins_and_counts_are_reported():
    result = PlatformResult(
        "Dise", [finding(Status.PASS), finding(Status.FAIL), finding(Status.REVIEW)]
    )
    assert result.status is Status.FAIL
    assert result.counts == {"pass": 1, "info": 0, "review": 1, "fail": 1}


def test_unselected_platform_is_reported_as_not_checked():
    result = PlatformResult("Dise", [], selected=False)
    assert result.status_label == "NOT CHECKED"
    assert result.to_dict()["status"] == "not_checked"


def test_rotation_swaps_display_dimensions(video_meta):
    assert video_meta(rotation=90).display_dimensions == (1080, 1920)
    assert video_meta(rotation=180).display_dimensions == (1920, 1080)
    assert video_meta(rotation=270).display_dimensions == (1080, 1920)


def test_resolution_and_serialisation(video_meta):
    assert video_meta().resolution == "1920 x 1080"
    assert video_meta(width=None).resolution == "Not reported"
    assert video_meta(path=Path("a") / "b.mp4").to_dict()["path"] == str(
        Path("a") / "b.mp4"
    )


def test_overall_status_uses_selected_platforms_only(video_meta):
    report = AnalysisReport(
        metadata=video_meta(),
        scala=PlatformResult("Scala", [finding(Status.PASS)]),
        dise=PlatformResult("Dise", [finding(Status.FAIL)], selected=False),
        generated_at="2026-01-01T00:00:00Z",
        checker_version="test",
    )
    assert report.overall_status is Status.PASS
    assert [result.platform for result in report.selected_results] == ["Scala"]
