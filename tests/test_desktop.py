"""Smoke tests for the Tk desktop app. Skipped when no display is available."""

import time

import pytest

tk = pytest.importorskip("tkinter")
pytest.importorskip("PIL.ImageTk")

from appearance import compact_filename  # noqa: E402
from desktop import MediaChecker  # noqa: E402
from workflow import Action  # noqa: E402


@pytest.fixture
def root():
    try:
        window = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"No display available: {exc}")
    window.withdraw()
    yield window
    window.destroy()


def start(root, *args):
    app = MediaChecker(root, *args)
    # The app shows a message box for callback errors, which would block a
    # test run; collect them instead.
    errors = []
    root.report_callback_exception = lambda *exc_info: errors.append(exc_info)
    return app, errors


def wait_for_results(root, app, count, timeout=60):
    deadline = time.monotonic() + timeout
    while (app.busy or len(app.results) < count) and time.monotonic() < deadline:
        root.update()
        time.sleep(0.02)
    assert len(app.results) == count, "timed out waiting for the check to finish"


def test_window_starts_empty(root):
    app, errors = start(root)
    root.update()
    assert root.title() == "Pixel Media Checker"
    assert app.file_title.get() == "No files selected"
    assert str(app.details_button.cget("state")) == "disabled"
    assert not errors


def test_opening_a_file_checks_it_and_shows_details(root, make_image):
    app, errors = start(root, make_image("still.png", size=(1920, 1080)))
    wait_for_results(root, app, 1)
    assert app.results[0].action is Action.PASS
    assert app.cards["Overall"].cget("text") == Action.PASS.value
    assert app.status.get() == "Pass: 1"

    app.toggle_details()
    text = app.detail_text.get("1.0", "end")
    assert text.startswith("still.png\nPass")
    assert "File properties" in text
    assert not errors


def test_changing_the_layout_rechecks(root, make_image):
    app, errors = start(root, make_image(size=(1080, 1920)))
    wait_for_results(root, app, 1)
    app.layout.set("HD portrait")
    app.setup_changed()
    wait_for_results(root, app, 1)
    assert app.batch_setup.endswith("HD portrait")
    content_size = [
        finding
        for finding in app.results[0].report.scala.findings
        if finding.rule == "Content size"
    ]
    assert content_size[0].expected == "1080 x 1920"
    assert not errors


def test_compact_filename():
    assert compact_filename("short.mp4") == "short.mp4"
    long_name = "client_campaign_" + "x" * 80 + "_final_v3.mp4"
    compacted = compact_filename(long_name)
    assert len(compacted) == 54
    assert compacted.endswith("x_final_v3.mp4") and "…" in compacted
