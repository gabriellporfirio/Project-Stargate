"""The entry point the launcher runs: it only ever opens the desktop app."""

import app as entry


def test_opens_the_desktop_app(monkeypatch):
    opened = []
    monkeypatch.setattr(entry, "launch", opened.append)
    monkeypatch.setattr(entry.sys, "argv", ["app.py"])
    assert entry.main() == 0
    assert opened == [None]


def test_checks_a_file_dropped_onto_the_launcher(monkeypatch):
    opened = []
    monkeypatch.setattr(entry, "launch", opened.append)
    monkeypatch.setattr(entry.sys, "argv", ["app.py", r"C:\Media Files\promo clip.mp4"])
    assert entry.main() == 0
    assert opened == [r"C:\Media Files\promo clip.mp4"]
