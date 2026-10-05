"""Shared fixtures: metadata factories and on-the-fly sample media files."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from helpers.models import MediaMetadata

HD_VIDEO = MediaMetadata(
    path=Path("clip.mp4"),
    media_type="video",
    extension=".mp4",
    size_bytes=10_000_000,
    format_name="mov,mp4,m4a,3gp,3g2,mj2",
    duration_seconds=10.0,
    overall_bit_rate=8_000_000,
    probe_backend="ffprobe",
    video_codec="h264",
    video_profile="High",
    video_level=40,
    width=1920,
    height=1080,
    pixel_format="yuv420p",
    average_frame_rate=25.0,
    nominal_frame_rate=25.0,
    video_bit_rate=8_000_000,
    video_bit_rate_source="stream metadata",
    field_order="progressive",
    stream_count=1,
    video_stream_count=1,
)

HD_IMAGE = MediaMetadata(
    path=Path("still.png"),
    media_type="image",
    extension=".png",
    size_bytes=500_000,
    format_name="png",
    format_long_name="PNG",
    probe_backend="Pillow",
    video_codec="png",
    width=1920,
    height=1080,
    pixel_format="rgb24",
    image_mode="RGB",
    stream_count=1,
    video_stream_count=1,
)

PDF_DOCUMENT = MediaMetadata(
    path=Path("menu.pdf"),
    media_type="document",
    extension=".pdf",
    size_bytes=200_000,
    format_name="pdf",
    format_long_name="PDF 1.7",
    probe_backend="pypdf",
    pdf_pages=3,
)


@pytest.fixture
def video_meta():
    """Build video metadata: a clean 1080p25 H.264 MP4 unless overridden."""

    def build(**changes) -> MediaMetadata:
        return replace(HD_VIDEO, **{"probe_notes": [], **changes})

    return build


@pytest.fixture
def image_meta():
    def build(**changes) -> MediaMetadata:
        return replace(HD_IMAGE, **{"probe_notes": [], **changes})

    return build


@pytest.fixture
def pdf_meta():
    def build(**changes) -> MediaMetadata:
        return replace(PDF_DOCUMENT, **{"probe_notes": [], **changes})

    return build


@pytest.fixture
def make_video(tmp_path):
    """Encode a short test video with PyAV (bundles libx264 on every OS)."""
    av = pytest.importorskip("av")

    def build(
        name: str = "sample.mp4",
        *,
        width: int = 320,
        height: int = 240,
        rate: int = 25,
        frames: int = 25,
        codec: str = "libx264",
        audio: bool = False,
    ) -> Path:
        path = tmp_path / name
        with av.open(str(path), "w") as container:
            video = container.add_stream(codec, rate=rate)
            video.width, video.height = width, height
            video.pix_fmt = "yuv420p"
            sound = container.add_stream("aac", rate=48000) if audio else None
            for index in range(frames):
                frame = av.VideoFrame(width, height, "yuv420p")
                for plane in frame.planes:
                    plane.update(bytes([(index * 8) % 256]) * plane.buffer_size)
                frame.pts = index
                frame.time_base = Fraction(1, rate)
                for packet in video.encode(frame):
                    container.mux(packet)
            for packet in video.encode():
                container.mux(packet)
            if sound:
                samples = 1024
                silence = av.AudioFrame(format="fltp", layout="stereo", samples=samples)
                silence.sample_rate = 48000
                for plane in silence.planes:
                    plane.update(bytes(plane.buffer_size))
                total = 48000 * frames // rate
                for start in range(0, total, samples):
                    silence.pts = start
                    for packet in sound.encode(silence):
                        container.mux(packet)
                for packet in sound.encode():
                    container.mux(packet)
        return path

    return build


@pytest.fixture
def make_image(tmp_path):
    """Save a solid-colour image with Pillow."""
    image_module = pytest.importorskip("PIL.Image")

    def build(name: str = "sample.png", *, size=(640, 360), mode="RGB", **save_options):
        path = tmp_path / name
        image_module.new(mode, size).save(path, **save_options)
        return path

    return build


@pytest.fixture
def make_pdf(tmp_path):
    """Write a blank PDF with pypdf."""
    pypdf = pytest.importorskip("pypdf")

    def build(name: str = "sample.pdf", *, pages: int = 1, password: str | None = None):
        writer = pypdf.PdfWriter()
        for _ in range(pages):
            writer.add_blank_page(595, 842)
        if password:
            writer.encrypt(password)
        path = tmp_path / name
        with path.open("wb") as handle:
            writer.write(handle)
        return path

    return build
