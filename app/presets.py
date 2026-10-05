from dataclasses import replace
from helpers.context import PlaybackContext

PLAYERS = {
    "PC — Scala + Dise": PlaybackContext(dise_version="general", dise_player="pc"),
    "PC — Scala": PlaybackContext(platform="scala"),
    "Dise One — PC": PlaybackContext(
        platform="dise", dise_version="one", dise_player="pc"
    ),
    "Dise One — SoC (Generic)": PlaybackContext(
        platform="dise", dise_version="one", dise_player="soc"
    ),
    "Dise One — Samsung": PlaybackContext(
        platform="dise", dise_version="one", dise_player="samsung"
    ),
    "Dise One — LG": PlaybackContext(
        platform="dise", dise_version="one", dise_player="lg"
    ),
    "Dise Premium / Lite — PC": PlaybackContext(
        platform="dise", dise_version="legacy", dise_player="pc"
    ),
    "Dise Premium / Lite — SoC (Generic)": PlaybackContext(
        platform="dise", dise_version="legacy", dise_player="soc"
    ),
    "Dise Premium / Lite — Samsung": PlaybackContext(
        platform="dise", dise_version="legacy", dise_player="samsung"
    ),
    "Dise Premium / Lite — LG": PlaybackContext(
        platform="dise", dise_version="legacy", dise_player="lg"
    ),
}
LAYOUTS = {
    "Standard / mixed sizes": (None, None),
    "HD landscape": (1920, 1080),
    "HD portrait": (1080, 1920),
    "2×1 landscape": (3840, 1080),
    "3×1 landscape": (5760, 1080),
    "4×1 landscape": (7680, 1080),
    "2×1 portrait screens": (2160, 1920),
    "3×1 portrait screens": (3240, 1920),
    "4×1 portrait screens": (4320, 1920),
    "4K landscape": (3840, 2160),
    "4K portrait": (2160, 3840),
    "Custom size…": (None, None),
}
DEFAULT_PLAYER = "PC — Scala + Dise"
DEFAULT_LAYOUT = "Standard / mixed sizes"


def make_context(player, layout, custom_size=None):
    size = custom_size if layout == "Custom size…" else LAYOUTS[layout]
    if size is None:
        raise ValueError("Enter a custom width and height.")
    return replace(PLAYERS[player], canvas_width=size[0], canvas_height=size[1])
