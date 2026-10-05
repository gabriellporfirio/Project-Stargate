"""File readers: ffprobe JSON parsing, isolated workers and error handling."""

import os
from pathlib import Path

import pytest

from helpers import probe
from helpers.analyzer import CHECKER_VERSION, analyze_file
from helpers.probe import EngineError, ProbeError, metadata_from_ffprobe, probe_media

needs_ffprobe = pytest.mark.skipif(
    not probe._ffprobe_candidates(), reason="ffprobe is not installed"
)


# Value parsing ---------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [("1200", 1200), (3.9, 3), ("2.5e6", 2_500_000), ("N/A", None), (0, None), (-5, None), ("x", None)],
)
def test_safe_int(value, expected):
    assert probe._safe_int(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [("30000/1001", pytest.approx(29.97, abs=0.01)), ("25/1", 25.0), ("0/0", None), ("1/0", None), (None, None)],
)
def test_rate(value, expected):
    assert probe._rate(value) == expected


@pytest.mark.parametrize("value, expected", [("-90", 270), (90.4, 90), ("bad", 0), (None, 0)])
def test_rotation(value, expected):
    assert probe._rotation(value) == expected


def test_h264_level_from_avcc_and_annex_b():
    assert probe.h264_level(bytes([1, 0x64, 0, 40, 0xFF])) == 40
    assert probe.h264_level(b"\x00\x00\x00\x01\x67\x4d\x00\x1f\xaa") == 31
    assert probe.h264_level(b"") is None


# ffprobe JSON ------------------------------------------------------------------


def ffprobe_json(**format_overrides):
    return {
        "format": {
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "format_long_name": "QuickTime / MOV",
            "duration": "10.000000",
            "bit_rate": "8192000",
            **format_overrides,
        },
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "H264",
                "profile": "High",
                "level": 40,
                "width": 1920,
                "height": 1080,
                "pix_fmt": "yuv420p",
                "avg_frame_rate": "24000/1001",
                "r_frame_rate": "30/1",
                "side_data_list": [{"rotation": -90}],
            },
            {"codec_type": "audio", "codec_name": "aac", "bit_rate": "128000", "channels": 2},
            {"codec_type": "audio", "codec_name": "aac", "bit_rate": "64000"},
            {"codec_type": "video", "codec_name": "mjpeg", "disposition": {"attached_pic": 1}},
            {"codec_type": "subtitle", "codec_name": "mov_text"},
        ],
    }


def test_metadata_from_ffprobe(tmp_path):
    path = tmp_path / "clip.mp4"
    path.write_bytes(b"\0" * 10)
    meta = metadata_from_ffprobe(path, ffprobe_json())
    assert meta.media_type == "video"
    assert meta.video_codec == "h264"
    assert (meta.width, meta.height, meta.rotation) == (1920, 1080, 270)
    assert meta.variable_frame_rate is True
    assert meta.average_frame_rate == pytest.approx(23.976, abs=0.001)
    # Cover art is not a video stream; both audio streams are counted.
    assert (meta.video_stream_count, meta.audio_stream_count) == (1, 2)
    assert meta.subtitle_stream_count == 1
    # No stream bitrate: estimated from the container minus all audio.
    assert meta.video_bit_rate == 8_192_000 - 192_000
    assert meta.video_bit_rate_source == "estimated from container"
    assert meta.probe_notes == [
        "The file has 2 audio streams; only the first was checked."
    ]
    assert meta.size_bytes == 10


@pytest.mark.parametrize(
    "name, streams, expected",
    [
        ("still.png", [{"codec_type": "video", "codec_name": "png"}], "image"),
        ("song.mp3", [{"codec_type": "audio", "codec_name": "mp3"}], "audio"),
        ("empty.mp4", [{"codec_type": "data"}], "unknown"),
    ],
)
def test_media_type_detection(tmp_path, name, streams, expected):
    path = tmp_path / name
    path.write_bytes(b"\0")
    assert metadata_from_ffprobe(path, {"streams": streams}).media_type == expected


# probe_media input validation --------------------------------------------------


def test_missing_file(tmp_path):
    with pytest.raises(ProbeError, match="cannot be found"):
        probe_media(tmp_path / "nope.mp4")


def test_folder_is_rejected(tmp_path):
    folder = tmp_path / "folder.mp4"
    folder.mkdir()
    with pytest.raises(ProbeError, match="not a folder"):
        probe_media(folder)


def test_unsupported_extension(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello")
    with pytest.raises(ProbeError, match="not supported"):
        probe_media(path)


def test_empty_file(tmp_path):
    path = tmp_path / "blank.mp4"
    path.touch()
    with pytest.raises(ProbeError, match="empty"):
        probe_media(path)


# Images (Pillow, isolated worker) ----------------------------------------------


def test_png_is_read_in_a_worker(make_image):
    meta = probe_media(make_image("logo.png", size=(640, 360), mode="RGBA"))
    assert meta.media_type == "image"
    assert meta.probe_backend == "Pillow"
    assert (meta.width, meta.height) == (640, 360)
    assert (meta.image_mode, meta.pixel_format) == ("RGBA", "rgba")
    assert isinstance(meta.path, Path)


def test_cmyk_jpeg(make_image):
    meta = probe_media(make_image("print.jpg", mode="CMYK"))
    assert (meta.video_codec, meta.image_mode) == ("mjpeg", "CMYK")


def test_exif_orientation_sets_rotation(make_image):
    from PIL import Image

    exif = Image.Exif()
    exif[274] = 6  # rotate 90 degrees clockwise
    meta = probe_media(make_image("phone.jpg", size=(400, 300), exif=exif))
    assert meta.rotation == 90
    assert meta.display_dimensions == (300, 400)


def test_damaged_image(tmp_path):
    path = tmp_path / "broken.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\nnot really a png")
    with pytest.raises(ProbeError, match="could not be read"):
        probe_media(path)


# PDFs (pypdf, isolated worker) ----------------------------------------------------


def test_pdf_pages(make_pdf):
    meta = probe_media(make_pdf(pages=2))
    assert meta.media_type == "document"
    assert meta.probe_backend == "pypdf"
    assert meta.pdf_pages == 2
    assert meta.format_long_name.startswith("PDF ")


def test_encrypted_pdf(make_pdf):
    with pytest.raises(ProbeError, match="Password-protected"):
        probe_media(make_pdf(password="secret"))


def test_damaged_pdf(tmp_path):
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"%PDF-1.7\nthis is not a pdf body")
    with pytest.raises(ProbeError, match="incomplete or damaged"):
        probe_media(path)


# Video and audio (ffprobe first, PyAV fallback) ---------------------------------


@needs_ffprobe
def test_video_through_ffprobe(make_video):
    meta = probe_media(make_video(width=320, height=240, rate=25, audio=True))
    assert meta.probe_backend == "ffprobe"
    assert meta.media_type == "video"
    assert meta.video_codec == "h264"
    assert (meta.width, meta.height) == (320, 240)
    assert meta.average_frame_rate == pytest.approx(25.0)
    assert meta.audio_codec == "aac"
    assert meta.duration_seconds == pytest.approx(1.0, abs=0.1)


def test_pyav_fallback_when_ffprobe_is_missing(make_video, monkeypatch):
    monkeypatch.setattr(probe, "_ffprobe_candidates", lambda: [])
    meta = probe_media(make_video(width=320, height=240))
    assert meta.probe_backend == "PyAV"
    assert meta.video_codec == "h264"
    assert (meta.width, meta.height) == (320, 240)
    assert meta.video_level  # read from the AVC configuration record
    assert meta.field_order == "progressive"
    assert meta.inspection == "Metadata and first video frame decoded"


def test_unreadable_video_reports_a_probe_error(tmp_path):
    path = tmp_path / "corrupt.mp4"
    path.write_bytes(b"\0\0\0\x18ftypmp42" + b"\xde\xad" * 64)
    with pytest.raises(ProbeError) as raised:
        probe_media(path)
    assert not isinstance(raised.value, EngineError)


def test_missing_engines_are_reported_as_engine_errors(tmp_path, monkeypatch):
    path = tmp_path / "clip.mp4"
    path.write_bytes(b"\0" * 32)

    def no_engine(_path):
        raise EngineError("missing")

    monkeypatch.setattr(probe, "_probe_with_ffprobe", no_engine)
    monkeypatch.setattr(probe, "_isolated_pyav", no_engine)
    with pytest.raises(EngineError, match="Extract a fresh copy"):
        probe_media(path)


def test_ffprobe_lookup_order(tmp_path, monkeypatch):
    """Bundled _app/tools first, then PIXEL_FFPROBE, then PATH."""
    name = "ffprobe.exe" if os.name == "nt" else "ffprobe"
    bundled = Path(probe.__file__).resolve().parents[1] / "tools" / name
    from_env = tmp_path / name
    from_env.write_text("")
    monkeypatch.setenv("PIXEL_FFPROBE", str(from_env))
    monkeypatch.setattr(probe.shutil, "which", lambda _name: None)
    expected = [str(bundled)] if bundled.is_file() else []
    assert probe._ffprobe_candidates() == expected + [str(from_env)]


# analyze_file -----------------------------------------------------------------


def test_analyze_file_end_to_end(make_image):
    report = analyze_file(make_image(size=(1920, 1080)))
    assert report.checker_version == CHECKER_VERSION
    assert report.generated_at.endswith("Z")
    assert report.metadata.media_type == "image"
    assert {result.platform for result in report.selected_results} == {"Scala", "Dise"}
