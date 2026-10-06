# Checks reference

Every rule in [`app/helpers/rules.py`](../app/helpers/rules.py), by the
name shown in reports. Statuses are explained in
[architecture.md](architecture.md#rules-helpersrulespy).

Guideline sources:

- **Dise**: Dise Media Format Guidelines, 15 July 2026; Premium & Lite, 29 April 2025
- **Scala**: Scala Creating Content Guidelines, Content Manager 13.60

"Engine-dependent" means: **PASS** for the Scala Windows 32-bit engine,
**FAIL** for Windows 64-bit, **REVIEW** when the engine is unknown or other.
The app's presets leave the engine as unknown, so in the app these show as
*Check before scheduling*.

## Formats

| Rule | Platform | Pass | Review | Fail |
| --- | --- | --- | --- | --- |
| Video format | Scala | | | DCP |
| Container | Scala | `.mp4`, `.mpg`, `.mpeg`, `.m2v` | Other containers | `.avi`, `.wmv`, MOV/ProRes 4444: engine-dependent |
| Video codec | Scala | H.264, HEVC, MPEG-2 | Other codecs | WMV/VC-1, ProRes 4444: engine-dependent |
| Video format / codec | Dise | MP4/H.264; WebM/VP9 on Dise One | Anything else | |
| Image format | Scala | JPEG, PNG, GIF, BMP | Other (e.g. WebP) | TIFF, WMF: engine-dependent |
| Image format | Dise | JPEG, PNG; WebP on Dise One | Anything else | |
| Audio format | Scala | MP3, WAV, AAC, M4A | | WMA: engine-dependent |
| Audio-only media | Dise | | Always | |
| PDF workflow | Scala | | Always (direct PDF playback isn't listed) | |
| PDF workflow | Dise | Composer import on Premium & Lite (not offered in the app's presets) | Otherwise | |
| Media type | Both | | | No readable video, image, audio or PDF |

## Size and layout (video and images)

| Rule | Pass | Review | Info / Fail |
| --- | --- | --- | --- |
| Content size | Displayed size equals the selected layout | Differs from the layout; or, with no layout, the aspect ratio looks like a 2–4 screen wall (±1.5%); or no dimensions | **Info**: no layout selected and not a wall shape |
| Player resolution | Matches the selected layout; images up to 3840×2160 and video up to 1920×1080 (either orientation) | Larger than these; Dise Samsung video over 1920×1080 | **Fail**: Dise One on Samsung, video 3840×2160 or larger (other Dise versions: Review) |
| Rotation | | A rotation tag (or EXIF orientation) is present | |

Displayed size accounts for rotation, so a 1920×1080 file tagged 90° is
checked as 1080×1920.

## Video

| Rule | Platform | Pass | Review |
| --- | --- | --- | --- |
| Frame rate | Both | ≤ 30 fps | Above 30 fps, or not reported |
| Video bitrate | Dise | ≤ 20 Mbps (10 Mbps target) | Higher, or not reported |
| Video bitrate | Scala | H.264 at ≤ 720p: ≤ 12 Mbps; ≤ 1080p: ≤ 20 Mbps; ≤ 4K: ≤ 40 Mbps. H.264 matching a wider selected layout: ≤ 20 Mbps | Higher; not reported; other codecs or canvases without published guidance |
| Scan type | Both | | Interlaced |
| Video colour | Both | | Not 8-bit 4:2:0, more than 8 bits, HDR (PQ/HLG), or unknown pixel format |
| Pixel shape | Both | | Non-square pixels |
| SoC profile | Dise, non-PC players, H.264 | Baseline, Constrained Baseline or Main, level ≤ 4.0 | Other profiles or levels, or missing |
| SoC codec | Dise, non-PC players | | VP9 |
| Audio track | Dise | No audio | Audio present (can freeze playback on some players) |
| Audio codec | Scala (any media with audio) | AAC, MP3, MP2, PCM | Other codecs; WMA is engine-dependent |
| Combined playback | Both | | *Multiple videos* setting on (not offered in the app's presets) |
| Player details | Scala | | Engine set to *Other* (also applies to non-video media; not offered in the app's presets) |
| Player details | Dise | | Version *Unknown*, or player *Unknown* / *Other* |

When a file reports no video bitrate, it is estimated from the container
bitrate minus audio and labelled *estimated average*. Peaks are not
measured.

## Images

| Rule | Platform | Pass | Review | Fail |
| --- | --- | --- | --- | --- |
| Image colour | Scala | | CMYK non-JPEG | CMYK JPEG |
| Image colour | Dise | | CMYK, or any mode other than RGB/RGBA | |
| Animation | Both | Scala: animated GIF | Any other multi-frame image | |

## Every file

| Rule | Review when |
| --- | --- |
| Extra tracks | More than one video or audio stream, or any subtitles |
| File notes | The reader left notes, e.g. EXIF mirroring or skipped streams |
| File extension | The extension doesn't match the actual format (e.g. a `.png` that is a JPEG, an `.mp4` that is AVI) |

## Player presets

| Preset | Platform | Dise version | Dise player |
| --- | --- | --- | --- |
| PC — Scala + Dise *(default)* | Both | General PC compatibility | External PC |
| PC — Scala | Scala | | |
| Dise One — PC / SoC (Generic) / Samsung / LG | Dise | Dise One | PC / SoC / Samsung Tizen / LG webOS |
| Dise Premium / Lite — PC / SoC (Generic) / Samsung / LG | Dise | Premium & Lite | PC / SoC / Samsung Tizen / LG webOS |

Every preset leaves the Scala engine as *Unknown*, the PDF workflow as
direct upload, and *Multiple videos* off. The rules for other values of
these settings stay in the engine, but don't come up in the app until a
preset offers them.

Layouts: Standard / mixed sizes (no canvas), HD landscape 1920×1080, HD
portrait 1080×1920, 2×1 / 3×1 / 4×1 landscape (3840 / 5760 / 7680 × 1080),
2×1 / 3×1 / 4×1 portrait screens (2160 / 3240 / 4320 × 1920), 4K landscape
3840×2160, 4K portrait 2160×3840, and Custom size.
