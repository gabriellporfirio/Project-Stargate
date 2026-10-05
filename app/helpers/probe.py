from __future__ import annotations

import json
import logging
import math
import os
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from .models import MediaMetadata

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".wmf",
}
VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".wmv",
    ".mkv",
    ".webm",
    ".mpg",
    ".mpeg",
    ".m2v",
    ".ts",
    ".m2ts",
    ".dcp",
}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".wma", ".aac", ".m4a"}
DOCUMENT_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = (
    IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | DOCUMENT_EXTENSIONS
)


class ProbeError(RuntimeError):
    pass


class EngineError(ProbeError):
    pass


def _probe_pdf(path: Path) -> MediaMetadata:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise EngineError(
            "The PDF reader is missing. Extract the complete app folder again."
        ) from exc
    try:
        with path.open("rb") as source:
            reader = PdfReader(source, strict=False)
            if reader.is_encrypted:
                raise ProbeError(
                    "Password-protected PDFs cannot be checked. Save an unlocked copy."
                )
            pages = len(reader.pages)
            if pages < 1:
                raise ProbeError("This PDF has no readable pages.")
            for page in reader.pages:
                _ = page.mediabox
                contents = page.get_contents()
                if contents is not None:
                    contents.get_data()
            version = reader.pdf_header
    except ProbeError:
        raise
    except PermissionError as exc:
        raise ProbeError(
            "This PDF cannot be accessed. Check permissions or try a local copy."
        ) from exc
    except Exception as exc:
        raise ProbeError(
            "This PDF is incomplete or damaged. Export a new copy."
        ) from exc
    return MediaMetadata(
        path=path,
        media_type="document",
        extension=".pdf",
        size_bytes=path.stat().st_size,
        format_name="pdf",
        format_long_name=f"PDF {version.removeprefix('%PDF-')}",
        probe_backend="pypdf",
        pdf_pages=pages,
        inspection="PDF structure and page streams; appearance not rendered",
    )


def _probe_image(path: Path) -> MediaMetadata:
    try:
        from PIL import Image
    except (ImportError, OSError) as exc:
        raise EngineError(
            "The image reader is missing. Extract the complete app folder again."
        ) from exc
    try:
        with Image.open(path) as im:
            fmt = im.format or ""
            width, height = im.size
            mode = im.mode
            frames = getattr(im, "n_frames", 1)
            orientation = im.getexif().get(274, 1)
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            im.load()
        codec = {"JPEG": "mjpeg", "TIFF": "tiff"}.get(fmt, fmt.lower())
        pixel = {
            "RGB": "rgb24",
            "RGBA": "rgba",
            "L": "gray",
            "P": "pal8",
            "CMYK": "cmyk",
        }.get(mode, mode.lower())
        notes = []
        if orientation in {2, 4, 5, 7}:
            notes.append(
                "Image includes an EXIF mirror transform; flatten its orientation before delivery."
            )
        return MediaMetadata(
            path=path,
            media_type="image",
            extension=path.suffix.lower(),
            size_bytes=path.stat().st_size,
            format_name=fmt.lower(),
            format_long_name=fmt,
            probe_backend="Pillow",
            video_codec=codec,
            width=width,
            height=height,
            pixel_format=pixel,
            image_mode=mode,
            image_frames=frames,
            rotation={3: 180, 5: 90, 6: 90, 7: 270, 8: 270}.get(orientation, 0),
            stream_count=1,
            video_stream_count=1,
            probe_notes=notes,
            inspection="Image structure and first frame decoded",
        )
    except ProbeError:
        raise
    except PermissionError as exc:
        raise ProbeError(
            "This image cannot be accessed. Check permissions or try a local copy."
        ) from exc
    except Exception as exc:
        raise ProbeError(
            "This image could not be read. It may be damaged or unsupported."
        ) from exc


def _safe_int(value: Any) -> int | None:
    if value in (None, "", "N/A", 0, "0"):
        return None
    try:
        parsed = int(value)
        return parsed if parsed > 0 else None
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = int(float(value))
            return parsed if parsed > 0 else None
        except (TypeError, ValueError, OverflowError):
            return None


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) and parsed >= 0 else None


def _rate(value: Any) -> float | None:
    if value in (None, "", "0/0", "N/A"):
        return None
    try:
        rate = float(Fraction(str(value)))
    except (ValueError, ZeroDivisionError):
        return None
    return rate if math.isfinite(rate) and rate > 0 else None


def _normalise_profile(value: Any) -> str:
    if value in (None, "", "unknown", "Unknown"):
        return ""
    return str(value)


def _rotation(value: Any) -> int:
    try:
        return round(float(value)) % 360
    except (ValueError, TypeError, OverflowError):
        return 0


def _ffprobe_candidates() -> list[str]:
    executable = "ffprobe.exe" if os.name == "nt" else "ffprobe"
    app_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    candidates = [
        str(app_root / "tools" / executable),
        os.environ.get("PIXEL_FFPROBE", ""),
        shutil.which("ffprobe") or "",
    ]
    return [
        candidate for candidate in candidates if candidate and Path(candidate).is_file()
    ]


def _probe_with_ffprobe(path: Path) -> MediaMetadata:
    candidates = _ffprobe_candidates()
    if not candidates:
        raise EngineError("ffprobe was not found")

    command = [
        candidates[0],
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(path),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except OSError as exc:
        raise EngineError("The media engine could not start.") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProbeError("Reading this file took too long. Try a local copy.") from exc
    if completed.returncode != 0:
        # Native loader failures and process crashes are app failures, not bad media.
        if completed.returncode < 0 or completed.returncode >= 0x80000000:
            raise EngineError(
                "The media engine stopped unexpectedly. Close and reopen the app."
            )
        message = completed.stderr.strip() or "the file could not be parsed"
        raise ProbeError(f"ffprobe reported: {message}")
    try:
        raw = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise EngineError("The media engine returned an incomplete response.") from exc
    return metadata_from_ffprobe(path, raw)


def metadata_from_ffprobe(path: Path, raw: dict[str, Any]) -> MediaMetadata:
    streams = raw.get("streams") or []
    format_data = raw.get("format") or {}
    video_streams = [
        stream
        for stream in streams
        if stream.get("codec_type") == "video"
        and not (stream.get("disposition") or {}).get("attached_pic")
    ]
    audio_streams = [
        stream for stream in streams if stream.get("codec_type") == "audio"
    ]
    video = video_streams[0] if video_streams else {}
    audio = audio_streams[0] if audio_streams else {}
    extension = path.suffix.lower()

    if extension in IMAGE_EXTENSIONS and video:
        media_type = "image"
    elif video:
        media_type = "video"
    elif audio:
        media_type = "audio"
    else:
        media_type = "unknown"

    average_rate = _rate(video.get("avg_frame_rate")) or _rate(
        video.get("r_frame_rate")
    )
    nominal_rate = _rate(video.get("r_frame_rate"))
    variable_rate = None
    if average_rate and nominal_rate:
        variable_rate = abs(average_rate - nominal_rate) > max(
            0.02, nominal_rate * 0.001
        )

    overall_bit_rate = _safe_int(format_data.get("bit_rate"))
    video_bit_rate = _safe_int(video.get("bit_rate"))
    source = "stream metadata" if video_bit_rate else ""
    if not video_bit_rate and media_type == "video" and overall_bit_rate:
        audio_bit_rate = sum(_safe_int(s.get("bit_rate")) or 0 for s in audio_streams)
        video_bit_rate = max(overall_bit_rate - audio_bit_rate, 0) or overall_bit_rate
        source = "estimated from container"

    metadata = MediaMetadata(
        path=path,
        media_type=media_type,
        extension=extension,
        size_bytes=path.stat().st_size,
        format_name=str(format_data.get("format_name") or ""),
        format_long_name=str(format_data.get("format_long_name") or ""),
        duration_seconds=_safe_float(format_data.get("duration")),
        overall_bit_rate=overall_bit_rate,
        probe_backend="ffprobe",
        video_codec=str(video.get("codec_name") or "").lower(),
        video_codec_long_name=str(video.get("codec_long_name") or ""),
        video_profile=_normalise_profile(video.get("profile")),
        video_level=_safe_int(video.get("level")),
        width=_safe_int(video.get("width")),
        height=_safe_int(video.get("height")),
        pixel_format=str(video.get("pix_fmt") or "").lower(),
        average_frame_rate=average_rate,
        nominal_frame_rate=nominal_rate,
        video_bit_rate=video_bit_rate,
        video_bit_rate_source=source,
        field_order=str(video.get("field_order") or "").lower(),
        color_space=str(video.get("color_space") or ""),
        color_transfer=str(video.get("color_transfer") or ""),
        color_primaries=str(video.get("color_primaries") or ""),
        bits_per_raw_sample=_safe_int(video.get("bits_per_raw_sample")),
        audio_codec=str(audio.get("codec_name") or "").lower(),
        audio_codec_long_name=str(audio.get("codec_long_name") or ""),
        audio_profile=_normalise_profile(audio.get("profile")),
        audio_sample_rate=_safe_int(audio.get("sample_rate")),
        audio_channels=_safe_int(audio.get("channels")),
        audio_channel_layout=str(audio.get("channel_layout") or ""),
        audio_bit_rate=_safe_int(audio.get("bit_rate")),
        stream_count=len(streams),
        variable_frame_rate=variable_rate,
        video_stream_count=len(video_streams),
        audio_stream_count=len(audio_streams),
        subtitle_stream_count=sum(s.get("codec_type") == "subtitle" for s in streams),
        rotation=_rotation((video.get("tags") or {}).get("rotate")),
        sample_aspect_ratio=str(video.get("sample_aspect_ratio") or ""),
    )
    for side in video.get("side_data_list", []):
        if "rotation" in side:
            metadata.rotation = _rotation(side["rotation"])
    if len(video_streams) > 1:
        metadata.probe_notes.append(
            f"The file has {len(video_streams)} video streams; only the first was checked."
        )
    if len(audio_streams) > 1:
        metadata.probe_notes.append(
            f"The file has {len(audio_streams)} audio streams; only the first was checked."
        )
    return metadata


def _probe_with_pyav(path: Path) -> MediaMetadata:
    try:
        import av  # type: ignore
    except (ImportError, OSError) as exc:
        raise EngineError("The media engine could not start.") from exc

    try:
        container = av.open(str(path))
    except Exception as exc:  # PyAV exposes several version-specific error classes.
        raise ProbeError(f"PyAV could not parse the file: {exc}") from exc

    try:
        video_streams = [
            s for s in container.streams.video if not (s.disposition.value & 0x400)
        ]
        audio_streams = list(container.streams.audio)
        video = video_streams[0] if video_streams else None
        audio = audio_streams[0] if audio_streams else None
        extension = path.suffix.lower()
        if extension in IMAGE_EXTENSIONS and video:
            media_type = "image"
        elif video:
            media_type = "video"
        elif audio:
            media_type = "audio"
        else:
            media_type = "unknown"

        duration = None
        if container.duration is not None:
            duration = float(container.duration / av.time_base)
        overall_bitrate = _safe_int(getattr(container, "bit_rate", None))

        context = video.codec_context if video else None
        audio_context = audio.codec_context if audio else None
        average_rate = (
            float(video.average_rate) if video and video.average_rate else None
        )
        nominal_rate = float(video.base_rate) if video and video.base_rate else None
        variable_rate = None
        if average_rate and nominal_rate:
            variable_rate = abs(average_rate - nominal_rate) > max(
                0.02, nominal_rate * 0.001
            )

        video_bit_rate = (
            _safe_int(getattr(context, "bit_rate", None)) if context else None
        )
        source = "stream metadata" if video_bit_rate else ""
        audio_bit_rate = (
            _safe_int(getattr(audio_context, "bit_rate", None))
            if audio_context
            else None
        )
        if not video_bit_rate and media_type == "video" and overall_bitrate:
            video_bit_rate = (
                max(overall_bitrate - (audio_bit_rate or 0), 0) or overall_bitrate
            )
            source = "estimated from container"

        pixel_format = ""
        if context and getattr(context, "format", None):
            pixel_format = getattr(context.format, "name", "") or ""
        profile = _normalise_profile(getattr(context, "profile", "")) if context else ""
        audio_profile = (
            _normalise_profile(getattr(audio_context, "profile", ""))
            if audio_context
            else ""
        )

        metadata = MediaMetadata(
            path=path,
            media_type=media_type,
            extension=extension,
            size_bytes=path.stat().st_size,
            format_name=str(getattr(container.format, "name", "") or ""),
            format_long_name=str(getattr(container.format, "long_name", "") or ""),
            duration_seconds=duration,
            overall_bit_rate=overall_bitrate,
            probe_backend="PyAV",
            video_codec=str(
                getattr(getattr(context, "codec", None), "name", "") or ""
            ).lower(),
            video_codec_long_name=str(
                getattr(getattr(context, "codec", None), "long_name", "") or ""
            ),
            video_profile=profile,
            video_level=_safe_int(getattr(context, "level", None)) if context else None,
            width=_safe_int(getattr(context, "width", None)) if context else None,
            height=_safe_int(getattr(context, "height", None)) if context else None,
            pixel_format=pixel_format.lower(),
            average_frame_rate=average_rate,
            nominal_frame_rate=nominal_rate,
            video_bit_rate=video_bit_rate,
            video_bit_rate_source=source,
            audio_codec=str(
                getattr(getattr(audio_context, "codec", None), "name", "") or ""
            ).lower(),
            audio_codec_long_name=str(
                getattr(getattr(audio_context, "codec", None), "long_name", "") or ""
            ),
            audio_profile=audio_profile,
            audio_sample_rate=(
                _safe_int(getattr(audio_context, "sample_rate", None))
                if audio_context
                else None
            ),
            audio_channels=(
                _safe_int(getattr(audio_context, "channels", None))
                if audio_context
                else None
            ),
            audio_channel_layout=str(
                getattr(getattr(audio_context, "layout", None), "name", "") or ""
            ),
            audio_bit_rate=audio_bit_rate,
            stream_count=len(container.streams),
            variable_frame_rate=variable_rate,
            video_stream_count=len(video_streams),
            audio_stream_count=len(audio_streams),
            subtitle_stream_count=len(container.streams.subtitles),
            sample_aspect_ratio=str(getattr(context, "sample_aspect_ratio", "") or ""),
        )
        if metadata.video_codec == "h264" and context:
            metadata.video_level = (
                h264_level(context.extradata or b"") or metadata.video_level
            )
        if video:
            try:
                frame = next(container.decode(video))
            except Exception as exc:
                raise ProbeError(
                    "The first video frame could not be read. Export a new copy."
                ) from exc
            metadata.rotation = int(frame.rotation) % 360
            metadata.field_order = (
                "interlaced" if frame.interlaced_frame else "progressive"
            )
            metadata.color_transfer = {16: "smpte2084", 18: "arib-std-b67"}.get(
                int(context.color_trc), ""
            )
            metadata.bits_per_raw_sample = (
                max((c.bits for c in frame.format.components), default=0) or None
            )
            metadata.inspection = "Metadata and first video frame decoded"
        if len(video_streams) > 1:
            metadata.probe_notes.append(
                f"The file has {len(video_streams)} video streams; only the first was checked."
            )
        if len(audio_streams) > 1:
            metadata.probe_notes.append(
                f"The file has {len(audio_streams)} audio streams; only the first was checked."
            )
        return metadata
    finally:
        container.close()


def h264_level(extra: bytes) -> int | None:
    """Read level_idc from AVC configuration or an Annex-B SPS, without decoding."""
    if len(extra) >= 4 and extra[0] == 1:
        return extra[3] or None
    import re

    for nal in re.split(b"\x00\x00(?:\x00)?\x01", extra):
        if len(nal) >= 4 and nal[0] & 31 == 7:
            return nal[3] or None
    return None


def _isolated_reader(path: Path, reader: str) -> MediaMetadata:
    # Keep native crashes and slow/damaged PDFs or images outside the desktop app.
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        executable = executable.with_name("python.exe")
    try:
        r = subprocess.run(
            [str(executable), "-m", "helpers.probe", "--worker", reader, str(path)],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        data = json.loads(r.stdout)
        if "error" in data:
            raise (EngineError if data.get("engine") else ProbeError)(data["error"])
        if r.returncode != 0:
            raise EngineError(
                "The file reader stopped unexpectedly. Close and reopen the app."
            )
        data["path"] = Path(data["path"])
        return MediaMetadata(**data)
    except subprocess.TimeoutExpired as exc:
        raise ProbeError("Reading this file took too long. Try a local copy.") from exc
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise EngineError(
            "The file reader could not start or stopped unexpectedly. Close and reopen the app."
        ) from exc


def _isolated_pyav(path: Path) -> MediaMetadata:
    return _isolated_reader(path, "video")


def probe_media(path: str | Path) -> MediaMetadata:
    try:
        resolved = Path(path).expanduser().resolve()
        if not resolved.exists():
            raise ProbeError(
                "The file cannot be found. Check the location or choose it again."
            )
        if not resolved.is_file():
            raise ProbeError("Please select a file, not a folder.")
        size = resolved.stat().st_size
        with resolved.open("rb") as source:
            source.read(1)
    except PermissionError as exc:
        raise ProbeError(
            "This file cannot be accessed. Check permissions or try a local copy."
        ) from exc
    except OSError as exc:
        raise ProbeError(
            "This file is unavailable. Download it fully or try a local copy."
        ) from exc

    extension = resolved.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ProbeError("This file type is not supported.")
    if size == 0:
        raise ProbeError("This file is empty. Please choose a complete copy.")
    if extension == ".pdf":
        return _isolated_reader(resolved, "pdf")
    if extension in IMAGE_EXTENSIONS - {".wmf"}:
        return _isolated_reader(resolved, "image")

    failures = []
    try:
        metadata = _probe_with_ffprobe(resolved)
        if metadata.media_type == "unknown":
            raise ProbeError("No readable media was found.")
        return metadata
    except Exception as exc:
        logging.getLogger(__name__).warning("Primary inspection failed: %s", exc)
        failures.append(exc)
    try:
        metadata = _isolated_pyav(resolved)
        if metadata.media_type == "unknown":
            raise ProbeError("No readable media was found.")
        return metadata
    except Exception as exc:
        logging.getLogger(__name__).warning("Fallback inspection failed: %s", exc)
        failures.append(exc)
    if all(isinstance(e, EngineError) for e in failures):
        raise EngineError(
            "The media engine could not start. Extract a fresh copy of the complete app folder."
        )
    raise ProbeError("This file could not be read. It may be damaged or unsupported.")


if __name__ == "__main__" and len(sys.argv) == 4 and sys.argv[1] == "--worker":
    try:
        readers = {"video": _probe_with_pyav, "image": _probe_image, "pdf": _probe_pdf}
        print(
            json.dumps(
                readers[sys.argv[2]](Path(sys.argv[3])).to_dict(), ensure_ascii=True
            )
        )
    except Exception as exc:
        print(json.dumps({"error": str(exc), "engine": isinstance(exc, EngineError)}))
        raise SystemExit(3)
