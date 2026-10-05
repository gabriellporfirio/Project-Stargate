import pytest

from helpers.context import PlaybackContext


def test_defaults_are_valid_and_cover_both_platforms():
    context = PlaybackContext()
    assert context.includes("scala")
    assert context.includes("dise")
    assert "Scala & Dise" in context.summary()
    assert "Content size: unknown / mixed" in context.summary()


@pytest.mark.parametrize(
    "field, value, message",
    [
        ("platform", "brightsign", "Choose a valid platform."),
        ("scala_engine", "win16", "Choose a valid scala engine."),
        ("dise_version", "beta", "Choose a valid dise version."),
        ("dise_player", "tizen", "Choose a valid dise player."),
        ("pdf_workflow", "print", "Choose a valid pdf workflow."),
    ],
)
def test_rejects_unknown_choices(field, value, message):
    with pytest.raises(ValueError, match=message):
        PlaybackContext(**{field: value})


def test_canvas_needs_both_dimensions():
    with pytest.raises(ValueError, match="both the content width and height"):
        PlaybackContext(canvas_width=1920)


@pytest.mark.parametrize("bad", [0, 65536, -1, 1920.0, True])
def test_canvas_dimensions_must_be_whole_numbers_in_range(bad):
    with pytest.raises(ValueError, match="whole numbers from 1 to 65535"):
        PlaybackContext(canvas_width=bad, canvas_height=1080)


def test_single_platform_only_includes_itself():
    context = PlaybackContext(platform="scala")
    assert context.includes("scala")
    assert not context.includes("dise")
    assert "Dise:" not in context.summary()


def test_summary_lists_optional_settings():
    summary = PlaybackContext(
        canvas_width=5760,
        canvas_height=1080,
        pdf_workflow="composer",
        simultaneous_videos=True,
    ).summary()
    assert "Content size: 5760 x 1080" in summary
    assert "PDF: Composer import" in summary
    assert "Multiple videos playing together" in summary


def test_to_dict_round_trips():
    context = PlaybackContext(platform="dise", dise_version="one", dise_player="lg")
    assert PlaybackContext(**context.to_dict()) == context
