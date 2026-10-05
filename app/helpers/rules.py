from __future__ import annotations

import math
from collections.abc import Iterable
from .context import PlaybackContext, SCALA_ENGINES, DISE_PLAYERS, DISE_VERSIONS
from .models import Finding, MediaMetadata, PlatformResult, Status

DISE_SOURCE = (
    "Dise Media Format Guidelines, 15 July 2026; Premium & Lite, 29 April 2025"
)
SCALA_SOURCE = "Scala Creating Content Guidelines, Content Manager 13.60"
H264_NAMES = {"h264", "avc", "avc1"}
H265_NAMES = {"hevc", "h265", "hev1", "hvc1"}
MPEG2_NAMES = {"mpeg2video", "mpeg2"}
AAC_NAMES = {"aac", "aac_latm"}
PASS, INFO, REVIEW, FAIL = Status.PASS, Status.INFO, Status.REVIEW, Status.FAIL
GENERAL_PC_BITRATE_LIMIT = 20_000_000


def _finding(status, rule, observed, expected, detail=""):
    return Finding(status, rule, str(observed), expected, detail)


def _fmt_bitrate(value):
    return "Not reported" if not value else f"{value / 1_000_000:.2f} Mbps"


def _fmt_profile_level(profile, level):
    # AVC level_idc is in tenths. HEVC levels use a different scale.
    return (
        f'{profile or "Unknown"}@L{level / 10:.1f}'
        if level
        else profile or "Not reported"
    )


def _is_within_4k(w, h):
    return bool(w and h and max(w, h) <= 3840 and min(w, h) <= 2160)


def _is_within_1080p(w, h):
    return bool(w and h and max(w, h) <= 1920 and min(w, h) <= 1080)


def _wide_canvas_layout(w, h):
    if not w or not h:
        return None
    # Suggestions only: aspect ratio cannot identify a client's real layout.
    for count in (2, 3, 4):
        for ratio, label in (
            (16 / 9 * count, f"{count}x1 landscape"),
            (9 / 16 * count, f"{count}x1 portrait"),
            (16 / 9 / count, f"1x{count} landscape"),
            (9 / 16 / count, f"1x{count} portrait"),
        ):
            if abs(w / h - ratio) <= ratio * 0.015:
                return label
    return None


def _matches_layout(meta, ctx):
    """The selected canvas defines the expected size for every player profile."""
    return ctx.canvas_width is not None and meta.display_dimensions == (
        ctx.canvas_width,
        ctx.canvas_height,
    )


def _layout(meta, ctx):
    w, h = meta.display_dimensions
    if not w or not h:
        return _finding(REVIEW, "Content size", "Not reported", "Readable dimensions")
    if ctx.canvas_width is not None:
        expected = f"{ctx.canvas_width} x {ctx.canvas_height}"
        if _matches_layout(meta, ctx):
            return _finding(
                PASS,
                "Content size",
                f"{w} x {h}",
                expected,
                "Matches the requested content size.",
            )
        return _finding(
            REVIEW,
            "Content size",
            f"{w} x {h}",
            expected,
            "Size differs; confirm cropping, scaling or the correct export.",
        )
    possible = _wide_canvas_layout(w, h)
    if possible:
        return _finding(
            REVIEW,
            "Content size",
            f"{w} x {h} (possible {possible})",
            "Confirmed client layout",
            "Looks like multi-screen content; check the client configuration.",
        )
    return _finding(
        INFO,
        "Content size",
        f"{w} x {h}",
        "Client content size not supplied",
        "Size has not been matched to the client layout.",
    )


def _frame_rate_finding(rate):
    if not rate or not math.isfinite(rate) or rate <= 0:
        return _finding(REVIEW, "Frame rate", "Not reported", "30 fps or below")
    return _finding(
        PASS if rate <= 30 else REVIEW,
        "Frame rate",
        f"{rate:.3f}".rstrip("0").rstrip(".") + " fps",
        "30 fps or below",
        "" if rate <= 30 else "May need a more powerful player.",
    )


def _scala_bitrate_profile(w, h):
    if not w or not h:
        return None
    for width, height, name, text, limit in (
        (1280, 720, "720p", "8–12 Mbps", 12_000_000),
        (1920, 1080, "1080p", "16–20 Mbps", 20_000_000),
        (3840, 2160, "4K", "30–40 Mbps", 40_000_000),
    ):
        if max(w, h) <= width and min(w, h) <= height:
            return name, text, limit
    return None


def _bitrate(meta, platform, ctx):
    value = meta.video_bit_rate
    observed = _fmt_bitrate(value)
    estimated = meta.video_bit_rate_source.startswith("estimated")
    if estimated:
        observed += " (estimated average)"
    if platform == "dise":
        limit, expected = (
            GENERAL_PC_BITRATE_LIMIT,
            "10 Mbps target; 20 Mbps recommended maximum",
        )
    else:
        profile = _scala_bitrate_profile(meta.width, meta.height)
        if meta.video_codec in H264_NAMES and profile:
            limit, expected = profile[2], f"{profile[0]}: {profile[1]}"
        elif (
            meta.video_codec in H264_NAMES
            and ctx.scala_engine != "other"
            and _matches_layout(meta, ctx)
        ):
            # Wide canvases have no published Scala bucket. Use the app's common
            # PC ceiling, not a missing-range warning caused by the chosen size.
            limit = GENERAL_PC_BITRATE_LIMIT
            expected = "General PC check: up to 20 Mbps"
        else:
            return _finding(
                REVIEW,
                "Video bitrate",
                observed,
                "Player-specific guidance",
                "No published H.264 range applies to this codec or canvas.",
            )
    if not value or value <= 0:
        return _finding(
            REVIEW,
            "Video bitrate",
            "Not reported",
            expected,
            "Check the export settings.",
        )
    if value > limit:
        return _finding(
            REVIEW,
            "Video bitrate",
            observed,
            expected,
            "May need a more powerful player; playback could stutter or freeze.",
        )
    return _finding(
        PASS,
        "Video bitrate",
        observed,
        expected,
        "Estimated average; bitrate peaks are not measured." if estimated else "",
    )


def _engine_support(meta, ctx, rule, observed):
    if ctx.scala_engine == "win32":
        return _finding(PASS, rule, observed, "Windows 32-bit playback engine")
    if ctx.scala_engine == "win64":
        return _finding(
            FAIL,
            rule,
            observed,
            "A format supported by the selected engine",
            "Listed only for the Windows 32-bit playback engine.",
        )
    return _finding(
        REVIEW,
        rule,
        observed,
        "Confirm Windows 32-bit playback engine",
        "Not listed for every playback engine.",
    )


def _scala_formats(meta, ctx):
    if meta.media_type == "video":
        ext, codec = meta.extension, meta.video_codec
        if ext == ".dcp" or "dcp" in meta.format_name:
            return [
                _finding(
                    FAIL,
                    "Video format",
                    "DCP",
                    "Supported video",
                    "DCP is explicitly unsupported.",
                )
            ]
        findings = []
        if ext in {".avi", ".wmv"}:
            findings.append(_engine_support(meta, ctx, "Container", ext))
        elif ext in {".mp4", ".mpg", ".mpeg", ".m2v"}:
            findings.append(_finding(PASS, "Container", ext, "MP4 or MPEG delivery"))
        elif (
            ext == ".mov" and codec == "prores" and meta.video_profile.lower() == "4444"
        ):
            findings.append(
                _engine_support(meta, ctx, "Container", "MOV / ProRes 4444")
            )
        else:
            findings.append(
                _finding(
                    REVIEW,
                    "Container",
                    ext or meta.format_name,
                    "Confirmed playback format",
                    "Test this container on the selected player.",
                )
            )
        if codec in H264_NAMES | H265_NAMES | MPEG2_NAMES:
            findings.append(
                _finding(PASS, "Video codec", codec.upper(), "H.264, HEVC or MPEG-2")
            )
        elif codec in {"wmv1", "wmv2", "wmv3", "vc1"} or (
            codec == "prores" and meta.video_profile.lower() == "4444"
        ):
            findings.append(_engine_support(meta, ctx, "Video codec", codec.upper()))
        else:
            findings.append(
                _finding(
                    REVIEW,
                    "Video codec",
                    codec.upper() or "Not reported",
                    "Published delivery codec",
                    "Not confirmed by the format table.",
                )
            )
        return findings
    if meta.media_type == "image":
        if meta.extension in {".tiff", ".tif", ".wmf"}:
            return [_engine_support(meta, ctx, "Image format", meta.extension)]
        return [
            _finding(
                (
                    PASS
                    if meta.extension in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
                    else REVIEW
                ),
                "Image format",
                meta.extension,
                "RGB JPEG, PNG, GIF or BMP",
            )
        ]
    if meta.media_type == "audio":
        if meta.extension == ".wma":
            return [_engine_support(meta, ctx, "Audio format", ".wma")]
        return [
            _finding(
                PASS if meta.extension in {".mp3", ".wav", ".aac", ".m4a"} else REVIEW,
                "Audio format",
                meta.extension,
                "MP3, WAV or AAC/M4A",
            )
        ]
    return [
        _finding(
            REVIEW,
            "PDF workflow",
            f'PDF; {meta.pdf_pages or "unknown"} pages',
            "Confirmed workflow or conversion to images",
            "Direct PDF playback is not listed in the format table.",
        )
    ]


def _dise_formats(meta, ctx):
    current = ctx.dise_version == "one"
    if meta.media_type == "video":
        codec = meta.video_codec
        mp4_avc = meta.extension == ".mp4" and codec in H264_NAMES
        webm_vp9 = meta.extension == ".webm" and codec == "vp9"
        expected = "MP4 / H.264 or WebM / VP9" if current else "MP4 / H.264"
        status = PASS if mp4_avc or (current and webm_vp9) else REVIEW
        detail = (
            ""
            if status == PASS
            else "Confirm the software version and player support, or re-encode."
        )
        return [
            _finding(
                status,
                "Video format / codec",
                f'{meta.extension} / {codec.upper() or "unknown"}',
                expected,
                detail,
            )
        ]
    if meta.media_type == "image":
        allowed = {".jpg", ".jpeg", ".png"} | ({".webp"} if current else set())
        return [
            _finding(
                PASS if meta.extension in allowed else REVIEW,
                "Image format",
                meta.extension,
                "JPEG, PNG or WebP" if current else "JPEG or PNG",
                (
                    ""
                    if meta.extension in allowed
                    else "Not confirmed for this software version; check or convert."
                ),
            )
        ]
    if meta.media_type == "audio":
        return [
            _finding(
                REVIEW,
                "Audio-only media",
                meta.audio_codec.upper() or "Unknown",
                "Confirmed audio workflow",
                "Check audio support in the client setup.",
            )
        ]
    if ctx.pdf_workflow == "composer" and ctx.dise_version == "legacy":
        return [
            _finding(
                PASS,
                "PDF workflow",
                f'PDF; {meta.pdf_pages or "unknown"} pages',
                "Composer PDF import",
                "Supported import route; check the resulting pages and timing.",
            )
        ]
    return [
        _finding(
            REVIEW,
            "PDF workflow",
            f'PDF; {meta.pdf_pages or "unknown"} pages',
            "Confirmed PDF import or conversion",
            "Composer can import PDF pages; direct playback on this setup is unconfirmed.",
        )
    ]


def _soc_profile(meta, ctx):
    if meta.video_codec not in H264_NAMES or ctx.dise_player == "pc":
        return None
    profile = (meta.video_profile or "").strip().lower()
    level = meta.video_level
    observed = _fmt_profile_level(meta.video_profile, level)
    expected = "H.264 Baseline/Main up to L4.0"
    accepted_profile = profile in {"baseline", "constrained baseline", "main"}
    accepted_level = level is not None and 0 < level <= 40
    if accepted_profile and accepted_level:
        return _finding(
            PASS,
            "SoC profile",
            observed,
            expected,
            "Within the agreed encoding range.",
        )
    if not profile or level is None or level <= 0:
        detail = "Profile or level is missing or invalid; check the export settings."
    else:
        detail = "Outside the tested range; confirm playback or re-encode."
    return _finding(REVIEW, "SoC profile", observed, expected, detail)


def _resolution(meta, ctx, platform):
    w, h = meta.width, meta.height
    if not w or not h:
        return _finding(
            REVIEW, "Player resolution", "Not reported", "Readable dimensions"
        )
    if (
        meta.media_type == "video"
        and platform == "dise"
        and ctx.dise_player == "samsung"
        and max(w, h) >= 3840
        and min(w, h) >= 2160
    ):
        return _finding(
            FAIL if ctx.dise_version == "one" else REVIEW,
            "Player resolution",
            meta.resolution,
            "Current Samsung integration: no 4K video",
            "Current Dise guidance explicitly excludes Samsung 4K video; check the software route.",
        )
    if _matches_layout(meta, ctx):
        return _finding(
            PASS,
            "Player resolution",
            meta.resolution,
            f"Selected layout: {ctx.canvas_width} x {ctx.canvas_height}",
            "Matches the selected layout.",
        )
    if meta.media_type == "image":
        return _finding(
            PASS if _is_within_4k(w, h) else REVIEW,
            "Player resolution",
            meta.resolution,
            (
                "Up to 3840 x 2160 or 2160 x 3840"
                if platform == "dise"
                else "Common image size: up to 4K"
            ),
            (
                ""
                if _is_within_4k(w, h)
                else "Large canvas; check image limits on the player."
            ),
        )
    if platform == "dise" and ctx.dise_player == "samsung":
        if w > 1920 or h > 1080:
            return _finding(
                REVIEW,
                "Player resolution",
                meta.resolution,
                "Confirmed Samsung decoder dimensions",
                "Portrait or wide video needs a player test; canvas size alone does not confirm playback.",
            )
    if _is_within_1080p(w, h):
        return _finding(
            PASS, "Player resolution", meta.resolution, "Within a common HD size"
        )
    return _finding(
        REVIEW,
        "Player resolution",
        meta.resolution,
        "Confirmed player decoding limits",
        "Confirm the content size and player setup.",
    )


def _media_checks(meta, ctx, platform):
    findings = []
    if meta.media_type in {"video", "image"}:
        findings += [_layout(meta, ctx), _resolution(meta, ctx, platform)]
        if meta.rotation:
            findings.append(
                _finding(
                    REVIEW,
                    "Rotation",
                    f"{meta.rotation} degrees",
                    "Orientation built into the exported pixels",
                    "Some players ignore rotation tags; check the displayed orientation.",
                )
            )
    if meta.media_type == "video":
        findings += [
            _frame_rate_finding(meta.average_frame_rate),
            _bitrate(meta, platform, ctx),
        ]
        if meta.field_order in {"tt", "bb", "tb", "bt", "interlaced"}:
            findings.append(
                _finding(
                    REVIEW,
                    "Scan type",
                    "Interlaced",
                    "Progressive video",
                    "Export a progressive copy.",
                )
            )
        pixel = meta.pixel_format.lower()
        advanced = pixel not in {"yuv420p", "yuvj420p", "nv12", "nv21", ""}
        if (
            advanced
            or (meta.bits_per_raw_sample or 0) > 8
            or "smpte2084" in meta.color_transfer
            or "arib-std-b67" in meta.color_transfer
        ):
            findings.append(
                _finding(
                    REVIEW,
                    "Video colour",
                    pixel or f"{meta.bits_per_raw_sample}-bit",
                    "8-bit 4:2:0 SDR unless approved",
                    "Check support for this colour format; an SDR export may be needed.",
                )
            )
        elif not pixel:
            findings.append(
                _finding(
                    REVIEW,
                    "Video colour",
                    "Not reported",
                    "Known colour format",
                    "Confirm the export settings.",
                )
            )
        sar = meta.sample_aspect_ratio
        if sar and sar not in {"1", "1:1", "1/1", "0:1", "0/1", "N/A"}:
            findings.append(
                _finding(
                    REVIEW,
                    "Pixel shape",
                    sar,
                    "Square pixels",
                    "Check the displayed proportions.",
                )
            )
        if platform == "dise":
            soc = _soc_profile(meta, ctx)
            if soc:
                findings.append(soc)
            present = bool(meta.audio_codec or meta.audio_stream_count)
            findings.append(
                _finding(
                    REVIEW if present else PASS,
                    "Audio track",
                    meta.audio_codec.upper() or ("Present" if present else "None"),
                    "No audio unless required",
                    (
                        "Audio may freeze content on some players; remove it if unused."
                        if present
                        else ""
                    ),
                )
            )
            if ctx.dise_player != "pc" and meta.video_codec == "vp9":
                findings.append(
                    _finding(
                        REVIEW,
                        "SoC codec",
                        "VP9",
                        "Confirmed support on this player model",
                        "Check this model and software version before approving WebM.",
                    )
                )
        if ctx.simultaneous_videos:
            findings.append(
                _finding(
                    REVIEW,
                    "Combined playback",
                    "Multiple videos playing together",
                    "Test the complete composition",
                    "These checks assess one file at a time; combined load needs a player test.",
                )
            )
    if platform == "scala" and (
        meta.media_type == "audio" or meta.audio_codec or meta.audio_stream_count
    ):
        codec = meta.audio_codec
        supported = codec in AAC_NAMES | {"mp3", "mp2"} or codec.startswith("pcm_")
        if codec.startswith("wma"):
            findings.append(_engine_support(meta, ctx, "Audio codec", codec.upper()))
        else:
            findings.append(
                _finding(
                    PASS if supported else REVIEW,
                    "Audio codec",
                    codec.upper() or "Not reported",
                    "AAC, MP3, MPEG audio or PCM",
                    (
                        ""
                        if supported
                        else "Confirm the audio codec or export a standard audio track."
                    ),
                )
            )
    if meta.media_type == "image":
        if meta.image_mode == "CMYK" or meta.pixel_format == "cmyk":
            findings.append(
                _finding(
                    (
                        FAIL
                        if platform == "scala" and meta.extension in {".jpg", ".jpeg"}
                        else REVIEW
                    ),
                    "Image colour",
                    "CMYK",
                    "RGB / RGBA",
                    "Export an RGB copy.",
                )
            )
        elif (
            meta.image_mode
            and meta.image_mode not in {"RGB", "RGBA"}
            and platform == "dise"
        ):
            findings.append(
                _finding(
                    REVIEW,
                    "Image colour",
                    meta.image_mode,
                    "24-bit RGB / 32-bit RGBA",
                    "Check colour conversion on the player.",
                )
            )
        if meta.image_frames > 1:
            status = (
                PASS if platform == "scala" and meta.extension == ".gif" else REVIEW
            )
            findings.append(
                _finding(
                    status,
                    "Animation",
                    f"{meta.image_frames} frames",
                    "Supported animated format",
                    "Only the first frame was decoded; verify animation and timing.",
                )
            )
    if (
        meta.video_stream_count > 1
        or meta.audio_stream_count > 1
        or meta.subtitle_stream_count
    ):
        findings.append(
            _finding(
                REVIEW,
                "Extra tracks",
                f"{meta.video_stream_count} video / {meta.audio_stream_count} audio / {meta.subtitle_stream_count} subtitle",
                "One intended video and audio track",
                "Only the first video/audio streams were checked; confirm which tracks play.",
            )
        )
    if meta.probe_notes:
        findings.append(
            _finding(
                REVIEW,
                "File notes",
                "Additional metadata needs review",
                "No unresolved inspection notes",
                " ".join(meta.probe_notes),
            )
        )
    # An extension is not proof of the encoded format.
    if meta.media_type == "image":
        expected = {
            ".jpg": {"mjpeg"},
            ".jpeg": {"mjpeg"},
            ".png": {"png", "apng"},
            ".webp": {"webp"},
            ".gif": {"gif"},
            ".bmp": {"bmp"},
            ".tif": {"tiff"},
            ".tiff": {"tiff"},
        }.get(meta.extension)
        if expected and meta.video_codec not in expected:
            findings.append(
                _finding(
                    REVIEW,
                    "File extension",
                    f"{meta.extension} contains {meta.video_codec}",
                    "Extension matches the actual image",
                    "Use the correct extension or export a new file.",
                )
            )
    elif meta.media_type == "video":
        fmt = meta.format_name
        expected = {
            ".mp4": ("mp4", "mov"),
            ".webm": ("webm", "matroska"),
            ".avi": ("avi",),
            ".wmv": ("asf",),
        }.get(meta.extension)
        if expected and fmt and not any(f in fmt for f in expected):
            findings.append(
                _finding(
                    REVIEW,
                    "File extension",
                    f"{meta.extension} contains {fmt}",
                    "Extension matches the actual container",
                    "Use the correct extension or export a new file.",
                )
            )
    elif meta.media_type == "audio":
        fmt = meta.format_name
        expected = {
            ".mp3": {"mp3"},
            ".wav": {"wav"},
            ".aac": {"aac"},
            ".m4a": {"mp4", "mov"},
            ".wma": {"asf"},
        }.get(meta.extension)
        if expected and fmt and not expected.intersection(fmt.split(",")):
            findings.append(
                _finding(
                    REVIEW,
                    "File extension",
                    f"{meta.extension} contains {fmt}",
                    "Extension matches the actual container",
                    "Use the correct extension or export a new file.",
                )
            )
    return findings


def _evaluate(meta, ctx, platform):
    title = platform.title()
    if not ctx.includes(platform):
        return PlatformResult(title, [], "Not selected for this check.", selected=False)
    if meta.media_type not in {"video", "image", "audio", "document"}:
        return PlatformResult(
            title,
            [
                _finding(
                    FAIL,
                    "Media type",
                    meta.media_type,
                    "Readable video, image, audio or PDF",
                )
            ],
        )
    findings = (
        _scala_formats(meta, ctx) if platform == "scala" else _dise_formats(meta, ctx)
    )
    findings += _media_checks(meta, ctx, platform)
    if meta.media_type == "video":
        if platform == "scala" and ctx.scala_engine == "other":
            findings.append(
                _finding(
                    REVIEW,
                    "Player details",
                    SCALA_ENGINES[ctx.scala_engine],
                    "Confirmed playback engine",
                    "Confirm the engine before approving this file.",
                )
            )
        elif platform == "dise" and (
            ctx.dise_player in {"unknown", "other"} or ctx.dise_version == "unknown"
        ):
            findings.append(
                _finding(
                    REVIEW,
                    "Player details",
                    f"{DISE_VERSIONS[ctx.dise_version]}; {DISE_PLAYERS[ctx.dise_player]}",
                    "Confirmed software and player",
                    "Confirm the version and player before approving this file.",
                )
            )
    elif platform == "scala" and ctx.scala_engine == "other":
        findings.append(
            _finding(
                REVIEW,
                "Player details",
                SCALA_ENGINES[ctx.scala_engine],
                "Confirmed playback engine",
                "The published format table covers Windows engines; check this player.",
            )
        )
    note = (
        "Engine: " + SCALA_ENGINES[ctx.scala_engine]
        if platform == "scala"
        else DISE_VERSIONS[ctx.dise_version] + "; " + DISE_PLAYERS[ctx.dise_player]
    )
    return PlatformResult(title, findings, note)


def evaluate_scala(meta, context=None):
    return _evaluate(meta, context or PlaybackContext(), "scala")


def evaluate_dise(meta, context=None):
    return _evaluate(meta, context or PlaybackContext(), "dise")


def highest_status(findings: Iterable[Finding]):
    return max((f.status for f in findings), default=REVIEW)
